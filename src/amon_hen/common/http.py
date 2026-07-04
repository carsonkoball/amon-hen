import logging
import time

import requests

# Logging setup
logger = logging.getLogger(__name__)

# Shared session for connection pooling
_session = requests.Session()

# Default configuration for all requests
DEFAULT_TIMEOUT = 10
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    # "Referer": "https://google.com"
}

# Retry configuration
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5

# Codes to retry requests on
RETRY_STATUS_CODES = {
    408,  # request timeout
    429,  # rate limited
    500,  # server error
    502,  # bad gateway
    503,  # service unavailable
    504,  # gateway timeout
}


def _request(
    method: str,
    url: str,
    **kwargs: Any,
) -> requests.Response | None:
    """
    Internal HTTP request helper with:
    - Automatic retries on exception errors
    - Automatic retries on HTTP failures
    - Exponential backoff - https://en.wikipedia.org/wiki/Exponential_backoff
    """

    # Apply user-supplied configuration if available
    headers = dict(DEFAULT_HEADERS)
    headers.update(kwargs.get("headers", {}))
    kwargs["headers"] = headers

    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)

    response = None

    # Attempt loop: total attempts = MAX_RETRIES + 1
    for attempt in range(MAX_RETRIES):
        reason = None
        try:
            response = _session.request(method, url, **kwargs)

            # HTTP failure case
            if response.status_code in RETRY_STATUS_CODES:
                reason = f"HTTP {response.status_code}"
            # Success case
            else:
                logger.debug(
                    "%s %s succeeded (status %s)", method, url, response.status_code
                )
                return response
        # Exception failure case
        except requests.RequestException as e:
            response = None
            reason = str(e)

        if attempt == MAX_RETRIES:
            break

        # Exponential backoff - https://en.wikipedia.org/wiki/Exponential_backoff
        sleep_time = BACKOFF_FACTOR * (2**attempt)

        logging.warning(
            "%s %s failed (%s), retrying in %.1fs [%d/%d]",
            method,
            url,
            reason,
            sleep_time,
            attempt + 1,
            MAX_RETRIES,
        )

        time.sleep(sleep_time)

    # All retries used
    logger.error("HTTP %s failed permanently: %s", method, url)
    return response


def http_get(url: str, **kwargs: Any) -> requests.Response | None:
    """
    Convenience wrapper for GET requests.
    """
    return _request("GET", url, **kwargs)


def http_post(url: str, **kwargs: Any) -> requests.Response | None:
    """
    Convenience wrapper for POST requests.
    """
    return _request("POST", url, **kwargs)


def http_head(url: str, **kwargs: Any) -> requests.Response | None:
    """
    Convenience wrapper for HEAD requests.
    """
    return _request("HEAD", url, **kwargs)


def safe_json(response: requests.Response) -> Any:
    """
    Safely parse JSON from a requests response.
    Returns parsed JSON or None if invalid.
    """
    try:
        return response.json()
    except ValueError:
        logger.error("Invalid JSON response from %s", response.url)
        return None
