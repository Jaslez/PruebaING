from django import forms
from .models import Curso, InscripcionCurso, Usuario

class CursoForm(forms.ModelForm):
    docente = forms.ModelChoiceField(queryset=Usuario.objects.filter(rol='docente'), required=True, label='Docente Responsable')

    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'docente']

class InscripcionCursoForm(forms.ModelForm):
    alumno = forms.ModelChoiceField(queryset=Usuario.objects.filter(rol='alumno'), required=True, label='Alumno')

    class Meta:
        model = InscripcionCurso
        fields = ['alumno']
