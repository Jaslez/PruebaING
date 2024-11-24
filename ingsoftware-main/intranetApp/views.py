from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Curso, Tarea, Entrega, InscripcionCurso
from .forms import CursoForm, InscripcionCursoForm
from django.urls import reverse

def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('administrador')
            elif hasattr(user, 'rol'):
                if user.rol == 'docente':
                    return redirect('docente')
                elif user.rol == 'alumno':
                    return redirect('alumno')
            else:
                return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@login_required
def administrador(request):
    if not request.user.is_superuser and request.user.rol != 'admin':
        return redirect('login')

    # Obtener todos los alumnos, docentes y cursos
    alumnos = Usuario.objects.filter(rol='alumno')
    docentes = Usuario.objects.filter(rol='docente')
    cursos = Curso.objects.all()

    # Formularios para creación de usuario, curso e inscripción
    curso_form = CursoForm(request.POST or None)
    inscripcion_form = InscripcionCursoForm(request.POST or None)

    # Manejo de formularios en una sola vista
    if request.method == 'POST':
        # Verificar qué formulario fue enviado
        if 'crear_usuario' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            rol = request.POST.get('rol')

            if username and password and email and rol:
                # Crear el nuevo usuario
                if rol == 'docente':
                    Usuario.objects.create_user(username=username, email=email, password=password, rol='docente')
                elif rol == 'alumno':
                    Usuario.objects.create_user(username=username, email=email, password=password, rol='alumno')
                messages.success(request, f"Usuario '{username}' creado exitosamente.")
            else:
                messages.error(request, "Todos los campos son requeridos para crear un usuario.")

        elif 'crear_curso' in request.POST and curso_form.is_valid():
            curso = curso_form.save(commit=False)
            curso.save()
            messages.success(request, f"Curso '{curso.nombre}' creado exitosamente.")

        elif 'inscribir_alumno' in request.POST:
            curso_id = request.POST.get('curso')
            alumno_id = request.POST.get('alumno')

            if curso_id and alumno_id:
                curso = get_object_or_404(Curso, id=curso_id)
                alumno = get_object_or_404(Usuario, id=alumno_id)

                # Crear la inscripción con los datos correctos
                inscripcion = InscripcionCurso(curso=curso, alumno=alumno)
                inscripcion.save()
                messages.success(request, f"Alumno {alumno.username} inscrito en el curso '{curso.nombre}' exitosamente.")
            else:
                messages.error(request, "Debe seleccionar tanto el alumno como el curso para proceder con la inscripción.")

        elif 'editar_curso' in request.POST:
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=curso_id)
            form = CursoForm(request.POST, instance=curso)
            if form.is_valid():
                form.save()
                messages.success(request, f"El curso '{curso.nombre}' ha sido actualizado.")

        elif 'eliminar_curso' in request.POST:
            curso_id = request.POST.get('curso_id')
            curso = get_object_or_404(Curso, id=curso_id)
            curso.delete()
            messages.success(request, f"El curso '{curso.nombre}' ha sido eliminado.")

        elif 'eliminar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            usuario = get_object_or_404(Usuario, id=usuario_id)
            usuario.delete()
            messages.success(request, f"El usuario '{usuario.username}' ha sido eliminado.")

        # Recargar la página para actualizar los datos
        return redirect('administrador')

    # Renderizar la vista con los formularios y listas
    return render(request, 'administrador.html', {
        'alumnos': alumnos,
        'docentes': docentes,
        'cursos': cursos,
        'curso_form': curso_form,
        'inscripcion_form': inscripcion_form,
    })


@login_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.user.is_superuser:
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
    return redirect('administrador')

@login_required
def docente(request):
    if request.user.rol != 'docente':
        return redirect('login')
    
    cursos = Curso.objects.filter(docente=request.user)
    tareas = Tarea.objects.filter(curso__in=cursos)
    return render(request, 'docente.html', {'cursos': cursos, 'tareas': tareas})

