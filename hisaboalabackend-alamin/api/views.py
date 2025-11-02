from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import permissions, generics
# from user.models import User, PhoneOTP
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# import random
# from django.contrib.auth import login
# from .serializers import *

# from knox.views import LoginView as KnoxLoginView
# from knox.auth import TokenAuthentication

# # Create your views here.
# class ValidatePhoneSentOTP(APIView):
#     """Validation of phone, otp sent and limit otp sent with count"""
#     def post(self, request, *args, **kwargs):
#         phone_number = request.data.get("phone")
#         if phone_number:
#             phone = str(phone_number)
#             user = User.objects.filter(phone__iexact=phone)
#             if user.exists():
#                 return Response(
#                     {"status": False, "detail": "Phone Number already exists."}
#                 )
#             else:
#                 key = send_otp(phone)
#                 if key:
#                     old = PhoneOTP.objects.filter(phone__iexact=phone)
#                     if old.exists():
#                         old = old.first()
#                         count = old.count
#                         if count > 10:
#                             return Response(
#                                 {
#                                     'status': False,
#                                     'detail': 'Sending otp error. Limit exceeded. Please contact customer support.'
#                                 }
#                             )
#                         old.count = count + 1
#                         old.save()
#                         print("Count increases", count)
#                         return Response({
#                             'status': True,
#                             'detail': 'OTP sent successfully.'
#                         })
#                     else:
#                         PhoneOTP.objects.create(
#                             phone=phone,
#                             otp=key,
#                         )
#                         return Response(
#                         {
#                             "status": True,
#                             "detail": "OTP sent successfully."
#                         }
#                     )
#                 else:
#                     return Response({"status": False, "detail": "Sending otp error"})
#         else:
#             return Response(
#                 {"status": False, "detail": "Phone Number is not given in post request"}
#             )


# def send_otp(phone):
#     if phone:
#         key = random.randint(1000, 9999)
#         return key
#     else:
#         return False


# class ValidateOTP(APIView):
#     """Validation of OTP, If u havre received otp, post a request with phone+otp and u will be redirected to set the password."""
#     def post(self, request, *args, **kwargs):
#         phone = request.data.get('phone', False)
#         otp_sent = request.data.get('otp', False)

#         if phone and otp_sent:
#             old = PhoneOTP.objects.filter(phone__iexact=phone)
#             if old.exists():
#                 old = old.first()
#                 otp = old.otp
#                 if str(otp_sent) == str(otp):
#                     old.validated = True
#                     old.save()
#                     return Response({
#                         'status': True,
#                         'detail': 'OTP MATCHED, Please proceed for registrations.'
#                     })
#                 else:
#                     return Response({
#                         'status': False,
#                         'detail': 'OTP INCORRECT'
#                     })
#             else:
#                 return Response({
#                     'status': False,
#                     'detail': 'First Proceed via sending otp request.'
#                 })
#         else:
#             return Response({
#                 'status': False,
#                 'detail': 'Please provide both phone and otp validation'
#             })


# class Register(APIView):
#     def post(self, request, *args, **kwargs):
#         phone = request.data.get('phone', False)
#         password = request.data.get('password', False)

#         if phone and password:
#             old = PhoneOTP.objects.filter(phone__iexact=phone)
#             if old.exists():
#                 old = old.first()
#                 validated = old.validated
#                 if validated:
#                     temp_data = {
#                         'phone': phone,
#                         'password': password
#                     }
#                     serializer = CreateUserSerializer(data = temp_data)
#                     serializer.is_valid(raise_exception= True)
#                     user = serializer.save()
#                     old.delete()
#                     return Response({
#                         'status': True,
#                         'detail': 'Account created.'
#                     })

#                 else:
#                     return Response({
#                         'status': False,
#                         'detail': 'OTP Not varified yet.'
#                     })

#             else:
#                 return Response({
#                     'status' : False,
#                     'detail' : 'Please varify number first.'
#                 })
#         else:
#             return Response({
#                 'status' : False,
#                 'detail' : 'Phone and Password are not sent'
#             })

# class LoginAPI(KnoxLoginView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         serializer = LoginUserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         if user.last_login is None :
#             user.first_login = True
#             user.save()

#         elif user.first_login:
#             user.first_login = False
#             user.save()

# class UserAPI(generics.RetrieveAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated, ]
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user


