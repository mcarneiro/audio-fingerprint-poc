import logging
import logging.handlers
import multiprocessing as mp
import os
import sys
from pathlib import Path

from libs.config import get_config
from recognize_from_file import run_recognition

# Logging and multiprocessing code was based on:
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes


def listener_configurer():
    config = get_config()
    root = logging.getLogger()
    f = logging.Formatter(config["log.format"])

    # Set up file handler
    if bool(config["log.file_out"]):
        h = logging.handlers.RotatingFileHandler(
            config["log.file"], "a", int(config["log.max_size"]), 10
        )
        h.setLevel(config["log.level"])
        h.setFormatter(f)
        root.addHandler(h)

    # Set up console handler
    if bool(config["log.console_out"]):
        sh = logging.StreamHandler()
        sh.setLevel(config["log.level"])
        sh.setFormatter(f)
        root.addHandler(sh)


# This is the listener process top-level loop: wait for logging events
# (LogRecords) on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except KeyboardInterrupt:
            break
        except Exception:
            import sys
            import traceback

            print("Whoops! Problem:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue):
    """
    The worker configuration is done at the start of the worker process run.
    Note that on Windows you can't rely on fork semantics, so each process
    will run the logging configuration code when it starts.
    """
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)


def worker_process(filepath, queue, configurer):
    """
    This is the worker process top-level loop, which will run
    audio recognition for a single audio file before terminating.
    """
    configurer(queue)
    logger = logging.getLogger(__name__)

    try:
        run_recognition(filepath, logger)
    except KeyboardInterrupt:
        print(
            'Received keyboard interrupt, '
            'stopping recognition processes...'
        )


def get_mp3_list(dirname):
    return list(
        map(
            lambda val: str(val),
            Path(os.path.abspath(dirname)).glob("**/*.mp3"),
        )
    )


def main():
    """
    Here's where everything gets orchestrated.
    Create the queue, create and start the listener,
    create process workers and start them, wait for them to finish,
    then send a None to the queue to tell the listener to finish.
    """
    args = sys.argv[1:]

    dirname = None
    if len(args) > 0:
        dirname = args[0]
    else:
        print("Must supply a directory name")
        sys.exit(1)

    queue = mp.Queue(-1)
    listener = mp.Process(
        target=listener_process, args=(queue, listener_configurer)
    )
    listener.start()

    workers = []
    for filepath in get_mp3_list(dirname):
        w = mp.Process(
            target=worker_process, args=(filepath, queue, worker_configurer)
        )
        workers.append(w)
        w.start()

    for w in workers:
        try:
            w.join()
        except KeyboardInterrupt:
            pass

    queue.put_nowait(None)
    listener.join()


if __name__ == "__main__":
    main()
