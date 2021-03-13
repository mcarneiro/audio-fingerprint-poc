.PHONY: tests

clean:
	@find . -name \*.pyc -delete

reset:
	@python reset-database.py

stat:
	@python get-database-stat.py

fingerprint-songs: clean
	@python collect-fingerprints-of-songs.py

recognize-file: clean
	@python recognize_from_file.py $(file)
