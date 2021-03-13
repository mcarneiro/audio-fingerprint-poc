import math
from itertools import zip_longest

# from termcolor import colored
import libs.fingerprint as fingerprint


def logmsg(msg, color=None, attrs=[], prefix=None):
    maxlen = 40  # Only print up to 40 chars

    if prefix is not None:
        prefix = "[ %s ] " % prefix[:maxlen]
        if len(prefix) < maxlen:
            prefix += "".join([" " for x in range(maxlen - len(prefix))])
        msg = "\n".join([(prefix + x) for x in msg.split("\n")])

    # Return uncolored message for logging purposes
    # return colored(msg, color=color, attrs=attrs)
    return msg


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (
        list(filter(None, values))
        for values in zip_longest(fillvalue=fillvalue, *args)
    )


def return_matches(db, hashes, logger=None, filename=None):
    mapper = {}
    for hash, offset in hashes:
        mapper[hash.upper()] = offset
    values = mapper.keys()

    split_size = 800
    grouped_values = grouper(values, split_size)
    steps = math.ceil(len(values) / split_size)
    step = 1

    for split_values in grouped_values:
        query = """
            SELECT upper(hash), song_fk, offset
            FROM fingerprints
            WHERE upper(hash) IN (%s)
        """
        query = query % ", ".join("?" * len(split_values))

        x = db.executeAll(query, split_values)
        matches_found = len(x)

        if logger:
            if matches_found > 0:
                msg = "   ** found %d hash matches (step %d/%d)"
                logger.debug(
                    logmsg(msg, "green", prefix=filename),
                    matches_found,
                    step,
                    steps,
                )
            else:
                msg = "   ** no matches found (step %d/%d)"
                logger.debug(
                    logmsg(msg, "red", prefix=filename), step, steps,
                )

        step += 1

        for hash, sid, offset in x:
            yield (sid, int.from_bytes(offset, "little") - mapper[hash])


def find_matches(
    db, samples, logger, Fs=fingerprint.DEFAULT_FS, filename=None
):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    return return_matches(db, hashes, logger, filename)


def align_matches(db, matches):
    diff_counter = {}
    largest = 0
    largest_count = 0
    song_id = -1

    for tup in matches:
        sid, diff = tup

        if diff not in diff_counter:
            diff_counter[diff] = {}

        if sid not in diff_counter[diff]:
            diff_counter[diff][sid] = 0

        diff_counter[diff][sid] += 1

        if diff_counter[diff][sid] > largest_count:
            largest = diff
            largest_count = diff_counter[diff][sid]
            song_id = sid

    songM = db.get_song_by_id(song_id)

    nseconds = round(
        float(largest)
        / fingerprint.DEFAULT_FS
        * fingerprint.DEFAULT_WINDOW_SIZE
        * fingerprint.DEFAULT_OVERLAP_RATIO,
        5,
    )

    return {
        "SONG_ID": song_id,
        "SONG_NAME": songM[1],
        "CONFIDENCE": largest_count,
        "OFFSET": int(largest),
        "OFFSET_SECS": nseconds,
    }


def print_match_results(db, matches, logger, filename=None):
    logger.info(logmsg("", "green", prefix=filename))
    total_matches_found = len(matches)

    if total_matches_found > 0:
        msg = " ** found %d total hash matches"
        logger.info(logmsg(msg, "green", prefix=filename), total_matches_found)

        song = align_matches(db, matches)

        msg = " => song: %s (id=%d)\n"
        msg += "    offset: %d (%d secs)\n"
        msg += "    confidence: %d\n"

        logger.info(
            logmsg(msg, "green", prefix=filename),
            song["SONG_NAME"],
            song["SONG_ID"],
            song["OFFSET"],
            song["OFFSET_SECS"],
            song["CONFIDENCE"],
        )
        return song
    else:
        msg = " ** no matches found"
        logger.info(logmsg(msg, "red", prefix=filename))
        return {}
