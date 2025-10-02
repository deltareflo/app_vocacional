from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, SelectField, \
    DateField, TextAreaField, FieldList, Form as WTForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models import fecha_actual


class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)], render_kw={"placeholder": "Nombre"})
    password = PasswordField('Contraseña', validators=[DataRequired()], render_kw={"placeholder": "contraseña"})
    edad = IntegerField('Edad', render_kw={"placeholder": "edad"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
    submit = SubmitField('Registrar')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={"placeholder": "email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "contraseña"})
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar recuperación de contraseña')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cambiar Contraseña')

class ContactoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()], render_kw={"placeholder": "Nombre"})
    numero = StringField('Número', validators=[DataRequired()], render_kw={"placeholder": "Número"})
    submit = SubmitField('Registrar')


class SegForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)], render_kw={"placeholder": "Nombre"})
    edad = IntegerField('Edad',validators=[DataRequired()], render_kw={"placeholder": "edad"})
    grado = StringField('Grado', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Grado"})
    localidad = StringField('Localidad', validators=[Length(max=60)],
                            render_kw={"placeholder": "Localidad"})
    email = StringField('Email', validators=[Length(max=150)], render_kw={"placeholder": "Email"})
    carpeta = StringField('Carpeta', validators=[Length(max=150)], render_kw={"placeholder": "Carpeta drive"})
    contacto = SelectField('Contacto', coerce=int)
    submit = SubmitField('Registrar')


class ConsultaForm(FlaskForm):
    fecha = StringField('Fecha', render_kw={f"placeholder": f"{fecha_actual()}"})
    profesional = SelectField('Profesional', coerce=int)
    comentario = StringField('Comentario', validators=[Length(max=100)], render_kw={"placeholder": "Comentario..."})
    usuario = SelectField('Usuario', coerce=int)
    submit = SubmitField('Registrar')


class EvalTipoForm(FlaskForm):
    evaluacion = StringField('Evaluacion', validators=[ Length(max=60)], render_kw={"placeholder": "Perfil completo"})
    submit = SubmitField('Registrar')


class EvalForm(FlaskForm):
    fecha = DateField('Fecha', render_kw={f"placeholder": f"{fecha_actual()}"})
    profesional1 = SelectField('Profesional 1', coerce=int)
    profesional2 = SelectField('Profesional 2', coerce=int)
    usuario = SelectField('Usuario', coerce=int)
    evaluacion = SelectField('Evaluacion', coerce=int)
    submit = SubmitField('Registrar')


class InformeForm(FlaskForm):
    fecha = DateField('Fecha', format='%m/%d/%Y', render_kw={f"placeholder": f"{fecha_actual()}"})
    comentario = StringField('Comentario', validators=[Length(max=100)], render_kw={"placeholder": "Comentario"})
    usuario = SelectField('Usuario', coerce=int)
    submit = SubmitField('Registrar')


class ResultadoForm(FlaskForm):
    fecha = DateField('Fecha', render_kw={f"placeholder": f"{fecha_actual()}"})
    comentario = StringField('Recomendación', validators=[Length(max=150)],
                                render_kw={"placeholder": "Comentario"})
    aa_cc = StringField('Altas capacidades', validators=[Length(max=50), DataRequired()],
                        render_kw={"placeholder": "Si"})
    excepcionalidad = StringField('Excepcionalidad', validators=[Length(max=50)],
                                  render_kw={"placeholder": "TDAH"})
    recomendacion = StringField('Recomendación', validators=[Length(max=100)],
                                render_kw={"placeholder": "Recomendación"})
    usuario = SelectField('Usuario', coerce=int)
    submit = SubmitField('Registrar')


class AcompForm(FlaskForm):
    fecha_inicio = StringField('Fecha', render_kw={f"placeholder": f"{fecha_actual()}"})
    encargado = SelectField('Profesional', coerce=int)
    modalidad = StringField('Modalidad', validators=[Length(max=20)],
                            render_kw={"placeholder": "Anual"})
    comentario = TextAreaField('Comentario')
    usuario = SelectField('Usuario', coerce=int)
    tipo_acompa = SelectField('Acompañamiento', coerce=int)
    submit = SubmitField('Registrar')


class TipoAcompForm(FlaskForm):
    tipo = StringField('Tipo', validators=[Length(max=50), DataRequired()], render_kw={"placeholder": "Acompañamiento"})
    submit = SubmitField('Registrar')


class InfoForm(FlaskForm):
    fecha_creado = DateField('Fecha', render_kw={f"placeholder": f"{fecha_actual()}"})
    info = TextAreaField('Comentario')
    usuario = SelectField('Usuario', coerce=int)
    submit = SubmitField('Registrar')


class ProfeForm(FlaskForm):
    nombre = StringField('Nombre', validators=[Length(max=50), DataRequired()], render_kw={"placeholder": "Nombre"})
    submit = SubmitField('Registrar')


class RavenGral(FlaskForm):
    nombre = StringField('Nombre', validators=[Length(max=50), DataRequired()], render_kw={"placeholder": "Nombre"})
    cedula = IntegerField('C.I. N°',validators=[DataRequired()], render_kw={"placeholder": "cedula"})
    edad = IntegerField('Edad',validators=[DataRequired()], render_kw={"placeholder": "edad"})
    fecha_nac = DateField('Fecha Nacimiento', format='%Y-%m-%d', render_kw={f"placeholder": f"{fecha_actual()}"})
    fecha_aplicacion = DateField('Fecha Aplicación', format='%Y-%m-%d', render_kw={f"placeholder": f"{fecha_actual()}"})
    email = StringField('Email', validators=[Length(max=150)], render_kw={"placeholder": "Email"})
    institucion = StringField('Intitución', validators=[DataRequired(), Length(max=60)], render_kw={"placeholder": "Institución"})
    curso = StringField('Curso', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Curso"})
    seccion = StringField('Seccion', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Sección"})
    turno = StringField('Turno', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Turno"})
    telefono = IntegerField('Telefono',validators=[DataRequired()], render_kw={"placeholder": "982123456"})
    contacto = StringField('Info Contacto', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Contacto"})
    evaluador = StringField('Evaluador', validators=[DataRequired(), Length(max=40)], render_kw={"placeholder": "Lic. Ana López"})
    submit = SubmitField('Registrar')


class EnvioMailForm(FlaskForm):
    institucion = SelectField("Institución", validators=[DataRequired()])

class TestItemForm(WTForm):
    item = IntegerField('Respuesta', validators=[DataRequired(), NumberRange(min=0, max=4)])

class CustomTestForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    cedula = StringField('Cédula', validators=[DataRequired(), Length(max=20)])
    sexo = SelectField('Sexo', choices=[('', 'Seleccione'), ('Masculino', 'Masculino'), ('Femenino', 'Femenino')], validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    fecha_aplicacion = DateField('Fecha de Aplicación', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    evaluador = StringField('Evaluador', validators=[DataRequired(), Length(max=64)])

    # Segundo Test (Flask-WTF)
    test2_items = FieldList(IntegerField('Ítem', validators=[DataRequired(), NumberRange(min=0, max=4)]), min_entries=10, max_entries=10)

    submit = SubmitField('Guardar Test')
