"""Main entry point for the Momentum Indicator Service.

This script starts the service that consumes stock data messages from a
message queue (RabbitMQ or SQS), applies momentum-based technical
analysis, and sends the results to output.
"""

import os
import sys

# Add 'src/' to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.setup_logger import setup_logger
from app.queue_handler import consume_messages

# Initialize logger
logger = setup_logger(__name__)


def main() -> None:
    """Main function to launch the momentum analysis service.

    This starts the message consumer which waits for new stock data, analyzes it using
    momentum indicators, and outputs the result.

    Args:
    ----



    """
    logger.info("Starting Momentum Indicator Analysis Service...")
    consume_messages()


if __name__ == "__main__":
    main()
