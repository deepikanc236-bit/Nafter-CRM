#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download NLTK data for TextBlob only if not present
if [ ! -d "/opt/render/project/src/.venv/lib/python3.12/site-packages/textblob/en" ]; then
    python -m textblob.download_corpora
fi

python manage.py collectstatic --no-input
python manage.py migrate
python setup_groups.py

# Create superuser automatically if environment variables are set
python create_admin.py
