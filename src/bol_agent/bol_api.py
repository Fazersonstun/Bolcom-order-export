"""bol.com Retailer API client with retry logic and rate limiting."""

import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)


class BolAPIError(Exception):
    """Base exception for bol.com API errors."""
    pass


class BolAuthError(BolAPIError):
    """Authentication related errors."""
    pass


class BolRateLimitError(BolAPIError):
    """Rate limit exceeded errors."""
    pass


@dataclass
class BolToken:
    """OAuth2 access token with expiration tracking."""
    access_token: str
    expires_at: float


class BolClient:
    """
    Client for interacting with the bol.com Retailer API.

    Features:
    - Automatic OAuth2 token management
    - Retry logic with exponential backoff
    - Rate limiting to prevent API throttling
    - Comprehensive error handling and logging
    """

    def __init__(self, client_id: str, client_secret: str, api_base: str):
        """
        Initialize the bol.com API client.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            api_base: Base URL for the API (e.g., https://api.bol.com/retailer)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base = api_base.rstrip("/")
        self._token: Optional[BolToken] = None

        # Rate limiting
        self._last_request_time = 0.0
        self._min_interval = 0.1  # Minimum 100ms between requests

        logger.info(f"BolClient initialized with API base: {self.api_base}")

    def _rate_limit(self) -> None:
        """Enforce minimum interval between API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    @retry(
        retry=retry_if_exception_type((requests.exceptions.RequestException, BolAuthError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _get_token(self) -> str:
        """
        Obtain or refresh OAuth2 access token.

        Returns:
            Valid access token

        Raises:
            BolAuthError: If authentication fails after retries
        """
        # Return cached token if still valid (with 30s buffer)
        if self._token and time.time() < (self._token.expires_at - 30):
            return self._token.access_token

        logger.debug("Requesting new access token")

        try:
            resp = requests.post(
                "https://login.bol.com/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json()

            access_token = payload["access_token"]
            expires_in = float(payload.get("expires_in", 300))
            self._token = BolToken(
                access_token=access_token,
                expires_at=time.time() + expires_in
            )

            logger.info(f"Access token obtained, expires in {expires_in}s")
            return access_token

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                error_msg = f"Authentication failed: {e.response.status_code} - Check credentials"
                logger.error(error_msg)
                raise BolAuthError(error_msg) from e
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain access token: {e}")
            raise BolAuthError(f"Token request failed: {e}") from e

    def _headers(self) -> Dict[str, str]:
        """
        Generate HTTP headers with authentication.

        Returns:
            Dictionary of HTTP headers
        """
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.retailer.v10+json",
        }

    @retry(
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def list_orders(self, fulfilment_method: str = "FBR") -> Dict[str, Any]:
        """
        Retrieve list of orders from bol.com.

        Args:
            fulfilment_method: Filter by fulfilment method (FBR or FBB)

        Returns:
            Dictionary containing orders list and metadata

        Raises:
            BolAPIError: If API request fails after retries
            BolRateLimitError: If rate limit is exceeded
        """
        self._rate_limit()

        url = f"{self.api_base}/orders"
        params = {"fulfilment-method": fulfilment_method}

        logger.info(f"Fetching orders list (fulfilment_method={fulfilment_method})")

        try:
            resp = requests.get(url, headers=self._headers(), params=params, timeout=30)

            if resp.status_code == 429:
                error_msg = "Rate limit exceeded"
                logger.error(error_msg)
                raise BolRateLimitError(error_msg)

            resp.raise_for_status()
            data = resp.json()

            order_count = len(data.get("orders", []))
            logger.info(f"Successfully fetched {order_count} orders")

            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching orders: {e.response.status_code}")
            raise BolAPIError(f"Failed to fetch orders: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching orders: {e}")
            raise BolAPIError(f"Failed to fetch orders: {e}") from e

    @retry(
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information for a specific order.

        Args:
            order_id: Unique order identifier

        Returns:
            Dictionary containing order details

        Raises:
            BolAPIError: If API request fails after retries
            BolRateLimitError: If rate limit is exceeded
        """
        self._rate_limit()

        url = f"{self.api_base}/orders/{order_id}"

        logger.debug(f"Fetching order details for: {order_id}")

        try:
            resp = requests.get(url, headers=self._headers(), timeout=30)

            if resp.status_code == 429:
                error_msg = f"Rate limit exceeded for order {order_id}"
                logger.error(error_msg)
                raise BolRateLimitError(error_msg)

            resp.raise_for_status()
            data = resp.json()

            logger.debug(f"Successfully fetched order {order_id}")
            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching order {order_id}: {e.response.status_code}")
            raise BolAPIError(f"Failed to fetch order {order_id}: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching order {order_id}: {e}")
            raise BolAPIError(f"Failed to fetch order {order_id}: {e}") from e
