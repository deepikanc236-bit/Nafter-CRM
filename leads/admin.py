from django.contrib import admin
from django.core.mail import send_mail
from django.utils.html import format_html
from django.utils import timezone
from .models import Lead, Feedback, LeadActivity

class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    readonly_fields = ('action', 'user', 'timestamp')
    can_delete = False

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name')
    list_editable = ("status",) # Base editable fields
    
    def get_list_editable(self, request):
        """
        Feature 2: Dynamic list_editable based on roles.
        Managers can edit assignment from the list view.
        """
        if request.user.is_superuser or request.user.groups.filter(name='Sales Managers').exists():
            return ("status", "assigned_user")
        return ("status",)

    def get_readonly_fields(self, request, obj=None):
        """
        Feature 2: Dynamic readonly_fields based on roles.
        Executives cannot assign leads.
        """
        readonly = ["created_at", "budget_inr_value", "conversion_probability"] # Base readonly
        if not (request.user.is_superuser or request.user.groups.filter(name='Sales Managers').exists()):
            readonly.append("assigned_user")
        return readonly

    def save_model(self, request, obj, form, change):
        """
        Feature 1: User-Attributed Audit Logging.
        Captures the exact user who created or changed status/assignment.
        """
        if change: # If this is an update
            old_obj = Lead.objects.get(pk=obj.pk)
            # Track Status Change
            if old_obj.status != obj.status:
                LeadActivity.objects.create(
                    lead=obj,
                    user=request.user,
                    action=f"Status changed to {obj.status} (via Admin)"
                )
            # Track Assignment Change
            if old_obj.assigned_user != obj.assigned_user:
                new_user = obj.assigned_user.username if obj.assigned_user else "Unassigned"
                LeadActivity.objects.create(
                    lead=obj,
                    user=request.user,
                    action=f"Lead assigned to {new_user} (via Admin)"
                )
        else:
            # First Save (Creation via Admin)
            # Note: The signal in signals.py also logs creation, but without user.
            # We'll log it here with user. Our signal should ideally skip if user is already set or use a flag.
            pass
        
        super().save_model(request, obj, form, change)
        
        if not change:
            # Now that it has an ID
            LeadActivity.objects.create(
                lead=obj,
                user=request.user,
                action="Lead Created (via Admin)"
            )

    inlines = [LeadActivityInline]

    def get_queryset(self, request):
        # Feature 1: Role-Based Access Control (RBAC)
        qs = super().get_queryset(request)
        
        # Superusers and Sales Managers can see all leads
        if request.user.is_superuser or request.user.groups.filter(name='Sales Managers').exists():
            return qs
            
        # Senior Sales Executives: ₹5,00,000 - ₹10,00,000
        if request.user.groups.filter(name='Senior Sales Executives').exists():
            return qs.filter(budget_inr_value__gte=500000, budget_inr_value__lte=1000000)
            
        # Sales Executives: < ₹5,00,000
        if request.user.groups.filter(name='Sales Executives').exists():
            return qs.filter(budget_inr_value__lt=500000)
            
        # If no role, return empty queryset for safety (or handle as needed)
        return qs.none()

    @admin.display(description="Lead Aging")
    def lead_aging_badge(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.total_seconds() < 86400: # 24h
            return format_html('<span style="color: #28a745; font-weight: bold;">{}</span>', "🔥 Hot")
        elif diff.total_seconds() < 172800: # 48h
            return format_html('<span style="color: #fd7e14; font-weight: bold;">{}</span>', "⚠️ Warm")
        else:
            return format_html('<span style="color: #dc3545; font-weight: bold;">{}</span>', "❄️ Cold")

    list_filter = ("service", "priority", "status", "created_at", "country")
    search_fields = ("first_name", "last_name", "work_email", "project_details", "company_name")
    actions = ['mark_as_done_and_email', 'export_to_csv']

    @admin.action(description="Export Selected Leads to CSV")
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Company', 'Country', 'Budget (Text)', 'Budget (INR)', 'Status'])
        
        for lead in queryset:
            writer.writerow([lead.first_name, lead.last_name, lead.work_email, lead.company_name, lead.country, lead.budget, lead.budget_inr_value, lead.status])
            
        return response

    @admin.action(description="Mark selected as Done & Send Feedback Email")
    def mark_as_done_and_email(self, request, queryset):
        for lead in queryset:
            lead.status = 'Closed' # Matching new status choices
            lead.save()
            
            # Send Email
            subject = "Project Completed! We'd love your feedback"
            message = f"""
Hi {lead.first_name},

We're excited to let you know that your project has been marked as completed!

We'd love to hear about your experience with Nafter Web Technologies. Please take a moment to share your feedback here:
http://127.0.0.1:8000/feedback/

Thank you for choosing us!

Best regards,
The Nafter Web Team
            """
            send_mail(
                subject,
                message,
                'support@nafterweb.com',
                [lead.work_email],
                fail_silently=False,
            )
        self.message_user(request, f"Email sent to {queryset.count()} customers.")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("client_name", "sentiment_label", "sentiment_score", "created_at")
    list_filter = ("sentiment_label", "created_at")
    search_fields = ("client_name", "message")
