# Einkaufszettel
Manage your shopping list with a REST API!


## Getting Started
```bash
./env/dev/generate_env_file.sh > .env
docker-compose up -d --build --remove-orphans
```


# Development
```bash
./env/dev/activate
docker-compose up -d --build --remove-orphans

mise install
uv sync
make
```
