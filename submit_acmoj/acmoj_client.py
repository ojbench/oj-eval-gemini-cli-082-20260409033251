#!/usr/bin/env python3
import requests
import json
import argparse
import os
from datetime import datetime

class ACMOJClient:
    def __init__(self, access_token: str):
        self.api_base = "https://acm.sjtu.edu.cn/OnlineJudge/api/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ACMOJ-Python-Client/2.2"
        }
        self.submission_log_file = '/workspace/submission_ids.log'

    def _make_request(self, method: str, endpoint: str, data=None, params=None):
        url = f"{self.api_base}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, data=data, timeout=10)
            if response.status_code == 204:
                return {"status": "success"}
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
        except Exception as e:
            print(f"API Request failed: {e}")
            return None

    def submit_code(self, problem_id: int, code: str):
        data = {"language": "cpp", "code": code}
        result = self._make_request("POST", f"/problem/{problem_id}/submit", data=data)
        if result and 'id' in result:
            with open(self.submission_log_file, 'a') as f:
                f.write(json.dumps({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "submission_id": result['id']}) + '\n')
            print(f"✅ Submission ID {result['id']} saved")
        return result

    def get_submission_detail(self, submission_id: int):
        return self._make_request("GET", f"/submission/{submission_id}")

    def abort_submission(self, submission_id: int):
        return self._make_request("POST", f"/submission/{submission_id}/abort")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("ACMOJ_TOKEN"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--problem-id", type=int, required=True)
    submit_parser.add_argument("--git-url", type=str, required=False)
    submit_parser.add_argument("--code-file", type=str, required=False)
    
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--submission-id", type=int, required=True)
    
    abort_parser = subparsers.add_parser("abort")
    abort_parser.add_argument("--submission-id", type=int, required=True)
    
    args = parser.parse_args()
    client = ACMOJClient(args.token)
    
    if args.command == "submit":
        if args.code_file:
            with open(args.code_file, 'r') as f:
                code = f.read()
        else:
            code = args.git_url
        result = client.submit_code(args.problem_id, code)
    elif args.command == "status":
        result = client.get_submission_detail(args.submission_id)
    elif args.command == "abort":
        result = client.abort_submission(args.submission_id)
        
    if result:
        print(json.dumps(result))
    else:
        exit(1)

if __name__ == "__main__":
    main()
