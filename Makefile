MAKEFLAGS += --always-make

qa: ruff ty test

ruff:
	ruff check .

ty:
	ty check .

test:
	pytest --doctest-modules --cov
	python -m doctest README.md

build:
	uv build

clean:
	rm -rf build/ dist/

pre-release: clean qa

upload:
	twine upload --repository pypi-felixhummel dist/*

patch-release: pre-release
	uv version --bump patch
	make build upload

minor-release: pre-release
	uv version --bump minor
	make build upload
