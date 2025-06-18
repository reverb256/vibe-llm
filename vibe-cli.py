#!/usr/bin/env python3
import sys
import requests
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: vibe-cli.py '<prompt>'")
        sys.exit(1)
    prompt = sys.argv[1]
    url = "http://localhost:8000/api/generate"
    payload = {"prompt": prompt}
    resp = requests.post(url, json=payload)
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    main()