@login_required
def alumno(request):
    if request.user.rol != 'alumno':
        return redirect('login')

    # Obtener los cursos en los que el alumno está inscrito
    cursos = Curso.objects.filter(inscripcioncurso__alumno=request.user)

    # Obtener las tareas asignadas a esos cursos
    tareas_recientes = Tarea.objects.filter(curso__in=cursos).order_by('-fecha_creacion')[:5]

    # Renderizar la plantilla con la lista resumida de tareas
    return render(request, 'alumno.html', {
        'tareas_recientes': tareas_recientes,
    })

    
@login_required
def crear_tarea(request, curso_id):
    if request.user.rol != 'docente':
        return redirect('login')
    curso = get_object_or_404(Curso, id=curso_id, docente=request.user)
    if request.method == 'POST':
        Tarea.objects.create(
            titulo=request.POST['titulo'],
            descripcion=request.POST['descripcion'],
            curso=curso,
            fecha_limite=request.POST['fecha_limite'],
            archivo=request.FILES.get('archivo')
        )
        messages.success(request, 'Tarea creada exitosamente')
        return redirect('docente')
    return render(request, 'crear_tarea.html', {'curso': curso})

@login_required
def entregar_tarea(request, tarea_id):
    if request.user.rol != 'alumno':
        return redirect('login')

    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.method == 'POST':
        # Verificamos si ya existe una entrega para esta tarea
        entrega, created = Entrega.objects.get_or_create(
            tarea=tarea,
            alumno=request.user,
            defaults={'archivo': request.FILES['archivo']}
        )
        
        if not created:  # Si ya existe una entrega, la actualizamos
            entrega.archivo = request.FILES['archivo']
            entrega.save()

        messages.success(request, 'Tarea entregada exitosamente')
        return redirect('alumno_panel')

    return render(request, 'entregar_tarea.html', {'tarea': tarea})

@login_required
def calificar_tarea(request, entrega_id):
    if request.user.rol != 'docente':
        return redirect('login')
    entrega = get_object_or_404(Entrega, id=entrega_id, tarea__curso__docente=request.user)
    if request.method == 'POST':
        entrega.calificacion = request.POST['calificacion']
        entrega.observaciones = request.POST['observaciones']
        entrega.save()
        messages.success(request, 'Tarea calificada exitosamente')
        return redirect('docente')
    return render(request, 'calificar_tarea.html', {'entrega': entrega})

@login_required
def editar_tarea(request, tarea_id):
    if request.user.rol != 'docente':
        return redirect('login')
    
    tarea = get_object_or_404(Tarea, id=tarea_id, curso__docente=request.user)
    if request.method == 'POST':
        tarea.titulo = request.POST.get('titulo')
        tarea.descripcion = request.POST.get('descripcion')
        tarea.fecha_limite = request.POST.get('fecha_limite')
        tarea.archivo = request.FILES.get('archivo', tarea.archivo)  # Si no se sube un archivo nuevo, mantener el anterior
        tarea.save()
        messages.success(request, 'Tarea actualizada exitosamente')
        return redirect('docente')

    return render(request, 'editar_tarea.html', {'tarea': tarea})

@login_required
def ver_entregas(request, curso_id):
    if request.user.rol != 'docente':
        return redirect('login')

    curso = get_object_or_404(Curso, id=curso_id, docente=request.user)
    entregas = Entrega.objects.filter(tarea__curso=curso)

    return render(request, 'ver_entregas.html', {'curso': curso, 'entregas': entregas})

# View para ver los alumnos de un curso específico
@login_required
def ver_alumnos_curso(request, curso_id):
    if request.user.rol != 'docente':
        return redirect('login')

    # Obtener el curso por su ID y verificar que pertenece al docente actual
    curso = get_object_or_404(Curso, id=curso_id, docente=request.user)

    # Obtener los alumnos inscritos en el curso
    alumnos = Usuario.objects.filter(inscripcioncurso__curso=curso)

    return render(request, 'ver_alumnos_curso.html', {
        'curso': curso,
        'alumnos': alumnos,
    })

