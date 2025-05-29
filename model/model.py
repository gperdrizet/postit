'''Main module to initialize LLM backend'''

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from torch import bfloat16
from transformers import pipeline

import functions.api_functions as api_funcs

# Make sure log directory exists
Path('logs').mkdir(parents=True, exist_ok=True)

# Get the logger
logger = logging.getLogger(__name__)

logging.basicConfig(
    handlers=[RotatingFileHandler(
        'logs/model.log',
        maxBytes=100000, backupCount=10
    )],
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Start the inference pipeline
pipeline = pipeline(
    'summarization',
    model='facebook/bart-large-cnn',
    device='cuda:0',
    torch_dtype=bfloat16
)

logger.info('Pipeline initialized')

# Initialize Flask app
flask_app = api_funcs.create_flask_celery_app(pipeline)
logger.info('Flask app initialized')


if __name__ == 'model':

    # Start the celery app
    api_funcs.start_celery(flask_app)
    logger.info('Celery app MainProcess thread started')