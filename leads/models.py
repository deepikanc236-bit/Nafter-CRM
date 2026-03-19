from django.db import models
from django.conf import settings

class Lead(models.Model):
    FIRST_NAME_MAX_LENGTH = 100
    LAST_NAME_MAX_LENGTH = 100
    COMPANY_MAX_LENGTH = 150
    
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('UAE', 'United Arab Emirates'),
        ('DE', 'Germany'),
        ('UK', 'United Kingdom'),
        ('IN', 'India'),
        ('Other', 'Other'),
    ]
    
    INTEREST_CHOICES = [
        ('AI_STRAT', 'AI Strategy & Consulting'),
        ('GEN_AI', 'Generative AI Solutions'),
        ('AI_ENG', 'AI Engineering & MLOps'),
        ('AGENT_ORCH', 'Autonomous Agents'),
        ('AI_AUTO', 'Workflows & Automation'),
        ('DRONE', 'Autonomous Drone Solutions'),
        ('FULL_STACK', 'Full Stack Development'),
        ('DIGITAL_MKT', 'AI Digital Marketing'),
        ('Other', 'Other'),
    ]

    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    work_email = models.EmailField()
    company_name = models.CharField(max_length=COMPANY_MAX_LENGTH, null=True, blank=True)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, default='IN')
    interest = models.CharField(max_length=100, choices=INTEREST_CHOICES, default='Other')

    service = models.CharField(max_length=50, null=True, blank=True)
    urgency = models.CharField(max_length=50, null=True, blank=True)
    budget = models.CharField(max_length=50, null=True, blank=True) # Storing raw text like "$15k"
    budget_inr_value = models.IntegerField(null=True, blank=True) # Normalized value
    timeline = models.CharField(max_length=100, null=True, blank=True)
    
    # Enterprise & ML Features
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    is_returning = models.BooleanField(default=False)
    engagement_score = models.IntegerField(default=0)
    conversion_probability = models.IntegerField(default=0) # 0-100%
    
    lead_score = models.IntegerField(default=0)

    project_details = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Medium')
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Negotiation', 'Negotiation'),
        ('Closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')

    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        
        if self.budget_inr_value and self.budget_inr_value > 1000000:
            if "🚨 HIGH VALUE" not in self.first_name:
                self.first_name = f"{self.first_name} 🚨 HIGH VALUE"
                
        super().save(*args, **kwargs)
        

    def get_freshness_status(self):
        """Returns hot, warm, or cold based on aging."""
        from django.utils import timezone
        diff = timezone.now() - self.created_at
        if diff.days < 1: return 'hot'
        if diff.days < 2: return 'warm'
        return 'cold'

    @staticmethod
    def get_role_restricted_queryset(user, queryset=None):
        if queryset is None:
            queryset = Lead.objects.all()
        
        group_names = [g.name.lower() for g in user.groups.all()]
        
        # Superusers and Sales Managers can see all leads
        if user.is_superuser or 'sales managers' in group_names:
            return queryset
            
        # Senior Sales Executives: ₹5,00,000 - ₹1,000,000
        if 'senior sales executives' in group_names:
            return queryset.filter(budget_inr_value__gte=500000, budget_inr_value__lte=1000000)
            
        # Sales Executives: < ₹5,00,000
        if 'sales executives' in group_names:
            return queryset.filter(budget_inr_value__lt=500000)
            
        # If no specific role or just a generic user, protect the data
        # Only show what is specifically assigned to them
        return queryset.filter(assigned_user=user)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name or 'Personal'}"

class Feedback(models.Model):
    client_name = models.CharField(max_length=100)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    sentiment_score = models.FloatField()
    sentiment_label = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.client_name} ({self.sentiment_label})"

class LeadActivity(models.Model):
    ACTION_CHOICES = [
        ('status_change', 'Status Changed'),
        ('assignment_change', 'Assignment Changed'),
        ('note_added', 'Note Added'),
        ('system_update', 'System Update'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Changed By")
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES, default='system_update')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Lead Activities"

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
