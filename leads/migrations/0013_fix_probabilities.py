from django.db import migrations

def fix_probabilities(apps, schema_editor):
    Lead = apps.get_model('leads', 'Lead')
    # We can't easily import the sentiment analyzer inside a migration without side effects,
    # but we can use a simplified version or try to import it.
    try:
        from leads.sentiment import analyze_sentiment
        from leads.ml_utils import calculate_conversion_probability
    except ImportError:
        # Fallback if imports fail in migration context
        return

    for lead in Lead.objects.all():
        try:
            score, _ = analyze_sentiment(lead.project_details or "")
            lead.conversion_probability = calculate_conversion_probability(lead, score)
            lead.save()
        except:
            continue

class Migration(migrations.Migration):
    dependencies = [
        ('leads', '0012_remove_leadactivity_user_leadactivity_changed_by'),
    ]
    operations = [
        migrations.RunPython(fix_probabilities),
    ]
