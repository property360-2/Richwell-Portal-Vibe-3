from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, MeSerializer


# ==============================================================
# 🔐 API VIEWS
# ==============================================================

@login_required
def dean_dashboard(request):
    return render(request, "dashboards/dean.html", {"user": request.user})

@login_required
def dean_courses(request):
    headers = ["Code", "Title", "Description"]
    return render(request, "dashboards/dean_courses.html", {"headers": headers, "user": request.user})

@login_required
def dean_subjects(request):
    headers = ["Code", "Title", "Units", "Type", "Course"]
    return render(request, "dashboards/dean_subjects.html", {"headers": headers, "user": request.user})

@login_required
def dean_sections(request):
    headers = ["Code", "Course", "Term", "Professor", "Slots"]
    return render(request, "dashboards/dean_sections.html", {"headers": headers, "user": request.user})

class HybridLoginView(APIView):
    """
    Handles both JWT token generation and Django session login.
    Works with the frontend fetch() or form-based login.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Create Django session (so @login_required works)
        login(request, user)

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": MeSerializer(user).data,
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Returns current user details (JWT protected)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class LogoutView(APIView):
    """
    Blacklists the refresh token and clears Django session.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = request.data.get("refresh")
            if token:
                token_obj = RefreshToken(token)
                token_obj.blacklist()
            logout(request)
            return Response({"detail": "Logged out successfully."}, status=200)
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=400)


# ==============================================================
# 🧱 TEMPLATE VIEWS
# ==============================================================

def login_page(request):
    """
    Renders the login template.
    If already logged in (session), redirect to dashboard.
    """
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return render(request, "login.html")


@login_required
def dashboard(request):
    """
    Renders role-based dashboard.
    Example: dashboards/dean.html, dashboards/professor.html
    """
    role = request.GET.get("role", request.user.role).lower()
    template = f"dashboards/{role}.html"
    return render(request, template, {"user": request.user})


def logout_view(request):
    """
    Logs out Django session + blacklists JWT (if provided).
    """
    refresh_token = request.COOKIES.get("refresh") or request.POST.get("refresh")
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

    logout(request)  # clears Django session
    response = redirect("/")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response