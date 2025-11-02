from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        help_text="Must be either 'user' or 'agent'"
    )

    class Meta:
        model = User
        fields = ("phone", "password", "role")
        extra_kwargs = {
            "password": {"write_only": True},
            "role": {"required": True}
        }

    def validate(self, data):
        # Convert role to lowercase for consistency
        data['role'] = data['role'].lower()

        # Validate role against model choices
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if data['role'] not in valid_roles:
            raise serializers.ValidationError({
                'role': f"Invalid role. Must be one of: {valid_roles}"
            })

        return data

    def create(self, validated_data):
        # Creates user or agent with identical fields
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "is_active", "first_login")  # Removed 'role' field
        read_only_fields = ("first_login",)

class LoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not (phone and password):
            raise serializers.ValidationError(
                'Both phone and password are required',
                code='authorization'
            )

        user = authenticate(
            request=self.context.get('request'),
            phone=phone,
            password=password
        )

        if not user:
            user_exists = User.objects.filter(phone=phone).exists()
            raise serializers.ValidationError(
                {
                    'detail': 'Invalid credentials',
                    'user_exists': user_exists
                },
                code='authorization'
            )

        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        """Enhanced response with user details"""
        data = super().to_representation(instance)
        user = instance.get('user')
        if user:
            data['user'] = {
                'id': user.id,
                'phone': user.phone,
                'is_active': user.is_active,  # Removed 'role' field
                'first_login': user.first_login
            }
        return data
