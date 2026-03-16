import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from leads.models import Lead
from leads.nlp_utils import extract_lead_info

def update_leads():
    leads = Lead.objects.all()
    updated_count = 0
    print(f"Starting lead data update for {leads.count()} leads...")
    
    for lead in leads:
        if not lead.project_details:
            continue
            
        # Re-extract info using the fixed logic
        nlp_data = extract_lead_info(lead.project_details)
        
        # Update fields
        old_budget = lead.budget_inr_value
        lead.budget_inr_value = nlp_data.get('budget_inr_value', 0)
        lead.budget = nlp_data.get('budget')
        lead.service = nlp_data.get('service')
        lead.lead_score = nlp_data.get('lead_score', 0)
        lead.priority = nlp_data.get('priority', 'Medium')
        
        # The HIGH VALUE tag is handled by lead.save() if the budget is high
        # But we should also ensure we don't duplicate it if it's already there
        # and maybe remove it if the budget is NO LONGER high (unlikely but safe)
        
        lead.save()
        
        if old_budget != lead.budget_inr_value:
            # Safely handle names with emojis for terminal output
            safe_name = lead.first_name.encode('ascii', 'ignore').decode('ascii')
            print(f"Fixed Lead {lead.id} ({safe_name}): {old_budget} -> {lead.budget_inr_value}")
            updated_count += 1
        else:
            print(f"Lead {lead.id} updated.")

    print(f"\nUpdate complete! {updated_count} leads had their budget corrected.")

if __name__ == "__main__":
    update_leads()
