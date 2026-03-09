from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Count
from .models import Lead, Feedback, LeadActivity
from .sentiment import analyze_sentiment
from .nlp_utils import extract_lead_info
from .ml_utils import calculate_conversion_probability
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
import os
import re

def extract_smart_budget(text):
    """
    Extracts budget from text, handling Indian (Lakh/Crore) and International (K/M) suffixes.
    Returns the normalized INR value as an integer.
    """
    if not text:
        return 0
        
    # 1. Clean and Normalize
    text = text.lower().replace(',', '')
    
    # 2. Multiplier Mapping
    multipliers = {
        'lakh': 100_000, 'lakhs': 100_000, 'lac': 100_000, 'lacs': 100_000,
        'cr': 10_000_000, 'crore': 10_000_000, 'crores': 10_000_000,
        'm': 1_000_000, 'million': 1_000_000, 'millions': 1_000_000,
        'k': 1_000
    }
    
    # 3. Currency Rates (if symbols are present, otherwise assume INR)
    rates = {'$': 83, 'usd': 83, 'aed': 22, 'eur': 90, '€': 90, '£': 105, 'inr': 1, '₹': 1}
    
    # 4. Regex Pattern
    # Matches: number (optional decimal) + space (optional) + suffix + word boundary
    # Also optionally matches currency symbols/codes
    pattern = r'(?P<currency>[\$€₹]|usd|aed|eur|gbp|inr)?\s*(?P<number>\d+(?:\.\d+)?)\s*(?P<suffix>lakhs?|lacs?|crores?|cr|millions?|m|k)?\b'
    
    match = re.search(pattern, text)
    if match:
        val = float(match.group('number'))
        suffix = match.group('suffix')
        currency = match.group('currency')
        
        # Apply Multiplier
        if suffix:
            val *= multipliers.get(suffix, 1)
            
        # Apply Currency Conversion
        rate = rates.get(currency, 1) # Default to 1 (assume INR)
        
        return int(val * rate)
        
    return 0

def role_required(view_func):
    """
    Decorator for views that checks if the user belongs to authorized CRM groups.
    """
    def _wrapped_view(request, *args, **kwargs):
        authorized_groups = ['Sales Executives', 'Senior Sales Executives', 'Sales Managers']
        if request.user.is_superuser or request.user.groups.filter(name__in=authorized_groups).exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return login_required(_wrapped_view)

def send_high_value_alerts(lead):
    # Email alert
    subject = f"🚨 HIGH VALUE LEAD: {lead.first_name} {lead.last_name}"
    message = f"Details:\nName: {lead.first_name} {lead.last_name}\nBudget: {lead.budget}\nINR Value: ₹{lead.budget_inr_value}\nService: {lead.interest}\nText: {lead.project_details}"
    send_mail(subject, message, 'alerts@nafterweb.com', ['admin@nafterweb.com'])

    # WhatsApp Alert (Twilio)
    # Note: Requires twilio package and credentials
    try:
        from twilio.rest import Client
        account_sid = os.getenv('TWILIO_SID', 'YOUR_TWILIO_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        
        client.messages.create(
            from_='whatsapp:+14155238886', # Twilio Sandbox Number
            body=f"🚨 *HIGH VALUE LEAD ALERT*\n\n*Name:* {lead.first_name} {lead.last_name}\n*Budget:* {lead.budget}\n*INR Value:* ₹{lead.budget_inr_value}",
            to='whatsapp:+91YOUR_NUMBER'
        )
    except Exception as e:
        print(f"Twilio Error: {e}")

    # Feature 3: Email Alert
    try:
        from django.conf import settings
        manager_email = getattr(settings, 'MANAGEMENT_EMAIL', 'admin@nafterweb.com')
        email_subject = f"🔥 MASSIVE LEAD: {lead.first_name} at {lead.company_name or 'Personal'}"
        email_body = f"""
        URGENT: A high-value lead has been submitted.
        
        Lead Details:
        - Name: {lead.first_name} {lead.last_name}
        - Email: {lead.work_email}
        - Website/Company: {lead.company_name}
        - Budget: ₹{lead.budget_inr_value}
        - Service: {lead.interest}
        - Engagement Score: {lead.engagement_score}
        - Conversion Prob: {lead.conversion_probability}%
        
        Dashboard Link: http://127.0.0.1:8000/admin/leads/lead/{lead.id}/change/
        """
        send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [manager_email])
    except Exception as e:
        print(f"Email Error: {e}")

def home(request):
    return render(request, "leads/index.html")

def about(request):
    return render(request, "leads/about.html")

def services(request):
    return render(request, "leads/services.html")

def portfolio(request):
    return render(request, "leads/portfolio.html")

