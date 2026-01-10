"""Health check utilities for verifying system status."""

import sys
import logging
from typing import Dict, Any, List

from .config import load_settings
from .bol_api import BolClient, BolAPIError, BolAuthError

logger = logging.getLogger(__name__)


class HealthCheckResult:
    """Result of a health check."""

    def __init__(self, name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}

    def __repr__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"[{status}] {self.name}: {self.message}"


def check_configuration() -> HealthCheckResult:
    """Verify configuration is valid."""
    try:
        settings = load_settings()
        return HealthCheckResult(
            name="Configuration",
            passed=True,
            message="Configuration loaded successfully",
            details={"api_base": settings.bol_api_base}
        )
    except ValueError as e:
        return HealthCheckResult(
            name="Configuration",
            passed=False,
            message=f"Configuration error: {e}"
        )
    except Exception as e:
        return HealthCheckResult(
            name="Configuration",
            passed=False,
            message=f"Unexpected error: {e}"
        )


def check_api_authentication() -> HealthCheckResult:
    """Verify API credentials are valid."""
    try:
        settings = load_settings()
        bol = BolClient(
            client_id=settings.bol_client_id,
            client_secret=settings.bol_client_secret,
            api_base=settings.bol_api_base,
        )

        # Attempt to get a token
        token = bol._get_token()

        return HealthCheckResult(
            name="API Authentication",
            passed=True,
            message="Successfully authenticated with bol.com API",
            details={"token_length": len(token)}
        )
    except BolAuthError as e:
        return HealthCheckResult(
            name="API Authentication",
            passed=False,
            message=f"Authentication failed: {e}"
        )
    except Exception as e:
        return HealthCheckResult(
            name="API Authentication",
            passed=False,
            message=f"Unexpected error: {e}"
        )


def check_api_connectivity() -> HealthCheckResult:
    """Verify API is reachable and responding."""
    try:
        settings = load_settings()
        bol = BolClient(
            client_id=settings.bol_client_id,
            client_secret=settings.bol_client_secret,
            api_base=settings.bol_api_base,
        )

        # Attempt to list orders
        response = bol.list_orders(fulfilment_method="FBR")
        order_count = len(response.get("orders", []))

        return HealthCheckResult(
            name="API Connectivity",
            passed=True,
            message="Successfully connected to API",
            details={"order_count": order_count}
        )
    except BolAPIError as e:
        return HealthCheckResult(
            name="API Connectivity",
            passed=False,
            message=f"API request failed: {e}"
        )
    except Exception as e:
        return HealthCheckResult(
            name="API Connectivity",
            passed=False,
            message=f"Unexpected error: {e}"
        )


def run_health_checks() -> List[HealthCheckResult]:
    """
    Run all health checks.

    Returns:
        List of HealthCheckResult objects
    """
    logger.info("Running health checks...")

    checks = [
        check_configuration(),
        check_api_authentication(),
        check_api_connectivity(),
    ]

    return checks


def main():
    """Main entry point for health check command."""
    from .logging_config import setup_logging

    setup_logging()

    logger.info("=" * 60)
    logger.info("Bol.com Order Export - Health Check")
    logger.info("=" * 60)

    results = run_health_checks()

    print("\nHealth Check Results:")
    print("-" * 60)

    for result in results:
        print(f"\n{result}")
        if result.details:
            for key, value in result.details.items():
                print(f"  {key}: {value}")

    print("\n" + "-" * 60)

    # Exit with error code if any check failed
    if all(r.passed for r in results):
        print("\n✓ All checks passed!")
        logger.info("All health checks passed")
        sys.exit(0)
    else:
        failed_count = sum(1 for r in results if not r.passed)
        print(f"\n✗ {failed_count} check(s) failed!")
        logger.error(f"{failed_count} health checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
