'''Postit model API.'''

import os
from typing import Callable
from threading import Thread
from flask import Flask, request
from celery import Celery, Task, shared_task
from celery.app import trace
from celery.result import AsyncResult
from celery.utils.log import get_task_logger

# Comment ##############################################################
# Code ########################################################################

# Disable return portion task success message log so that
# user messages don't get logged.
trace.LOG_SUCCESS='''\
Task %(name)s[%(id)s] succeeded in %(runtime)ss\
'''

def start_celery(flask_app: Callable) -> None:
    '''Initializes Celery and starts it in a thread'''

    # Get the Celery app
    celery_app=flask_app.extensions['celery']

    # Put the Celery into a thread
    celery_app_thread=Thread(
        target=celery_app.worker_main,
        args=[['worker','--pool=solo',f'--loglevel=INFO']]
    )

    # Start the Celery app thread
    celery_app_thread.start()


def create_flask_celery_app(pipeline: Callable) -> Flask:

    '''Creates Flask app for use with Celery'''

    # Make the app
    app=Flask(__name__)

    # Make redis url
    redis_url = (f"redis://:{os.environ['REDIS_PASSWORD']}@" +
        f"{os.environ['REDIS_IP']}:{os.environ['REDIS_PORT']}")

    # Set the Celery configuration
    app.config.from_mapping(
        CELERY=dict(
            broker_url=redis_url,
            result_backend=redis_url,
            task_ignore_result=True,
            broker_connection_retry_on_startup=True,
            user='nobody',
            group='nogroup'

        ),
    )

    app.config.from_prefixed_env()

    # Make the celery app
    create_celery_app(app)

    # Get task logger
    logger = get_task_logger(__name__)

    @shared_task(ignore_result=False)
    def summarize_text(input_text: str=None) -> str:
        '''Submits a text string for summarization'''

        logger.info('Submitting text for summarization')
        return pipeline(input_text)


    # Set listener for text strings via POST
    @app.post('/submit_text')
    def submit_text() -> dict:
        '''Submits text for scoring. Returns dict. containing result id.'''

        # Get the suspect text string from the request data
        request_data=request.get_json()
        text_string=request_data['text']

        # Submit the text for summarization
        result=summarize_text.delay(text_string)

        return {'result_id': result.id}


    @app.get('/result/<result_id>')
    def task_result(result_id: str) -> dict:
        '''Gets result by result id. Returns dictionary with task status'''

        # Get the result
        result=AsyncResult(result_id)

        # Return status and result if ready
        return {
            'ready': result.ready(),
            'successful': result.successful(),
            'value': result.result if result.ready() else None,
        }

    return app


def create_celery_app(app: Flask, log_level: str = 'INFO') -> Celery:
    '''Sets up Celery app object'''

    class FlaskTask(Task):
        '''Gives task function an active Flask context'''

        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    # Create Celery app
    celery_app=Celery(app.name, task_cls=FlaskTask)

    # Add configuration from Flask app's Celery config. dict
    celery_app.config_from_object(app.config['CELERY'])

    # Configure logging
    celery_app.log.setup(
        loglevel=log_level,
        logfile='logs/celery.log',
        colorize=None
    )

    # Set as default and add to extensions
    celery_app.set_default()
    app.extensions['celery']=celery_app

    return celery_app