def contact(request):
    if request.method == "POST":
        details = request.POST.get("details")
        
        # Smart NLP Extraction (Multi-Currency)
        nlp_data = extract_lead_info(details)

        # Feature 2: Returning Lead Detection
        email = request.POST.get("work_email")
        existing_lead = Lead.objects.filter(work_email=email).first()
        is_returning = False
        engagement_score = 0
        
        if existing_lead:
            is_returning = True
            engagement_score = existing_lead.engagement_score + 20
        
        # Sentiment Analysis for Probability
        sentiment_score, sentiment_label = analyze_sentiment(details)

        new_lead = Lead.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            work_email=email,
            company_name=request.POST.get("company_name"),
            country=request.POST.get("country"),
            interest=request.POST.get("interest"),
            
            service=nlp_data.get('service'),
            urgency=nlp_data.get('urgency'),
            budget=nlp_data.get('budget'), 
            budget_inr_value=extract_smart_budget(details), 
            timeline=nlp_data.get('timeline'),
            lead_score=nlp_data.get('lead_score', 0),
            project_details=details,
            priority=nlp_data.get('priority', 'Medium'),
            
            # New Features
            is_returning=is_returning,
            engagement_score=engagement_score
        )
        
        # Feature 3 & 4: Calculate Conversion Probability
        new_lead.conversion_probability = calculate_conversion_probability(new_lead, sentiment_score)
        new_lead.save()

        return redirect("contact")

    return render(request, "leads/contact.html")

def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Avg
    
    # Lead Distribution
    lead_stats = Lead.objects.values('service').annotate(count=Count('id'))
    priority_stats = Lead.objects.values('priority').annotate(count=Count('id'))
    
    # KPI Calculations
    total_leads = Lead.objects.count()
    
    last_24h = timezone.now() - timedelta(days=1)
    hot_leads_count = Lead.objects.filter(created_at__gte=last_24h).count()
    
    total_value = Lead.objects.aggregate(Sum('budget_inr_value'))['budget_inr_value__sum'] or 0
    avg_conversion = Lead.objects.aggregate(Avg('conversion_probability'))['conversion_probability__avg'] or 0
    
    # Pre-process stats for template to avoid |default issues
    lead_stats_list = list(lead_stats)
    for item in lead_stats_list:
        if item['count'] is None: item['count'] = 0
        if not item['service']: item['service'] = 'Other'
        
    priority_stats_list = list(priority_stats)
    for item in priority_stats_list:
        if item['count'] is None: item['count'] = 0

    # Feedback with Sentiment
    feedbacks = Feedback.objects.all().order_by('-created_at')

    context = {
        'lead_stats': lead_stats_list,
        'priority_stats': priority_stats_list,
        'feedbacks': feedbacks,
        'total_leads': total_leads,
        'hot_leads_count': hot_leads_count,
        'total_value': total_value,
        'avg_conversion': round(avg_conversion, 1)
    }
    return render(request, 'leads/dashboard.html', context)


def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        
        score, label = analyze_sentiment(message)
        
        Feedback.objects.create(
            client_name=name,
            message=message,
            sentiment_score=score,
            sentiment_label=label
        )
        return redirect("feedback")
        
    return render(request, "leads/feedback.html")

@role_required
def kanban_board(request):
    leads = Lead.objects.all()
    columns = {
        'New': leads.filter(status='New'),
        'Contacted': leads.filter(status='Contacted'),
        'Negotiation': leads.filter(status='Negotiation'),
        'Closed': leads.filter(status='Closed'),
    }
    context = {'columns': columns}
    return render(request, 'leads/kanban.html', context)

@login_required
@csrf_exempt
def update_lead_status(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('status')
        try:
            lead = Lead.objects.get(id=lead_id)
            lead.status = new_status
            lead.save()
            return JsonResponse({'success': True})
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lead not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@role_required
def feedback_dashboard(request):
    feedbacks = Feedback.objects.all()
    negative = feedbacks.filter(sentiment_score__lt=0).count()
    neutral = feedbacks.filter(sentiment_score=0).count()
    positive = feedbacks.filter(sentiment_score__gt=0).count()
    
    context = {
        'negative': negative,
        'neutral': neutral,
        'positive': positive,
    }
    return render(request, 'leads/feedback_dashboard.html', context)

class LeadListView(ListView):
    model = Lead
    template_name = 'leads/leads_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        queryset = Lead.objects.all().prefetch_related('feedback_set').order_by('-created_at')
        
        # Filtering
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter != 'All Statuses':
            queryset = queryset.filter(status=status_filter)
            
        # Sorting
        sort_by = self.request.GET.get('sort')
        if sort_by == 'Newest First':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'Oldest First':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'Conversion Probability':
            queryset = queryset.order_by('-conversion_probability')
        elif sort_by == 'Score':
            queryset = queryset.order_by('-lead_score')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = [choice[0] for choice in Lead.STATUS_CHOICES]
        context['current_status'] = self.request.GET.get('status', 'All Statuses')
        context['current_sort'] = self.request.GET.get('sort', 'Newest First')
        return context

class LeadDetailView(DetailView):
    model = Lead
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedbacks'] = self.object.feedback_set.all().order_by('-created_at')
        context['activities'] = self.object.activities.all().order_by('-timestamp')
        return context
