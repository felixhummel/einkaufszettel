MAKEFLAGS += --always-make

qa: ruff ty test

ruff:
	ruff format .
	ruff check --fix .

ty:
	ty check --ignore unresolved-attribute .

test:
	pytest tests/

runserver:
	./manage.py runserver 127.0.0.1:8001

uvicorn:
	uvicorn einkaufszettel.asgi:app --host 127.0.0.1 --port 8001 --reload
