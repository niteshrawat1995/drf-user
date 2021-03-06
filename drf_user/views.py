from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView

from django.utils.text import gettext_lazy as _


class Register(CreateAPIView):
    """
    Register a new user to the system.
    """
    from .serializers import UserSerializer
    from rest_framework.permissions import AllowAny
    from rest_framework.renderers import JSONRenderer

    renderer_classes = (JSONRenderer,)
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        from .models import User

        user = User.objects.create_user(username=serializer.validated_data['username'],
                                        email=serializer.validated_data['email'],
                                        name=serializer.validated_data['name'],
                                        password=serializer.validated_data['password'],
                                        mobile=serializer.validated_data['mobile'],
                                        is_whatsapp=serializer.validated_data['is_whatsapp'])
        serializer = self.get_serializer(user)


class Login(APIView):
    """
    This is used to Login into system. The data required are 'username' and 'password'.
    In 'username' user can provide either username or mobile or email address.
    """
    from rest_framework_jwt.serializers import JSONWebTokenSerializer
    from rest_framework.permissions import AllowAny
    from rest_framework.renderers import JSONRenderer

    renderer_classes = (JSONRenderer,)
    permission_classes = (AllowAny,)
    serializer_class = JSONWebTokenSerializer

    def validated(self, serialized_data, *args, **kwargs):
        from rest_framework_jwt.settings import api_settings

        from datetime import datetime

        from .models import AuthTransaction

        from drfaddons.add_ons import get_client_ip

        from rest_framework.response import Response

        user = serialized_data.object.get('user') or self.request.user
        token = serialized_data.object.get('token')
        response_data = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER(token, user, self.request)
        response = Response(response_data)
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                token,
                                expires=expiration,
                                httponly=True)

        user.last_login = datetime.now()
        user.save()

        AuthTransaction(user=user, ip_address=get_client_ip(self.request), token=token,
                        session=user.get_session_auth_hash()).save()

        return response

    def post(self, request):
        from drfaddons.add_ons import JsonResponse

        from rest_framework import status

        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid():
            return self.validated(serialized_data=serialized_data)
        else:
            return JsonResponse(serialized_data.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class VerifyOTP(APIView):
    """
    Used to VerifyOTP
    """
    from .serializers import OTPSerializer

    from rest_framework.permissions import AllowAny

    permission_classes = (AllowAny, )
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from rest_framework.mixins import status

        from rest_framework.exceptions import APIException

        from .utils import validate_otp, login_user, generate_otp, send_otp

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        destination = serializer.validated_data.get('destination')
        prop = serializer.validated_data.get('prop')
        user = serializer.validated_data.get('user')
        email = serializer.validated_data.get('email')
        is_login = serializer.validated_data.get('is_login')

        if 'verify_otp' in request.data.keys():
            if validate_otp(destination, request.data.get('verify_otp')):
                if is_login:
                    return Response(login_user(user, self.request), status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(data={'OTP': [_('OTP Validated successfully!'), ]}, status=status.HTTP_202_ACCEPTED)
        else:
            otp_obj = generate_otp(prop, destination)
            sentotp = send_otp(destination, otp_obj, email)

            if sentotp['success']:
                otp_obj.send_counter += 1
                otp_obj.save()

                return Response(sentotp, status=status.HTTP_201_CREATED)
            else:
                raise APIException(detail=_('A Server Error occurred: ' + sentotp['message']))


class CheckUnique(APIView):
    """
    This view checks if the given property -> value pair is unique (or doesn't exists yet)
    'prop': A property to check for uniqueness (username/email/mobile)
    'value': Value against property which is to be checked for.
    """
    from .serializers import CheckUniqueSerializer
    from rest_framework.permissions import AllowAny
    from rest_framework.renderers import JSONRenderer

    renderer_classes = (JSONRenderer,)
    permission_classes = (AllowAny,)
    serializer_class = CheckUniqueSerializer

    def validated(self, serialized_data, *args, **kwargs):
        from .utils import check_unique

        from rest_framework.mixins import status

        return {'unique': check_unique(serialized_data.validated_data['prop'],
                                       serialized_data.validated_data['value'])}, status.HTTP_200_OK

    def post(self, request):
        from drfaddons.add_ons import JsonResponse
        from rest_framework import status

        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid():
            return JsonResponse(self.validated(serialized_data=serialized_data))
        else:
            return JsonResponse(serialized_data.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class RetrieveUpdateUserAccountView(RetrieveUpdateAPIView):
    """
    This view is to update a user profile.
    """
    from .serializers import UserSerializer
    from .models import User

    from rest_framework.permissions import IsAuthenticated

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'created_by'

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        if 'password' in request.data.keys():
            self.request.user.set_password(request.data.pop('password'))
            self.request.user.save()

        return super(RetrieveUpdateUserAccountView, self).update(request, *args, **kwargs)


class LogoutView(RetrieveAPIView):
    """
    View logs out user from the system i.e. invalidates a token
    """
    from rest_framework.permissions import IsAuthenticated

    from .models import AuthTransaction

    permission_classes = (IsAuthenticated, )
    queryset = AuthTransaction.objects.all()
    lookup_field = 'token'

    def get_object(self):
        self.kwargs[self.lookup_field] = self.request.META.get('HTTP_AUTHORIZATION')
        self.kwargs['user'] = self.request.user
        return super(LogoutView, self).get_object()

    def retrieve(self, request, *args, **kwargs):
        from rest_framework.response import Response

        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'user': [_('Logout successfully.'), ]})
