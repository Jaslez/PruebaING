from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

class UsuarioFactory:
    @staticmethod
    def crear_usuario(username, password, email, rol):
        User = get_user_model()
        try:
            usuario = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                rol=rol
            )
            return usuario
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None

class DocenteFactory(UsuarioFactory):
    @staticmethod
    def crear_usuario(username, password, email):
        return UsuarioFactory.crear_usuario(username, password, email, 'docente')

class AlumnoFactory(UsuarioFactory):
    @staticmethod
    def crear_usuario(username, password, email):
        return UsuarioFactory.crear_usuario(username, password, email, 'alumno')