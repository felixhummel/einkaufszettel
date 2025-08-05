#!/bin/bash
set -euo pipefail

cat <<EOF
APP_ADMIN_PASSWORD=${APP_ADMIN_PASSWORD:-$(pwgen 12 1)}
COOKIE_DOMAIN=einkaufszettel.0-main.de
CSRF_TRUSTED_ORIGINS=https://einkaufszettel.0-main.de,http://localhost
DB_DATABASE_NAME=einkaufszettel
DB_HOST=localhost
DB_PASSWORD=${DB_PASSWORD:-$(pwgen 12 1)}
DB_PORT=5432
DB_USERNAME=django
DEBUG=true
MEDIA_ROOT=$PWD/media
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$(pwgen 12 1)}
SECRET_KEY=${SECRET_KEY:-$(pwgen 12 1)}
STATIC_ROOT=$PWD/staticfiles
UV_PREVIEW=1
EOF

