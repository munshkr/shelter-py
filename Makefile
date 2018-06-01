.PHONY: test autotest

test:
	poetry run pytest

autotest:
	poetry run nosy -c .nosy.cfg
