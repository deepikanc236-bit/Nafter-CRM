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

class ErrorLoggingMiddleware:
    """
    Safely logs unhandled exceptions to the console so they show up in Render logs
    without modifying Django's complex global LOGGING config.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        import traceback
        import sys
        print(f"\\n{'='*50}\\n500 ERROR CAUGHT BY MIDDLEWARE:\\n{exception}\\n{'='*50}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(f"{'='*50}\\n", file=sys.stderr)
        return None
