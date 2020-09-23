#!/usr/bin/python3
import os
import sys
import logging

from libs.config import get_config
from libs.reader_file import FileReader
from libs.db_sqlite import SqliteDatabase
from libs.utils import logmsg, find_matches, print_match_results


def run_recognition(filename, logger):
    db = SqliteDatabase()

    abs_filename = os.path.abspath(filename)
    filename = abs_filename.rsplit(os.sep)[-1]

    r = FileReader(abs_filename)
    data = r.parse_audio()

    Fs = data["Fs"]
    channel_amount = len(data["channels"])
    matches = []

    for channeln, channel in enumerate(data["channels"]):
        msg = "   fingerprinting channel %d/%d"
        logger.info(
            logmsg(msg, attrs=["dark"], prefix=filename),
            channeln + 1,
            channel_amount,
        )

        matches.extend(find_matches(db, channel, logger, Fs, filename))

        msg = "   finished channel %d/%d, got %d hashes"
        logger.info(
            logmsg(msg, attrs=["dark"], prefix=filename),
            channeln + 1,
            channel_amount,
            len(matches),
        )

    print_match_results(db, matches, logger, filename)


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) > 0:
        filename = args[0]
    else:
        print("Must supply a file name to match")
        sys.exit(1)

    config = get_config()

    # Set up logging
    handlers = []
    if bool(config["log.console_out"]):
        handlers.append(logging.StreamHandler())
    if bool(config["log.file_out"]):
        handlers.append(logging.FileHandler(f"{filename}_rec.log"))

    logger = logging.basicConfig(
        handlers=handlers,
        format=config["log.format"],
        level=config["log.level"],
    )

    # Run recognition
    run_recognition(filename, logger)
