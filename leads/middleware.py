from django.shortcuts import redirect
from django.urls import reverse

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the user is authenticated and not a superuser
        if request.user.is_authenticated and not request.user.is_superuser:
            # Check if we have already redirected this session
            if not request.session.get('admin_to_dashboard_redirected', False):
                if request.path == '/admin/':
                    request.session['admin_to_dashboard_redirected'] = True
                    return redirect('/dashboard/')

        response = self.get_response(request)
        return response
