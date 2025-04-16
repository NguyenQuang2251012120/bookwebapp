from django.http import HttpResponseForbidden
from django.shortcuts import redirect

class DomainRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        host = request.get_host()

        # Nếu tenant domain truy cập vào trang login của public domain, chuyển hướng về login1
        if path == "/login/" and host != "127.0.0.1:8000":
            return HttpResponseForbidden("Lỗi, vui lòng quay lại trang ban đầu!")

        # Nếu public domain truy cập vào login1, chuyển hướng về login của public domain
        if path == "/login1/" and host == "127.0.0.1:8000":
            return redirect("/login/")  # Chuyển đến login

        return self.get_response(request)
