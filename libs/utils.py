import math
from itertools import zip_longest
from termcolor import colored
import libs.fingerprint as fingerprint


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (
        list(filter(None, values))
        for values in zip_longest(fillvalue=fillvalue, *args)
    )


def return_matches(db, hashes, print_output=True):
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

        if print_output:
            if matches_found > 0:
                msg = "   ** found %d hash matches (step %d/%d)"
                print(colored(msg, "green") % (matches_found, step, steps))
            else:
                msg = "   ** no matches found (step %d/%d)"
                print(colored(msg, "red") % (step, steps))

        step += 1

        for hash, sid, offset in x:
            yield (sid, int.from_bytes(offset, "little") - mapper[hash])


def find_matches(db, samples, Fs=fingerprint.DEFAULT_FS, print_output=True):
    hashes = fingerprint.fingerprint(samples, Fs=Fs, print_output=print_output)
    return return_matches(db, hashes, print_output)


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


def print_match_results(db, matches):
    print("")
    total_matches_found = len(matches)

    if total_matches_found > 0:
        msg = " ** found %d total hash matches"
        print(colored(msg, "green") % total_matches_found)

        song = align_matches(db, matches)

        msg = " => song: %s (id=%d)\n"
        msg += "    offset: %d (%d secs)\n"
        msg += "    confidence: %d"

        print(
            colored(msg, "green")
            % (
                song["SONG_NAME"],
                song["SONG_ID"],
                song["OFFSET"],
                song["OFFSET_SECS"],
                song["CONFIDENCE"],
            )
        )
    else:
        msg = " ** no matches found"
        print(colored(msg, "red"))
