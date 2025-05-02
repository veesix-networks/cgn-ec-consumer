import httpx
from typing import Optional

def query_session_mappings(
    x_ip: Optional[str] = None,
    x_port: Optional[int] = None,
    limit: int = 100,
    skip: int = 0,
    hook: str = "example",
    api_key: str = "default-change-me"
):
    ip = x_ip or "10.4.21.133"
    port = x_port or 3001

    url = f"http://{ip}:{port}/v1/session_mappings/"
    params = {
        "limit": limit,
        "skip": skip,
        "hook": hook,
    }
    headers = {
        "accept": "application/json",
        "x-api-key": api_key,
    }

    try:
        response = httpx.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"An error occurred while requesting: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error response: {e.response.status_code} - {e.response.text}")


# Example usage
if __name__ == "__main__":
    result = query_session_mappings(limit=5)
    if result:
        print(result)