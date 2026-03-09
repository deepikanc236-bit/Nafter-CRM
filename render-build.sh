#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download NLTK data for TextBlob
python -m textblob.download_corpora

python manage.py collectstatic --no-input
python manage.py migrate
