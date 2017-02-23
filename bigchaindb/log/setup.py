"""Setup logging."""
import os
import logging
import logging.handlers
from logging.config import dictConfig
from multiprocessing import Process, Queue, Event, current_process


DEFAULT_ROOT_LOG_LEVEL = 'INFO'

# listener config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    # 'formatters': {
    #     'default': {
    #         'class': 'logging.Formatter',
    #         'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
    #     },
    # },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            # 'formatter': 'default',
        },
    },
    #'loggers': {
    #    'bigchaindb.pipelines': {
    #        'handlers': ['console'],
    #    },
    #},
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}


def setup_logging(log_config=None):
    dictConfig(LOGGING)
    log_config = log_config or {}
    root_level = log_config.get('level', DEFAULT_ROOT_LOG_LEVEL)
    log_levels = log_config.get('granular_levels', {})
    log_levels[''] = root_level
    for logger_name, level in log_levels.items():
        logging.getLogger(logger_name).setLevel(level)


def setup_multiprocessing_logging():
    pass


def logger_thread(q, config):
    logging.config.dictConfig(config)
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)



# The listener process configuration shows that the full flexibility of
# logging configuration is available to dispatch events to handlers however
# you want.
# We disable existing loggers to disable the "setup" logger used in the
# parent process. This is needed on POSIX because the logger will
# be there in the child following a fork().
config_listener = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'      # noqa
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'      # noqa
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'mplog.log',
            'mode': 'w',
            'formatter': 'detailed',
        },
        'foofile': {
            'class': 'logging.FileHandler',
            'filename': 'mplog-foo.log',
            'mode': 'w',
            'formatter': 'detailed',
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'mplog-errors.log',
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'foo': {
            'handlers': ['foofile']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file', 'errors']
    },
}


class LogHandler:
    """
    A simple handler for logging events. It runs in the listener process and
    dispatches events to loggers based on the name in the received record,
    which then get dispatched, by the logging system, to the handlers
    configured for those loggers.
    """
    def handle(self, record):
        logger = logging.getLogger(record.name)
        # The process name is transformed just to show that it's the listener
        # doing the logging to files and console
        record.processName = '%s (for %s)' % (current_process().name,
                                              record.processName)
        logger.handle(record)


def listener_process(q, stop_event, config):
    """
    This could be done in the main process, but is just done in a separate
    process for illustrative purposes.

    This initialises logging according to the specified configuration,
    starts the listener and waits for the main process to signal completion
    via the event. The listener is then stopped, and the process exits.
    """
    logging.config.dictConfig(config)
    listener = logging.handlers.QueueListener(q, LogHandler())
    listener.start()
    if os.name == 'posix':
        # On POSIX, the setup logger will have been configured in the
        # parent process, but should have been disabled following the
        # dictConfig call.
        # On Windows, since fork isn't used, the setup logger won't
        # exist in the child, so it would be created and the message
        # would appear - hence the "if posix" clause.
        logger = logging.getLogger('setup')
        logger.critical('Should not appear, because of disabled logger ...')
    stop_event.wait()
    listener.stop()