# View para ver los detalles de un alumno específico
@login_required
def detalle_alumno(request, alumno_id):
    if request.user.rol != 'docente':
        return redirect('login')

    # Obtener el alumno y verificar que está inscrito en uno de los cursos del docente
    alumno = get_object_or_404(Usuario, id=alumno_id, rol='alumno')
    cursos_docente = Curso.objects.filter(docente=request.user)

    if not cursos_docente.filter(inscripcioncurso__alumno=alumno).exists():
        messages.error(request, 'No tienes permiso para ver los detalles de este alumno.')
        return redirect('docente')

    # Obtener entregas del alumno
    entregas = Entrega.objects.filter(alumno=alumno)

    return render(request, 'detalle_alumno.html', {
        'alumno': alumno,
        'entregas': entregas,
    })

# View para calificar a un alumno
@login_required
def calificar_alumno(request, alumno_id):
    if request.user.rol != 'docente':
        return redirect('login')

    # Obtener el alumno y verificar que está inscrito en uno de los cursos del docente
    alumno = get_object_or_404(Usuario, id=alumno_id, rol='alumno')
    cursos_docente = Curso.objects.filter(docente=request.user)

    if not cursos_docente.filter(inscripcioncurso__alumno=alumno).exists():
        messages.error(request, 'No tienes permiso para calificar a este alumno.')
        return redirect('docente')

    if request.method == 'POST':
        entrega_id = request.POST.get('entrega_id')
        calificacion = request.POST.get('calificacion')
        observaciones = request.POST.get('observaciones')

        # Obtener la entrega y actualizar la calificación
        entrega = get_object_or_404(Entrega, id=entrega_id, alumno=alumno)
        entrega.calificacion = calificacion
        entrega.observaciones = observaciones
        entrega.save()

        messages.success(request, f'La entrega de {alumno.username} ha sido calificada exitosamente.')
        return redirect('detalle_alumno', alumno_id=alumno_id)

    # Obtener entregas del alumno que aún no han sido calificadas
    entregas_pendientes = Entrega.objects.filter(alumno=alumno, calificacion__isnull=True)

    return render(request, 'calificar_alumno.html', {
        'alumno': alumno,
        'entregas_pendientes': entregas_pendientes,
    })
    
    
@login_required
def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    return render(request, 'detalle_tarea.html', {'tarea': tarea})


@login_required
def ver_calificaciones(request):
    if request.user.rol != 'alumno':
        return redirect('login')

    # Obtener las entregas calificadas del alumno
    entregas = Entrega.objects.filter(alumno=request.user, calificacion__isnull=False)

    return render(request, 'ver_calificaciones.html', {
        'entregas': entregas,
    })
    

@login_required
def ver_tarea(request, tarea_id):
    # Obtener la tarea correspondiente
    tarea = get_object_or_404(Tarea, id=tarea_id)
    
    # Filtrar las entregas del alumno para esta tarea si es un alumno
    entregas = None
    if request.user.rol == 'alumno':
        entregas = Entrega.objects.filter(tarea=tarea, alumno=request.user)
    
    # Renderizar la plantilla con los detalles de la tarea y el historial de entregas
    return render(request, 'ver_tarea.html', {
        'tarea': tarea,
        'entregas': entregas,
    })

@login_required
def ver_tareas(request):
    if request.user.rol != 'alumno':
        return redirect('login')

    # Obtener los cursos en los que el alumno está inscrito
    cursos = Curso.objects.filter(inscripcioncurso__alumno=request.user)

    # Obtener todas las tareas asignadas a los cursos del alumno
    tareas = Tarea.objects.filter(curso__in=cursos)

    # Renderizar la plantilla con la lista de tareas
    return render(request, 'ver_tareas.html', {
        'tareas': tareas,
    })
