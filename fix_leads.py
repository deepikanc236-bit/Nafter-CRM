import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from leads.models import Lead
from leads.sentiment import analyze_sentiment
from leads.ml_utils import calculate_conversion_probability

def fix_leads():
    print(">>> [FIX] Recalculating probabilities for all leads...")
    leads = Lead.objects.all()
    count = 0
    for lead in leads:
        score, _ = analyze_sentiment(lead.project_details or "")
        lead.conversion_probability = calculate_conversion_probability(lead, score)
        lead.save()
        count += 1
        print(f"Fixed {lead.first_name} {lead.last_name}: {lead.conversion_probability}%")
    print(f">>> [FIX] Done. {count} leads updated.")

if __name__ == '__main__':
    fix_leads()
