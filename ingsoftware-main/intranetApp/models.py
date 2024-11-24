from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('docente', 'Docente'),
        ('alumno', 'Alumno')
    )
    rol = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    docente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'docente'})


class Tarea(models.Model):
    ESTADOS = (
        ('asignada', 'Asignada'),
        ('proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('vencida', 'Vencida')
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_limite = models.DateTimeField()
    archivo = models.FileField(upload_to='tareas/', null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='asignada')

    def __str__(self):
        return self.titulo


class Entrega(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'alumno'})
    archivo = models.FileField(upload_to='entregas/')
    fecha_entrega = models.DateTimeField(default=timezone.now)
    calificacion = models.FloatField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    @property
    def is_late(self):
        return self.fecha_entrega > self.tarea.fecha_limite

    def __str__(self):
        return f"Entrega de {self.alumno.username} - {self.tarea.titulo}"
    
    

    
class InscripcionCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'alumno'})
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.alumno.username} inscrito en {self.curso.nombre}"
