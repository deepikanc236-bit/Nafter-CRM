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
    Consolidated budget extraction using the NLP utility.
    """
    if not text:
        return 0
    
    from .nlp_utils import extract_lead_info
    data = extract_lead_info(text)
    return data.get('budget_inr_value', 0)

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

# Alert functions moved to alerts.py to avoid blocking UI and circular imports

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
        try:
            details = request.POST.get("details", "")
            first_name = request.POST.get("first_name", "Anonymous")
            last_name = request.POST.get("last_name", "")
            email = request.POST.get("work_email", "")
            company_name = request.POST.get("company_name", "")
            country = request.POST.get("country", "IN")
            interest = request.POST.get("interest", "Other")

            # 1. NLP Extraction (Resilient)
            try:
                nlp_data = extract_lead_info(details)
                budget_inr = extract_smart_budget(details)
            except Exception as e:
                print(f">>> [NLP] Error: {e}")
                nlp_data = {}
                budget_inr = 0

            # 2. Returning Lead Detection
            existing_lead = Lead.objects.filter(work_email=email).first()
            is_returning = False
            engagement_score = 0
            if existing_lead:
                is_returning = True
                engagement_score = existing_lead.engagement_score + 25
                LeadActivity.objects.create(
                    lead=existing_lead,
                    action_type='system_update',
                    action=f"Returning lead detected: {email}. Engagement score increased."
                )

            # 3. Sentiment & Scoring
            sentiment_score, _ = analyze_sentiment(details)
            base_lead_score = nlp_data.get('lead_score', 0)
            if is_returning:
                base_lead_score = min(base_lead_score + 20, 100)

            # 4. Create Lead
            new_lead = Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                work_email=email,
                company_name=company_name,
                country=country,
                interest=interest,
                project_details=details,
                budget_inr_value=budget_inr,
                lead_score=base_lead_score,
                is_returning=is_returning,
                engagement_score=engagement_score,
                status='New'
            )

            # 5. Probability (Calculated separately to avoid blocking create)
            try:
                new_lead.conversion_probability = calculate_conversion_probability(new_lead, sentiment_score)
                new_lead.save()
            except Exception as e:
                print(f">>> [PROBABILITY] Error: {e}")

            return render(request, "leads/contact.html", {"success": True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return render(request, "leads/contact.html", {"error": f"Intelligence Mode Error: {str(e)}"})

    return render(request, "leads/contact.html")

def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Avg
    
    # RBAC Filtering
    base_qs = Lead.get_role_restricted_queryset(request.user)
    
    # Lead Distribution
    lead_stats = base_qs.values('service').annotate(count=Count('id'))
    priority_stats = base_qs.values('priority').annotate(count=Count('id'))
    
    # KPI Calculations
    total_leads = base_qs.count()
    
    last_24h = timezone.now() - timedelta(days=1)
    hot_leads_count = base_qs.filter(created_at__gte=last_24h).count()
    
    total_value = base_qs.aggregate(Sum('budget_inr_value'))['budget_inr_value__sum'] or 0
    avg_conversion = base_qs.aggregate(Avg('conversion_probability'))['conversion_probability__avg'] or 0
    
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
    

@role_required
def lead_ranking(request):
    """View to list leads ranked by their lead score."""
    leads = Lead.get_role_restricted_queryset(request.user).order_by('-lead_score')
    return render(request, 'leads/lead_ranking.html', {'leads': leads})


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
    leads = Lead.get_role_restricted_queryset(request.user)
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
            old_status = lead.status
            lead.status = new_status
            lead.save()
            
            # Record the manual status change with actor
            LeadActivity.objects.create(
                lead=lead,
                changed_by=request.user,
                action_type='status_change',
                action=f"Status changed from {old_status} to {new_status}"
            )
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
        queryset = Lead.get_role_restricted_queryset(self.request.user)
        queryset = queryset.prefetch_related('feedback_set').order_by('-created_at')
        
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

    def get_queryset(self):
        return Lead.get_role_restricted_queryset(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedbacks'] = self.object.feedback_set.all().order_by('-created_at')
        context['activities'] = self.object.activities.all().order_by('-timestamp')
        
        # Add assignable users if the current user is a Sales Manager
        group_names = [g.name.lower() for g in self.request.user.groups.all()]
        if 'sales managers' in group_names:
            from django.contrib.auth.models import User
            context['assignable_users'] = User.objects.filter(
                groups__name__in=['Sales Executives', 'Senior Sales Executives']
            ).distinct()
            context['is_manager'] = True
        return context

@login_required
@csrf_exempt
def assign_lead(request, lead_id):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_names = [g.name.lower() for g in request.user.groups.all()]
        
        # Only Managers can assign
        if 'sales managers' not in group_names:
            return JsonResponse({'success': False, 'message': 'Permission denied'})
            
        try:
            lead = Lead.objects.get(id=lead_id)
            from django.contrib.auth.models import User
            new_assignee = User.objects.get(id=user_id)
            
            old_assignee_name = lead.assigned_user.username if lead.assigned_user else "None"
            lead.assigned_user = new_assignee
            lead.save()
            
            # Record the manual assignment
            LeadActivity.objects.create(
                lead=lead,
                changed_by=request.user,
                action_type='assignment_change',
                action=f"Manual Assignment: Transferred from {old_assignee_name} to {new_assignee.username}"
            )
            
            return JsonResponse({'success': True})
        except (Lead.DoesNotExist, User.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Lead or User not found'})
            
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@role_required
def export_leads_csv(request):
    """
    Exports all leads to a CSV file.
    """
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Work Email', 'Company Name', 
        'Country', 'Interest', 'Status', 'Budget (INR)', 'Lead Score', 
        'Conversion Prob (%)', 'Priority', 'Created At'
    ])
    
    leads = Lead.get_role_restricted_queryset(request.user)
    for lead in leads:
        writer.writerow([
            lead.id, lead.first_name, lead.last_name, lead.work_email, lead.company_name,
            lead.country, lead.interest, lead.status,
            lead.budget_inr_value, lead.lead_score, lead.conversion_probability,
            lead.priority, lead.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
        
    return response

