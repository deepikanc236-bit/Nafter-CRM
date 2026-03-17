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
echo "Checking for superuser environment variables..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Attempting to create superuser: $DJANGO_SUPERUSER_USERNAME"
    python manage.py createsuperuser \
        --no-input \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || echo "Superuser already exists or creation failed (this is usually fine)."
else
    echo "Skipping automated superuser creation: Variables not found."
fi
