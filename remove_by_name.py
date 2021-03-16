#!/usr/bin/python3
import sys
from libs.db_sqlite import SqliteDatabase

if __name__ == "__main__":
  args = sys.argv[1:]
  db = SqliteDatabase()

  if len(args) > 0:
    filename = args[0]
  else:
    print("Must supply a file name to match")
    sys.exit(1)

  #
  # songs table
  queryResult = db.executeOne("SELECT id FROM songs WHERE name = '%s'" % args[0])

  if queryResult is None:
    print("%s was not found on 'name' column of songs database" % args[0])
    sys.exit(1)

  id = queryResult[0]

  db.query("DELETE FROM fingerprints WHERE song_fk = %d" % id)
  db.query("DELETE FROM songs WHERE id = %d" % id)
  print("%s was deleted from the database" % args[0])

  print("done")
