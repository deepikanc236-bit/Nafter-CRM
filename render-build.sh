#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download NLTK data for TextBlob only if not present
if [ ! -d "/opt/render/project/src/.venv/lib/python3.12/site-packages/textblob/en" ]; then
    python -m textblob.download_corpora
fi

echo ">>> Running Database Migrations..."
python manage.py migrate
echo ">>> Migrations Complete."
