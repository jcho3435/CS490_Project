import requests

def get_status(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    endpoint = 'https://api.openai.com/v1/engines/gpt-3.5-turbo-0125'
    response = None
    try:
        status = requests.get(endpoint, headers=headers)
        status.raise_for_status()

        response = {"code": status.status_code, "reason": status.reason}
    except requests.HTTPError as e:
        # Handle HTTP errors (e.g., 4xx, 5xx status codes)
        response = genResFromError(e)
    except requests.ConnectionError as e:
        # Handle connection errors (e.g., network issues)
        response = genResFromError(e)
    except requests.Timeout as e:
        # Handle request timeout
        response = genResFromError(e)
    except requests.TooManyRedirects as e:
        # Handle too many redirects
        response = genResFromError(e)
    except requests.RequestException as e:
        # Handle other request exceptions
        response = genResFromError(e)
    except Exception as e:
        response = {"code": 500, "reason": str(e)}
    
    return response

def genResFromError(e: requests.HTTPError | requests.ConnectionError | requests.Timeout | requests.TooManyRedirects | requests.RequestException) -> dict:
    return {"code": e.response.status_code, "reason": e.response.reason}