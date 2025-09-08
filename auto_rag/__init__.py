import logging

# Set up a default logger for the entire 'auto_rag' package.
# This prevents the "No handlers found" error if the library is used
# in an application that hasn't configured logging.

# Get the top-level logger for the package
logger = logging.getLogger(__name__)

# Add a NullHandler to it. This handler does nothing, but it satisfies
# the need for a handler to be present. The consuming application
# is still responsible for configuring the actual logging behavior.
if not logger.handlers:
    logger.addHandler(logging.NullHandler())
