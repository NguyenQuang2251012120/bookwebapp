from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()

class DomainRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        host = request.get_host().split(":")[0]  # Lấy domain mà không bao gồm port

        # Cho phép truy cập vào login1 mà không cần xác thực
        if path == "/login1/":
            return self.get_response(request)

        # Các logic khác liên quan đến xác thực tenant
        user = request.user
        if user.is_authenticated:
            schema_name = user.schema_name
            if schema_name and schema_name != host:
                correct_domain = f"http://{schema_name}.localhost:8000/login1/"
                return redirect(correct_domain)

        elif path != "/login/":  # Người chưa đăng nhập chỉ có thể truy cập public login
            return HttpResponseForbidden("Bạn cần đăng nhập để truy cập trang này!")

        return self.get_response(request)

