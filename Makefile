MAKEFLAGS += --always-make

qa: ruff ty test

ruff:
	ruff check .

ty:
	ty check --ignore unresolved-attribute .

test:
	pytest --doctest-modules
