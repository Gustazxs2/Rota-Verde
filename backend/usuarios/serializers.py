from django.contrib.auth.models import User
from rest_framework import serializers


class CadastroSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="first_name")
    email = serializers.EmailField()
    senha = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "nome", "email", "senha"]

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email

    def create(self, validated_data):
        senha = validated_data.pop("senha")
        email = validated_data.pop("email")

        usuario = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            **validated_data
        )

        return usuario
