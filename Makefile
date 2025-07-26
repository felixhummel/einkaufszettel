MAKEFLAGS += --always-make

default: ruff ty test

ruff:
	ruff check .

ty:
	ty .

test:
	pytest --doctest-modules
