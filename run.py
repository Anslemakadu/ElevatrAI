from app import create_app
from flask import Flask, request
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

if __name__ == "__main__":
    app.run(port=1234, debug=True)

# This script initializes the Flask application and runs it on port 1234 with debug mode enabled.



