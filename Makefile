MAKEFLAGS += --always-make

default: ruff ty test

ruff:
	ruff check .

ty:
	ty check .

test:
	pytest --doctest-modules --cov
