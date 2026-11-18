from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CadastroSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def cadastro(request):
    serializer = CadastroSerializer(data=request.data)

    if serializer.is_valid():
        usuario = serializer.save()

        return Response(
            {
                "mensagem": "Cadastro realizado com sucesso!",
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.first_name,
                    "email": usuario.email,
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email", "").strip().lower()
    senha = request.data.get("senha", "")

    if not email or not senha:
        return Response(
            {"erro": "Informe o e-mail e a senha."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario_cadastrado = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response(
            {"erro": "E-mail ou senha incorretos."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    usuario = authenticate(
        request,
        username=usuario_cadastrado.username,
        password=senha
    )

    if usuario is None:
        return Response(
            {"erro": "E-mail ou senha incorretos."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(usuario)

    return Response({
        "mensagem": "Login realizado com sucesso!",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": {
            "id": usuario.id,
            "nome": usuario.first_name,
            "email": usuario.email,
        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meu_perfil(request):
    usuario = request.user

    return Response({
        "id": usuario.id,
        "nome": usuario.first_name,
        "email": usuario.email,
    })