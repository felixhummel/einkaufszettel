MAKEFLAGS += --always-make

qa: ruff ty test

ruff:
	ruff check .

ty:
	ty check --ignore unresolved-attribute .

test:
	pytest tests/

uvicorn:
	uvicorn einkaufszettel.asgi:app --host 127.0.0.1 --port 8001 --reload
