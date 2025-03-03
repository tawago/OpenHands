import os
import requests
import json
from enum import Enum

class Platform(Enum):
    INVALID = 0
    GITHUB = 1
    GITLAB = 2

def identify_token(token: str, repo: str = None) -> Platform:
    """
    Identifies whether a token belongs to GitHub or GitLab.
    """
    print("\n=== Testing GitHub Token ===")
    
    # Try GitHub Actions token format (Bearer) with repo endpoint if repo is provided
    if repo:
        github_repo_url = f'https://api.github.com/repos/{repo}'
        github_bearer_headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
        }

        try:
            print(f"\nTesting Bearer token with repo endpoint: {github_repo_url}")
            github_repo_response = requests.get(
                github_repo_url, headers=github_bearer_headers, timeout=5
            )
            print(f"Status code: {github_repo_response.status_code}")
            print(f"Response headers: {json.dumps(dict(github_repo_response.headers), indent=2)}")
            print(f"Response preview: {github_repo_response.text[:200]}...")
            
            if github_repo_response.status_code == 200:
                print("✅ Bearer token authentication successful")
                return Platform.GITHUB
            else:
                print("❌ Bearer token authentication failed")
        except requests.RequestException as e:
            print(f'Error connecting to GitHub API (repo check): {e}')

    # Try GitHub PAT format (token)
    github_url = 'https://api.github.com/user'
    github_headers = {'Authorization': f'token {token}'}

    try:
        print(f"\nTesting token with user endpoint: {github_url}")
        github_response = requests.get(github_url, headers=github_headers, timeout=5)
        print(f"Status code: {github_response.status_code}")
        print(f"Response headers: {json.dumps(dict(github_response.headers), indent=2)}")
        print(f"Response preview: {github_response.text[:200]}...")
        
        if github_response.status_code == 200:
            print("✅ Token authentication successful")
            return Platform.GITHUB
        else:
            print("❌ Token authentication failed")
    except requests.RequestException as e:
        print(f'Error connecting to GitHub API: {e}')

    # Try GitLab token
    gitlab_url = 'https://gitlab.com/api/v4/user'
    gitlab_headers = {'Authorization': f'Bearer {token}'}

    try:
        print(f"\nTesting token with GitLab endpoint: {gitlab_url}")
        gitlab_response = requests.get(gitlab_url, headers=gitlab_headers, timeout=5)
        print(f"Status code: {gitlab_response.status_code}")
        
        if gitlab_response.status_code == 200:
            print("✅ GitLab token authentication successful")
            return Platform.GITLAB
        else:
            print("❌ GitLab token authentication failed")
    except requests.RequestException as e:
        print(f'Error connecting to GitLab API: {e}')

    return Platform.INVALID

def test_repo_endpoints(token: str, repo: str):
    """
    Test various GitHub API endpoints with the token
    """
    print("\n=== Testing GitHub API Endpoints ===")
    
    endpoints = [
        (f"https://api.github.com/repos/{repo}", "Repository info"),
        (f"https://api.github.com/repos/{repo}/contents", "Repository contents"),
        (f"https://api.github.com/repos/{repo}/issues", "Repository issues"),
        ("https://api.github.com/user", "User info"),
        ("https://api.github.com/rate_limit", "Rate limit")
    ]
    
    for url, description in endpoints:
        print(f"\nTesting {description}: {url}")
        
        # Test with token format
        token_headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github+json'
        }
        
        try:
            token_response = requests.get(url, headers=token_headers, timeout=5)
            print(f"Token format - Status code: {token_response.status_code}")
            if token_response.status_code == 200:
                print("✅ Token format successful")
            else:
                print("❌ Token format failed")
                print(f"Response: {token_response.text[:200]}...")
        except requests.RequestException as e:
            print(f'Error with token format: {e}')
        
        # Test with bearer format
        bearer_headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        }
        
        try:
            bearer_response = requests.get(url, headers=bearer_headers, timeout=5)
            print(f"Bearer format - Status code: {bearer_response.status_code}")
            if bearer_response.status_code == 200:
                print("✅ Bearer format successful")
            else:
                print("❌ Bearer format failed")
                print(f"Response: {bearer_response.text[:200]}...")
        except requests.RequestException as e:
            print(f'Error with bearer format: {e}')

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        exit(1)
    
    repo = os.environ.get("GITHUB_REPOSITORY", "tawago/OpenHands")
    print(f"Testing token for repository: {repo}")
    
    result = identify_token(token, repo)
    print(f"\nidentify_token result: {result}")
    
    if result == Platform.GITHUB:
        print("✅ Token identified as GitHub token")
    else:
        print("❌ Token not identified as GitHub token")
    
    test_repo_endpoints(token, repo)