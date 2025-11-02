from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics, status
from user.models import User, PhoneOTP
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
from django.contrib.auth import login
from .serializers import *
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox.views import LogoutView as KnoxLogoutView
from rest_framework.permissions import IsAuthenticated

# Custom Permission Classes
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'agent'

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'staff'

class ValidatePhoneSentOTP(APIView):
    """Validation of phone, otp sent and limit otp sent with count"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone")
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response(
                    {"status": False, "detail": "Phone Number already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response(
                                {
                                    'status': False,
                                    'detail': 'Sending otp error. Limit exceeded. Please contact customer support.'
                                },
                                status=status.HTTP_429_TOO_MANY_REQUESTS
                            )
                        old.count = count + 1
                        old.save()
                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully.'
                        })
                    else:
                        PhoneOTP.objects.create(
                            phone=phone,
                            otp=key,
                        )
                        return Response(
                            {
                                "status": True,
                                "detail": "OTP sent successfully."
                            }
                        )
                else:
                    return Response(
                        {"status": False, "detail": "Sending otp error"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(
                {"status": False, "detail": "Phone Number is not given in post request"},
                status=status.HTTP_400_BAD_REQUEST
            )


def send_otp(phone):
    if phone:
        key = random.randint(1000, 9999)
        return key
    else:
        return False


class ValidateOTP(APIView):
    """Validation of OTP"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp_sent) == str(otp):
                    old.validated = True
                    old.save()
                    return Response({
                        'status': True,
                        'detail': 'OTP MATCHED, Please proceed for registration.'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP INCORRECT'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'status': False,
                    'detail': 'First proceed via sending otp request.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'status': False,
                'detail': 'Please provide both phone and otp for validation'
            }, status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        required_fields = ['phone', 'password', 'role']

        # Validate all required fields are present
        if not all(field in request.data for field in required_fields):
            return Response({
                'status': False,
                'detail': f'Required fields: {", ".join(required_fields)}',
                'missing_fields': [f for f in required_fields if f not in request.data]
            }, status=status.HTTP_400_BAD_REQUEST)

        phone = request.data['phone']
        password = request.data['password']
        role = request.data['role'].lower()  # Normalize to lowercase

        # OTP Verification (your existing code)
        old = PhoneOTP.objects.filter(phone__iexact=phone).first()
        if not old or not old.validated:
            return Response({
                'status': False,
                'detail': 'OTP not verified.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        serializer = CreateUserSerializer(data={
            'phone': phone,
            'password': password,
            'role': role
        })

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            old.delete()

            return Response({
                'status': True,
                'detail': 'Account created successfully.',
                'user': {
                    'phone': user.phone,
                    'role': user.role,
                    'first_login': user.first_login
                }
            })

        except serializers.ValidationError as e:
            return Response({
                'status': False,
                'detail': 'Validation failed',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.last_login is None:
            user.first_login = True
        else:
            user.first_login = False
        user.save()

        login(request, user)
        response = super().post(request, format=None)

        # Remove role from the response
        response.data['user'] = {
            'id': user.id,
            'phone': user.phone,
            'name': user.name,
            'is_active': user.is_active  # Removed 'role' field
        }
        return response


class UserAPI(generics.RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# Role-specific views
class AdminDashboard(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            "message": "Welcome Admin",
            "user_count": User.objects.count(),
            "admin_count": User.objects.filter(role='admin').count()
        })


class AgentDashboard(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get(self, request):
        return Response({
            "message": "Welcome Agent",
            "assigned_tasks": []  # Add agent-specific data here
        })


class StaffDashboard(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get(self, request):
        return Response({
            "message": "Welcome Staff Member",
            "pending_approvals": []  # Add staff-specific data here
        })


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()