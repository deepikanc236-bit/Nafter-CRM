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
        ('AGENT_ORCH', 'Autonomous Agent Orchestration'),
        ('AI_AUTO', 'AI Workflow Automation'),
        ('DRONE', 'Autonomous Drone Solutions'),
        ('FULL_STACK', 'Full Stack Development'),
        ('DIGITAL_MKT', 'AI Digital Marketing'),
        ('GCC', 'GCC Setup'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__old_status = self.status
        self.__old_assigned_user = self.assigned_user

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # Audit Log
        if is_new:
            # We'll create the record after super().save() to have an ID
            pass
        else:
            if self.__old_status != self.status:
                LeadActivity.objects.create(
                    lead=self,
                    action=f"Status changed from {self.__old_status} to {self.status}"
                )
            if self.__old_assigned_user != self.assigned_user:
                action_text = f"Assigned to {self.assigned_user}" if self.assigned_user else "Unassigned"
                LeadActivity.objects.create(
                    lead=self,
                    action=action_text
                )
        
        # Feature 3: High-Value Notifications (> 10 Lakhs)
        if self.budget_inr_value and self.budget_inr_value > 1000000:
            if "🚨 HIGH VALUE" not in self.first_name:
                self.first_name = f"{self.first_name} 🚨 HIGH VALUE"
            
            # Trigger notifications only for new leads or if budget just became high-value
            if is_new:
                from .views import send_high_value_alerts
                send_high_value_alerts(self)
                
        super().save(*args, **kwargs)
        
        if is_new:
            LeadActivity.objects.create(
                lead=self,
                action="Lead created from contact form"
            )

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Lead Activities"

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
