"""
URL configuration for intranet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from intranetApp import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('administrador/', views.administrador, name='administrador'),
    path('docente/', views.docente, name='docente'),
    path('alumno/', views.alumno, name='alumno'),
    path('crear_tarea/<int:curso_id>/', views.crear_tarea, name='crear_tarea'),
    path('entregar_tarea/<int:tarea_id>/', views.entregar_tarea, name='entregar_tarea'),
    path('calificar_tarea/<int:entrega_id>/', views.calificar_tarea, name='calificar_tarea'),
    path('eliminar_usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),  # Vista para eliminar usuarios
    path('docente/curso/<int:curso_id>/alumnos/', views.ver_alumnos_curso, name='ver_alumnos_curso'),
    path('docente/alumno/<int:alumno_id>/detalle/', views.detalle_alumno, name='detalle_alumno'),
    path('docente/alumno/<int:alumno_id>/calificar/', views.calificar_alumno, name='calificar_alumno'),
    path('docente/curso/<int:curso_id>/crear_tarea/', views.crear_tarea, name='crear_tarea'),
    path('docente/tarea/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('tarea/<int:tarea_id>/', views.detalle_tarea, name='detalle_tarea'),
    path('alumno/', views.alumno, name='alumno'),
    path('alumno/tarea/<int:tarea_id>/entregar/', views.entregar_tarea, name='entregar_tarea'),
    path('alumno/calificaciones/', views.ver_calificaciones, name='ver_calificaciones'),
    path('alumno/tareas/', views.ver_tareas, name='ver_tareas'),
    path('alumno/tarea/<int:tarea_id>/', views.ver_tarea, name='ver_tarea'),
]   