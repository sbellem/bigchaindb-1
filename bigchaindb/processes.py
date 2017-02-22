import logging
import logging.handlers
import multiprocessing as mp
from random import choice, random
import time

import bigchaindb
from bigchaindb.pipelines import vote, block, election, stale
from bigchaindb.web import server


logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. BigchainDB Server is ready and waiting.       *
*   You can send HTTP requests via the HTTP API documented in the          *
*   BigchainDB Server docs at:                                             *
*    https://bigchaindb.com/http-api                                       *
*                                                                          *
*   Listening to client connections on: {:<15}                             *
*                                                                          *
****************************************************************************
"""


# Because you'll want to define the logging configurations for listener and
# workers, the
# listener and worker process functions take a configurer parameter which is a
# callable
# for configuring logging for that process. These functions are also passed the
# queue, which they use for communication.
#
# In practice, you can configure the listener however you want, but note that
# in this
# simple example, the listener does not apply level or filter logic to received
# records.
# In practice, you would probably want to do this logic in the worker
# processes, to avoid
# sending events which would be filtered out between processes.
#
# The size of the rotated files is made small so you can see the results
# easily.
def listener_configurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('mptest.log', 'a', 300, 10)
    f = logging.Formatter(
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)


# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()

            # We send this as a sentinel to tell the listener to quit.
            if record is None:
                break

            logger = logging.getLogger(record.name)

            # No level or filter logic applied - just do it!
            logger.handle(record)
        except Exception:
            import sys, traceback   # noqa
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

# Arrays used for random selections in this demo

LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING,
          logging.ERROR, logging.CRITICAL]

LOGGERS = ['a.b.c', 'd.e.f']

MESSAGES = [
    'Random message #1',
    'Random message #2',
    'Random message #3',
]


# The worker configuration is done at the start of the worker process run.
# Note that on Windows you can't rely on fork semantics, so each process
# will run the logging configuration code when it starts.
def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)


# This is the worker process top-level loop, which just logs ten events with
# random intervening delays before terminating.
# The print messages are just so you know it's doing something!
def worker_process(queue, configurer):
    configurer(queue)
    name = mp.current_process().name
    print('Worker started: %s' % name)
    for i in range(10):
        time.sleep(random())
        logger = logging.getLogger(choice(LOGGERS))
        level = choice(LEVELS)
        message = choice(MESSAGES)
        logger.log(level, message)
    print('Worker finished: %s' % name)


# Here's where the demo gets orchestrated. Create the queue, create and start
# the listener, create ten workers and start them, wait for them to finish,
# then send a None to the queue to tell the listener to finish.

def start():
    logging_queue = mp.Queue(-1)
    listener = mp.Process(
        target=listener_process,
        args=(logging_queue, listener_configurer)
    )

    listener.start()

    #workers = []

    #for i in range(10):
    #    worker = mp.Process(
    #        target=worker_process,
    #        args=(logging_queue, worker_configurer)
    #    )
    #    workers.append(worker)
    #    worker.start()

    #for w in workers:
    #    w.join()


    ###########################################################################
    ###########################################################################
    ###########################################################################
    ###########################################################################
    logger.info('Initializing BigchainDB...')

    # start the processes
    logger.info('Starting block')
    block.start()

    #logger.info('Starting voter')
    #vote.start()

    #logger.info('Starting stale transaction monitor')
    #stale.start()

    #logger.info('Starting election')
    #election.start()

    ## start the web api
    app_server = server.create_server(bigchaindb.config['server'])
    p_webapi = mp.Process(
        name='webapi',
        target=app_server.run,
        kwargs={'logging_queue': logging_queue},
    )
    p_webapi.start()

    # TODO Why is this needed to log to file?
    #p_webapi.join()

    ## start message
    logger.info(BANNER.format(bigchaindb.config['server']['bind']))
    logging_queue.put_nowait(None)
    listener.join()
