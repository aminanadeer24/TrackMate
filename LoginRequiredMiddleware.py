from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be logged in to access certain pages.
    Allows access if any one of the session keys for valid users is present.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('loginindex'),
            reverse('shopregistration'),
            reverse('userregistration'),
            reverse('supplierregistration'),
            reverse('deliveryregistration'),
             reverse('index'),

            # Add other exempt URLs as needed
        ]
        self.session_keys = [
            'admin_id',
            'shop_id',
            'user_id',
            'supplier_id',
            'delivery_id'
        ]

    def __call__(self, request):
        # Skip check for exempt URLs
        if request.path not in self.exempt_urls:
            # Check if any of the expected session keys are present
            if not any(request.session.get(key) for key in self.session_keys):
                return redirect('loginindex')  # Redirect to login if not authenticated

        return self.get_response(request)
