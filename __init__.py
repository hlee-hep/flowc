"""
FlowC — Unified Daily Automation System
================================================

Provides:
- DailyFlow: main
- Access to connectors, services, and flows modules
"""

import logging


def _configure_logging():
    """Apply a sensible default logging configuration once."""
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


_configure_logging()
