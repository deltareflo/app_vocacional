from shared import db
import datetime
import pytz
from datetime import datetime as _dt
from sqlalchemy import column, String, Integer, ForeignKey, Boolean, Text, Date
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import uuid
from time import time
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from flask import current_app

def fecha_actual():
    hoy = datetime.date.today()
    return hoy.strftime("%d/%m/%Y")


class TimestampMixin(object):
    # Use application-level timezone-aware timestamps set to Paraguay time
    _PARAGUAY_TZ = pytz.timezone('America/Asuncion')

    created = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: _dt.now(TimestampMixin._PARAGUAY_TZ)
    )
    updated = db.Column(
        db.DateTime(timezone=True), onupdate=lambda: _dt.now(TimestampMixin._PARAGUAY_TZ)
    )
    status = db.Column(Boolean, default=True)


class IntEnum(db.TypeDecorator):
    impl = db.Integer()

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

        def process_bind_param(self, value, dialect):
                if isinstance(value, enum):
                    return value
                elif isinstance(value, int):
                    return value
                return value.value

        def process_result_value(self, value, dialect):
            return self._enumtype(value)


class Opciones(enum.Enum):
    varon= 'varón'
    mujer= 'mujer'
    general= 'general'


class Usuarios(db.Model, UserMixin):
    __tablename__= 'basc_user'

    id = db.Column(Integer, primary_key=True)
    nombre= db.Column(String(length=50), nullable=False)
    edad = db.Column(Integer)
    email = db.Column(String(length=150), unique=True)
    password= db.Column(String(length=128))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def get_reset_password_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset_password': self.id})

    @staticmethod
    def get_by_id(id):
        return Usuarios.query.get(id)
    @staticmethod
    def get_by_email(email):
        return Usuarios.query.filter_by(email=email).first()
    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=600)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        user_id = data.get('reset_password') if isinstance(data, dict) else None
        return Usuarios.get_by_id(user_id)

class Examenes(db.Model):

    id = db.Column(Integer, primary_key=True)
    item1= db.Column(Integer)
    item2= db.Column(Integer)
    item3= db.Column(Integer)


class SegUser(db.Model, UserMixin, TimestampMixin):
    __tablename__= 'seguimiento_user'

    id = db.Column(Integer, primary_key=True)
    nombre = db.Column(String(length=50), nullable=False)
    edad = db.Column(Integer)
    grado = db.Column(String(length=40))
    localidad = db.Column(String(length=60))
    email = db.Column(String(length=150))
    carpeta = db.Column(String(length=150))
    # ForeignKey
    id_contacto = db.Column(Integer, ForeignKey('contacto_user.id'))
    contacto = db.relationship('ContactoSegUser', backref='seguimiento_user', lazy=True)

    def __repr__(self):
        return f'<User {self.nombre}>'


class ContactoSegUser(db.Model, TimestampMixin):
    __tablename__ = 'contacto_user'

    id = db.Column(Integer, primary_key=True)
    nombre = db.Column(String(length=50), nullable=False)
    telefono = db.Column(String(length=40))

    def __repr__(self):
        return f'<User {self.nombre}>'


class ConsultaSegUser(db.Model, TimestampMixin):
    __tablename__ = 'consulta_user'

    id = db.Column(Integer, primary_key=True)
    fecha = db.Column(String(length=15))
    # profesional = db.Column(String(length=40))
    comentario = db.Column(String(length=100))
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='consulta_user', lazy=True)
    id_prof = db.Column(Integer, ForeignKey('profesionales.id'))
    prof = db.relationship('Profesionales', backref='consulta_prof', lazy=True)

    def __repr__(self):
        return f'<Profesional {self.profesional}>'


class EvalSegUser(db.Model, TimestampMixin):
    __tablename__ = 'evaluacion_user'

    id = db.Column(Integer, primary_key=True)
    fecha = db.Column(Date)
    # profesionales = db.Column(String(length=100))
    # Foreignkey
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='eval_user', lazy=True)
    id_eval = db.Column(Integer, ForeignKey('tipos_eval.id'))
    evaluacion = db.relationship('EvaluacionTipo', backref='tipos_eval', lazy=True)
    id_prof = db.Column(Integer, ForeignKey('profesionales.id'))
    prof = db.relationship('Profesionales', backref='eval_prof', lazy=True)
    id_prof1 = db.Column(Integer)

    def __repr__(self):
        return f'<Profesional {self.profesionales}>'


class EvaluacionTipo(db.Model, TimestampMixin):
    __tablename__ = 'tipos_eval'

    id = db.Column(Integer, primary_key=True)
    evaluacion = db.Column(String(length=60), nullable=False)

    def __repr__(self):
        return f'<Evaluacion {self.evaluacion}>'


# esta clase no va
class InformeSegUser(db.Model, TimestampMixin):
    __tablename__ = 'informe_user'
    # Unir a la tabla resultado y relacionar con evalauacion
    id = db.Column(Integer, primary_key=True)
    fecha = db.Column(Date)
    comentario = db.Column(String(length=100))
    # Foreignkey
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='informe_user', lazy=True)

    def __repr__(self):
        return f'<Fecha {self.fecha}>'


class ResultadoSegUser(db.Model, TimestampMixin):
    __tablename__ = 'resultado_user'

    id = db.Column(Integer, primary_key=True)
    fecha = db.Column(Date)
    comentario = db.Column(String(length=150))
    aa_cc = db.Column(String(length=50), nullable=False)
    excepcionalidad = db.Column(String(length=50))
    recomendacion = db.Column(String(length=150))

    # Foreignkey
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='resultado_user', lazy=True)

    def __repr__(self):
        return f'<Resultado {self.aa_cc}>'


class AcompSegUser(db.Model, TimestampMixin):
    __tablename__ = 'acompanhar_user'

    id = db.Column(Integer, primary_key=True)
    fecha_inicio = db.Column(String(length=20))
    # encargado = db.Column(String(length=50))
    modalidad = db.Column(String(length=20))
    comentario = db.Column(Text)
    # Foreignkey
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='acomp_user', lazy=True)
    id_tipo = db.Column(Integer, ForeignKey('tipo_acompanamiento.id'))
    tipo = db.relationship('Tipo', backref='tipo_acompanamiento', lazy=True)
    id_prof = db.Column(Integer, ForeignKey('profesionales.id'))
    prof = db.relationship('Profesionales', backref='user_prof', lazy=True)

    def __repr__(self):
        return f'<Encargada {self.encargado}>'


class Tipo(db.Model, TimestampMixin):
    __tablename__ = 'tipo_acompanamiento'

    id = db.Column(Integer, primary_key=True)
    tipo = db.Column(String(length=50), nullable=False)

    def __repr__(self):
        return f'<Tipo {self.tipo}>'


class InfoSeg(db.Model, TimestampMixin):
    __tablename__ = 'info_seguimiento'

    id = db.Column(Integer, primary_key=True)
    fecha_creado = db.Column(Date)
    info = db.Column(Text, nullable=False)
    id_user = db.Column(Integer, ForeignKey('seguimiento_user.id'))
    user = db.relationship('SegUser', backref='info_user', lazy=True)

    def __repr__(self):
        return f'<Info {self.info}>'


class Profesionales(db.Model, TimestampMixin):
    __tablename__ = 'profesionales'

    id = db.Column(Integer, primary_key=True)
    nombre = db.Column(String(length=50), nullable=False)

    def __repr__(self):
        return f'<Nombre {self.nombre}>'
    

class ArchivoEnviado(db.Model, TimestampMixin):
    __tablename__ = 'pdf_send'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    cedula = db.Column(Integer, nullable=False)
    mail = db.Column(String(length=100))
    telefono = db.Column(Integer)
    metodo = db.Column(String(length=10), nullable=False)
    sender = db.Column(String(length=100), nullable=False)
    test = db.Column(String(length=20), nullable=False)


class DatosRavenGeneral(db.Model, TimestampMixin):
    __tablename__ = 'raven_general_datos'

    id = db.Column(Integer,primary_key=True)
    nombre = db.Column(String(length=100), nullable=False)
    cedula = db.Column(Integer, nullable=False)
    edad = db.Column(Integer, nullable=False)
    fecha_nacimiento = db.Column(Date, nullable=False)
    fecha_aplicacion = db.Column(
        Date, nullable=False)
    email = db.Column(String(length=100))
    instituto = db.Column(String(length=100), nullable=False)
    curso = db.Column(Integer, nullable=False)
    seccion = db.Column(String(length=5), nullable=False)
    turno = db.Column(String(length=10), nullable=False)
    telefono = db.Column(Integer, nullable=False)
    info_contacto = db.Column(String(length=50), nullable=False)
    evaluador = db.Column(String(length=100), nullable=False)


class TestRavenGeneral(db.Model, TimestampMixin):
    __tablename__ = 'raven_general_test'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    id_user = db.Column(Integer, ForeignKey('raven_general_datos.id'))
    item_a1 = db.Column(Integer,nullable=False)
    item_a2 = db.Column(Integer,nullable=False)
    item_a3 = db.Column(Integer,nullable=False)
    item_a4 = db.Column(Integer,nullable=False)
    item_a5 = db.Column(Integer,nullable=False)
    item_a6 = db.Column(Integer,nullable=False)
    item_a7 = db.Column(Integer,nullable=False)
    item_a8 = db.Column(Integer,nullable=False)
    item_a9 = db.Column(Integer,nullable=False)
    item_a10 = db.Column(Integer,nullable=False)
    item_a11 = db.Column(Integer,nullable=False)
    item_a12 = db.Column(Integer,nullable=False)
    item_b1 = db.Column(Integer,nullable=False)
    item_b2 = db.Column(Integer,nullable=False)
    item_b3 = db.Column(Integer,nullable=False)
    item_b4 = db.Column(Integer,nullable=False)
    item_b5 = db.Column(Integer,nullable=False)
    item_b6 = db.Column(Integer,nullable=False)
    item_b7 = db.Column(Integer,nullable=False)
    item_b8 = db.Column(Integer,nullable=False)
    item_b9 = db.Column(Integer,nullable=False)
    item_b10 = db.Column(Integer,nullable=False)
    item_b11 = db.Column(Integer,nullable=False)
    item_b12 = db.Column(Integer,nullable=False)
    item_c1 = db.Column(Integer,nullable=False)
    item_c2 = db.Column(Integer,nullable=False)
    item_c3 = db.Column(Integer,nullable=False)
    item_c4 = db.Column(Integer,nullable=False)
    item_c5 = db.Column(Integer,nullable=False)
    item_c6 = db.Column(Integer,nullable=False)
    item_c7 = db.Column(Integer,nullable=False)
    item_c8 = db.Column(Integer,nullable=False)
    item_c9 = db.Column(Integer,nullable=False)
    item_c10 = db.Column(Integer,nullable=False)
    item_c11 = db.Column(Integer,nullable=False)
    item_c12 = db.Column(Integer,nullable=False)
    item_d1 = db.Column(Integer,nullable=False)
    item_d2 = db.Column(Integer,nullable=False)
    item_d3 = db.Column(Integer,nullable=False)
    item_d4 = db.Column(Integer,nullable=False)
    item_d5 = db.Column(Integer,nullable=False)
    item_d6 = db.Column(Integer,nullable=False)
    item_d7 = db.Column(Integer,nullable=False)
    item_d8 = db.Column(Integer,nullable=False)
    item_d9 = db.Column(Integer,nullable=False)
    item_d10 = db.Column(Integer,nullable=False)
    item_d11 = db.Column(Integer,nullable=False)
    item_d12 = db.Column(Integer,nullable=False)
    item_e1 = db.Column(Integer,nullable=False)
    item_e2 = db.Column(Integer,nullable=False)
    item_e3 = db.Column(Integer,nullable=False)
    item_e4 = db.Column(Integer,nullable=False)
    item_e5 = db.Column(Integer,nullable=False)
    item_e6 = db.Column(Integer,nullable=False)
    item_e7 = db.Column(Integer,nullable=False)
    item_e8 = db.Column(Integer,nullable=False)
    item_e9 = db.Column(Integer,nullable=False)
    item_e10 = db.Column(Integer,nullable=False)
    item_e11 = db.Column(Integer,nullable=False)
    item_e12 = db.Column(Integer,nullable=False)

class TestRavenAvanzado(db.Model, TimestampMixin):
    __tablename__ = 'raven_avanzado_test'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    id_user = db.Column(Integer, ForeignKey('raven_general_datos.id'))
    inicio = db.Column(db.Time)
    fin = db.Column(db.Time)
    duracion = db.Column(db.Time)
    item_a1 = db.Column(Integer,nullable=False)
    item_a2 = db.Column(Integer,nullable=False)
    item_a3 = db.Column(Integer,nullable=False)
    item_a4 = db.Column(Integer,nullable=False)
    item_a5 = db.Column(Integer,nullable=False)
    item_a6 = db.Column(Integer,nullable=False)
    item_a7 = db.Column(Integer,nullable=False)
    item_a8 = db.Column(Integer,nullable=False)
    item_a9 = db.Column(Integer,nullable=False)
    item_a10 = db.Column(Integer,nullable=False)
    item_a11 = db.Column(Integer,nullable=False)
    item_a12 = db.Column(Integer,nullable=False)
    item_b1 = db.Column(Integer,nullable=False)
    item_b2 = db.Column(Integer,nullable=False)
    item_b3 = db.Column(Integer,nullable=False)
    item_b4 = db.Column(Integer,nullable=False)
    item_b5 = db.Column(Integer,nullable=False)
    item_b6 = db.Column(Integer,nullable=False)
    item_b7 = db.Column(Integer,nullable=False)
    item_b8 = db.Column(Integer,nullable=False)
    item_b9 = db.Column(Integer,nullable=False)
    item_b10 = db.Column(Integer,nullable=False)
    item_b11 = db.Column(Integer,nullable=False)
    item_b12 = db.Column(Integer,nullable=False)
    item_b13 = db.Column(Integer,nullable=False)
    item_b14 = db.Column(Integer,nullable=False)
    item_b15 = db.Column(Integer,nullable=False)
    item_b16 = db.Column(Integer,nullable=False)
    item_b17 = db.Column(Integer,nullable=False)
    item_b18 = db.Column(Integer,nullable=False)
    item_b19 = db.Column(Integer,nullable=False)
    item_b20 = db.Column(Integer,nullable=False)
    item_b21 = db.Column(Integer,nullable=False)
    item_b22 = db.Column(Integer,nullable=False)
    item_b23 = db.Column(Integer,nullable=False)
    item_b24 = db.Column(Integer,nullable=False)
    item_b25 = db.Column(Integer,nullable=False)
    item_b26 = db.Column(Integer,nullable=False)
    item_b27 = db.Column(Integer,nullable=False)
    item_b28 = db.Column(Integer,nullable=False)
    item_b29 = db.Column(Integer,nullable=False)
    item_b30 = db.Column(Integer,nullable=False)
    item_b31 = db.Column(Integer,nullable=False)
    item_b32 = db.Column(Integer,nullable=False)
    item_b33 = db.Column(Integer,nullable=False)
    item_b34 = db.Column(Integer,nullable=False)
    item_b35 = db.Column(Integer,nullable=False)
    item_b36 = db.Column(Integer,nullable=False)
    

class DatosTestVocacional(db.Model, TimestampMixin):
    __tablename__ = 'test_vocacional_datos'

    id = db.Column(Integer,primary_key=True)
    nombre = db.Column(String(length=100), nullable=False)
    cedula = db.Column(Integer, nullable=False)
    sexo = db.Column(String(length=20), nullable=False)
    fecha_nacimiento = db.Column(Date, nullable=False)
    email = db.Column(String(length=100))
    telefono = db.Column(Integer, nullable=True)


class TestONet(db.Model, TimestampMixin):
    __tablename__ = 'test_onet'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    uuid = db.Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    id_user = db.Column(Integer, ForeignKey('test_vocacional_datos.id'))
    zona = db.Column(Integer, nullable=False)
    item_1 = db.Column(Integer,nullable=False)
    item_2 = db.Column(Integer,nullable=False)
    item_3 = db.Column(Integer,nullable=False)
    item_4 = db.Column(Integer,nullable=False)
    item_5 = db.Column(Integer,nullable=False)
    item_6 = db.Column(Integer,nullable=False)
    item_7 = db.Column(Integer,nullable=False)
    item_8 = db.Column(Integer,nullable=False)
    item_9 = db.Column(Integer,nullable=False)
    item_10 = db.Column(Integer,nullable=False)
    item_11 = db.Column(Integer,nullable=False)
    item_12 = db.Column(Integer,nullable=False)
    item_13 = db.Column(Integer,nullable=False)
    item_14 = db.Column(Integer,nullable=False)
    item_15 = db.Column(Integer,nullable=False)
    item_16 = db.Column(Integer,nullable=False)
    item_17 = db.Column(Integer,nullable=False)
    item_18 = db.Column(Integer,nullable=False)
    item_19 = db.Column(Integer,nullable=False)
    item_20 = db.Column(Integer,nullable=False)
    item_21 = db.Column(Integer,nullable=False)
    item_22 = db.Column(Integer,nullable=False)
    item_23 = db.Column(Integer,nullable=False)
    item_24 = db.Column(Integer,nullable=False)
    item_25 = db.Column(Integer,nullable=False)
    item_26 = db.Column(Integer,nullable=False)
    item_27 = db.Column(Integer,nullable=False)
    item_28 = db.Column(Integer,nullable=False)
    item_29 = db.Column(Integer,nullable=False)
    item_30 = db.Column(Integer,nullable=False)
    item_31 = db.Column(Integer,nullable=False)
    item_32 = db.Column(Integer,nullable=False)
    item_33 = db.Column(Integer,nullable=False)
    item_34 = db.Column(Integer,nullable=False)
    item_35 = db.Column(Integer,nullable=False)
    item_36 = db.Column(Integer,nullable=False)
    item_37 = db.Column(Integer,nullable=False)
    item_38 = db.Column(Integer,nullable=False)
    item_39 = db.Column(Integer,nullable=False)
    item_40 = db.Column(Integer,nullable=False)
    item_41 = db.Column(Integer,nullable=False)
    item_42 = db.Column(Integer,nullable=False)
    item_43 = db.Column(Integer,nullable=False)
    item_44 = db.Column(Integer,nullable=False)
    item_45 = db.Column(Integer,nullable=False)
    item_46 = db.Column(Integer,nullable=False)
    item_47 = db.Column(Integer,nullable=False)
    item_48 = db.Column(Integer,nullable=False)
    item_49 = db.Column(Integer,nullable=False)
    item_50 = db.Column(Integer,nullable=False)
    item_51 = db.Column(Integer,nullable=False)
    item_52 = db.Column(Integer,nullable=False)
    item_53 = db.Column(Integer,nullable=False)
    item_54 = db.Column(Integer,nullable=False)
    item_55 = db.Column(Integer,nullable=False)
    item_56 = db.Column(Integer,nullable=False)
    item_57 = db.Column(Integer,nullable=False)
    item_58 = db.Column(Integer,nullable=False)
    item_59 = db.Column(Integer,nullable=False)
    item_60 = db.Column(Integer,nullable=False)


class TestNeoPIR(db.Model, TimestampMixin):
    __tablename__ = 'test_neo_pir'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    uuid = db.Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    id_user = db.Column(Integer, ForeignKey('test_vocacional_datos.id'))
    item_1 = db.Column(Integer,nullable=False)
    item_2 = db.Column(Integer,nullable=False)
    item_3 = db.Column(Integer,nullable=False)
    item_4 = db.Column(Integer,nullable=False)
    item_5 = db.Column(Integer,nullable=False)
    item_6 = db.Column(Integer,nullable=False)
    item_7 = db.Column(Integer,nullable=False)
    item_8 = db.Column(Integer,nullable=False)
    item_9 = db.Column(Integer,nullable=False)
    item_10 = db.Column(Integer,nullable=False)
    item_11 = db.Column(Integer,nullable=False)
    item_12 = db.Column(Integer,nullable=False)
    item_13 = db.Column(Integer,nullable=False)
    item_14 = db.Column(Integer,nullable=False)
    item_15 = db.Column(Integer,nullable=False)
    item_16 = db.Column(Integer,nullable=False)
    item_17 = db.Column(Integer,nullable=False)
    item_18 = db.Column(Integer,nullable=False)
    item_19 = db.Column(Integer,nullable=False)
    item_20 = db.Column(Integer,nullable=False)
    item_21 = db.Column(Integer,nullable=False)
    item_22 = db.Column(Integer,nullable=False)
    item_23 = db.Column(Integer,nullable=False)
    item_24 = db.Column(Integer,nullable=False)
    item_25 = db.Column(Integer,nullable=False)
    item_26 = db.Column(Integer,nullable=False)
    item_27 = db.Column(Integer,nullable=False)
    item_28 = db.Column(Integer,nullable=False)
    item_29 = db.Column(Integer,nullable=False)
    item_30 = db.Column(Integer,nullable=False)
    item_31 = db.Column(Integer,nullable=False)
    item_32 = db.Column(Integer,nullable=False)
    item_33 = db.Column(Integer,nullable=False)
    item_34 = db.Column(Integer,nullable=False)
    item_35 = db.Column(Integer,nullable=False)
    item_36 = db.Column(Integer,nullable=False)
    item_37 = db.Column(Integer,nullable=False)
    item_38 = db.Column(Integer,nullable=False)
    item_39 = db.Column(Integer,nullable=False)
    item_40 = db.Column(Integer,nullable=False)
    item_41 = db.Column(Integer,nullable=False)
    item_42 = db.Column(Integer,nullable=False)
    item_43 = db.Column(Integer,nullable=False)
    item_44 = db.Column(Integer,nullable=False)
    item_45 = db.Column(Integer,nullable=False)
    item_46 = db.Column(Integer,nullable=False)
    item_47 = db.Column(Integer,nullable=False)
    item_48 = db.Column(Integer,nullable=False)
    item_49 = db.Column(Integer,nullable=False)
    item_50 = db.Column(Integer,nullable=False)
    item_51 = db.Column(Integer,nullable=False)
    item_52 = db.Column(Integer,nullable=False)
    item_53 = db.Column(Integer,nullable=False)
    item_54 = db.Column(Integer,nullable=False)
    item_55 = db.Column(Integer,nullable=False)
    item_56 = db.Column(Integer,nullable=False)
    item_57 = db.Column(Integer,nullable=False)
    item_58 = db.Column(Integer,nullable=False)
    item_59 = db.Column(Integer,nullable=False)
    item_60 = db.Column(Integer,nullable=False)
    item_61 = db.Column(Integer,nullable=False)
    item_62 = db.Column(Integer,nullable=False)
    item_63 = db.Column(Integer,nullable=False)
    item_64 = db.Column(Integer,nullable=False)
    item_65 = db.Column(Integer,nullable=False)
    item_66 = db.Column(Integer,nullable=False)
    item_67 = db.Column(Integer,nullable=False)
    item_68 = db.Column(Integer,nullable=False)
    item_69 = db.Column(Integer,nullable=False)
    item_70 = db.Column(Integer,nullable=False)
    item_71 = db.Column(Integer,nullable=False)
    item_72 = db.Column(Integer,nullable=False)
    item_73 = db.Column(Integer,nullable=False)
    item_74 = db.Column(Integer,nullable=False)
    item_75 = db.Column(Integer,nullable=False)
    item_76 = db.Column(Integer,nullable=False)
    item_77 = db.Column(Integer,nullable=False)
    item_78 = db.Column(Integer,nullable=False)
    item_79 = db.Column(Integer,nullable=False)
    item_80 = db.Column(Integer,nullable=False)
    item_81 = db.Column(Integer,nullable=False)
    item_82 = db.Column(Integer,nullable=False)
    item_83 = db.Column(Integer,nullable=False)
    item_84 = db.Column(Integer,nullable=False)
    item_85 = db.Column(Integer,nullable=False)
    item_86 = db.Column(Integer,nullable=False)
    item_87 = db.Column(Integer,nullable=False)
    item_88 = db.Column(Integer,nullable=False)
    item_89 = db.Column(Integer,nullable=False)
    item_90 = db.Column(Integer,nullable=False)
    item_91 = db.Column(Integer,nullable=False)
    item_92 = db.Column(Integer,nullable=False)
    item_93 = db.Column(Integer,nullable=False)
    item_94 = db.Column(Integer,nullable=False)
    item_95 = db.Column(Integer,nullable=False)
    item_96 = db.Column(Integer,nullable=False)
    item_97 = db.Column(Integer,nullable=False)
    item_98 = db.Column(Integer,nullable=False)
    item_99 = db.Column(Integer,nullable=False)
    item_100 = db.Column(Integer,nullable=False)
    item_101 = db.Column(Integer,nullable=False)
    item_102 = db.Column(Integer,nullable=False)
    item_103 = db.Column(Integer,nullable=False)
    item_104 = db.Column(Integer,nullable=False)
    item_105 = db.Column(Integer,nullable=False)
    item_106 = db.Column(Integer,nullable=False)
    item_107 = db.Column(Integer,nullable=False)
    item_108 = db.Column(Integer,nullable=False)
    item_109 = db.Column(Integer,nullable=False)
    item_110 = db.Column(Integer,nullable=False)
    item_111 = db.Column(Integer,nullable=False)
    item_112 = db.Column(Integer,nullable=False)
    item_113 = db.Column(Integer,nullable=False)
    item_114 = db.Column(Integer,nullable=False)
    item_115 = db.Column(Integer,nullable=False)
    item_116 = db.Column(Integer,nullable=False)
    item_117 = db.Column(Integer,nullable=False)
    item_118 = db.Column(Integer,nullable=False)
    item_119 = db.Column(Integer,nullable=False)
    item_120 = db.Column(Integer,nullable=False)
    item_121 = db.Column(Integer,nullable=False)
    item_122 = db.Column(Integer,nullable=False)
    item_123 = db.Column(Integer,nullable=False)
    item_124 = db.Column(Integer,nullable=False)
    item_125 = db.Column(Integer,nullable=False)
    item_126 = db.Column(Integer,nullable=False)
    item_127 = db.Column(Integer,nullable=False)
    item_128 = db.Column(Integer,nullable=False)
    item_129 = db.Column(Integer,nullable=False)
    item_130 = db.Column(Integer,nullable=False)
    item_131 = db.Column(Integer,nullable=False)
    item_132 = db.Column(Integer,nullable=False)
    item_133 = db.Column(Integer,nullable=False)
    item_134 = db.Column(Integer,nullable=False)
    item_135 = db.Column(Integer,nullable=False)
    item_136 = db.Column(Integer,nullable=False)
    item_137 = db.Column(Integer,nullable=False)
    item_138 = db.Column(Integer,nullable=False)
    item_139 = db.Column(Integer,nullable=False)
    item_140 = db.Column(Integer,nullable=False)
    item_141 = db.Column(Integer,nullable=False)
    item_142 = db.Column(Integer,nullable=False)
    item_143 = db.Column(Integer,nullable=False)
    item_144 = db.Column(Integer,nullable=False)
    item_145 = db.Column(Integer,nullable=False)
    item_146 = db.Column(Integer,nullable=False)
    item_147 = db.Column(Integer,nullable=False)
    item_148 = db.Column(Integer,nullable=False)
    item_149 = db.Column(Integer,nullable=False)
    item_150 = db.Column(Integer,nullable=False)
    item_151 = db.Column(Integer,nullable=False)
    item_152 = db.Column(Integer,nullable=False)
    item_153 = db.Column(Integer,nullable=False)
    item_154 = db.Column(Integer,nullable=False)
    item_155 = db.Column(Integer,nullable=False)
    item_156 = db.Column(Integer,nullable=False)
    item_157 = db.Column(Integer,nullable=False)
    item_158 = db.Column(Integer,nullable=False)
    item_159 = db.Column(Integer,nullable=False)
    item_160 = db.Column(Integer,nullable=False)
    item_161 = db.Column(Integer,nullable=False)
    item_162 = db.Column(Integer,nullable=False)
    item_163 = db.Column(Integer,nullable=False)
    item_164 = db.Column(Integer,nullable=False)
    item_165 = db.Column(Integer,nullable=False)
    item_166 = db.Column(Integer,nullable=False)
    item_167 = db.Column(Integer,nullable=False)
    item_168 = db.Column(Integer,nullable=False)
    item_169 = db.Column(Integer,nullable=False)
    item_170 = db.Column(Integer,nullable=False)
    item_171 = db.Column(Integer,nullable=False)
    item_172 = db.Column(Integer,nullable=False)
    item_173 = db.Column(Integer,nullable=False)
    item_174 = db.Column(Integer,nullable=False)
    item_175 = db.Column(Integer,nullable=False)
    item_176 = db.Column(Integer,nullable=False)
    item_177 = db.Column(Integer,nullable=False)
    item_178 = db.Column(Integer,nullable=False)
    item_179 = db.Column(Integer,nullable=False)
    item_180 = db.Column(Integer,nullable=False)
    item_181 = db.Column(Integer,nullable=False)
    item_182 = db.Column(Integer,nullable=False)
    item_183 = db.Column(Integer,nullable=False)
    item_184 = db.Column(Integer,nullable=False)
    item_185 = db.Column(Integer,nullable=False)
    item_186 = db.Column(Integer,nullable=False)
    item_187 = db.Column(Integer,nullable=False)
    item_188 = db.Column(Integer,nullable=False)
    item_189 = db.Column(Integer,nullable=False)
    item_190 = db.Column(Integer,nullable=False)
    item_191 = db.Column(Integer,nullable=False)
    item_192 = db.Column(Integer,nullable=False)
    item_193 = db.Column(Integer,nullable=False)
    item_194 = db.Column(Integer,nullable=False)
    item_195 = db.Column(Integer,nullable=False)
    item_196 = db.Column(Integer,nullable=False)
    item_197 = db.Column(Integer,nullable=False)
    item_198 = db.Column(Integer,nullable=False)
    item_199 = db.Column(Integer,nullable=False)
    item_200 = db.Column(Integer,nullable=False)
    item_201 = db.Column(Integer,nullable=False)
    item_202 = db.Column(Integer,nullable=False)
    item_203 = db.Column(Integer,nullable=False)
    item_204 = db.Column(Integer,nullable=False)
    item_205 = db.Column(Integer,nullable=False)
    item_206 = db.Column(Integer,nullable=False)
    item_207 = db.Column(Integer,nullable=False)
    item_208 = db.Column(Integer,nullable=False)
    item_209 = db.Column(Integer,nullable=False)
    item_210 = db.Column(Integer,nullable=False)
    item_211 = db.Column(Integer,nullable=False)
    item_212 = db.Column(Integer,nullable=False)
    item_213 = db.Column(Integer,nullable=False)
    item_214 = db.Column(Integer,nullable=False)
    item_215 = db.Column(Integer,nullable=False)
    item_216 = db.Column(Integer,nullable=False)
    item_217 = db.Column(Integer,nullable=False)
    item_218 = db.Column(Integer,nullable=False)
    item_219 = db.Column(Integer,nullable=False)
    item_220 = db.Column(Integer,nullable=False)
    item_221 = db.Column(Integer,nullable=False)
    item_222 = db.Column(Integer,nullable=False)
    item_223 = db.Column(Integer,nullable=False)
    item_224 = db.Column(Integer,nullable=False)
    item_225 = db.Column(Integer,nullable=False)
    item_226 = db.Column(Integer,nullable=False)
    item_227 = db.Column(Integer,nullable=False)
    item_228 = db.Column(Integer,nullable=False)
    item_229 = db.Column(Integer,nullable=False)
    item_230 = db.Column(Integer,nullable=False)
    item_231 = db.Column(Integer,nullable=False)
    item_232 = db.Column(Integer,nullable=False)
    item_233 = db.Column(Integer,nullable=False)
    item_234 = db.Column(Integer,nullable=False)
    item_235 = db.Column(Integer,nullable=False)
    item_236 = db.Column(Integer,nullable=False)
    item_237 = db.Column(Integer,nullable=False)
    item_238 = db.Column(Integer,nullable=False)
    item_239 = db.Column(Integer,nullable=False)
    item_240 = db.Column(Integer,nullable=False)

class TestRokeach(db.Model,TimestampMixin):
    __tablename__ = 'test_rokeach'
    __table_args__ = {'extend_existing': True}
    id = db.Column(Integer,primary_key=True)
    uuid = db.Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    id_user = db.Column(Integer, ForeignKey('test_vocacional_datos.id'))
    item_1 = db.Column(Integer,nullable=False)
    item_2 = db.Column(Integer,nullable=False)
    item_3 = db.Column(Integer,nullable=False)
    item_4 = db.Column(Integer,nullable=False)
    item_5 = db.Column(Integer,nullable=False)
    item_6 = db.Column(Integer,nullable=False)
    item_7 = db.Column(Integer,nullable=False)
    item_8 = db.Column(Integer,nullable=False)
    item_9 = db.Column(Integer,nullable=False)
    item_10 = db.Column(Integer,nullable=False)
    item_11 = db.Column(Integer,nullable=False)
    item_12 = db.Column(Integer,nullable=False)
    item_13 = db.Column(Integer,nullable=False)
    item_14 = db.Column(Integer,nullable=False)
    item_15 = db.Column(Integer,nullable=False)
    item_16 = db.Column(Integer,nullable=False)
    item_17 = db.Column(Integer,nullable=False)
    item_18 = db.Column(Integer,nullable=False)
    item_19 = db.Column(Integer,nullable=False)
    item_20 = db.Column(Integer,nullable=False)
    item_21 = db.Column(Integer,nullable=False)
    item_22 = db.Column(Integer,nullable=False)
    item_23 = db.Column(Integer,nullable=False)
    item_24 = db.Column(Integer,nullable=False)
    item_25 = db.Column(Integer,nullable=False)
    item_26 = db.Column(Integer,nullable=False)
    item_27 = db.Column(Integer,nullable=False)
    item_28 = db.Column(Integer,nullable=False)
    item_29 = db.Column(Integer,nullable=False)
    item_30 = db.Column(Integer,nullable=False)
    item_31 = db.Column(Integer,nullable=False)
    item_32 = db.Column(Integer,nullable=False)
    item_33 = db.Column(Integer,nullable=False)
    item_34 = db.Column(Integer,nullable=False)
    item_35 = db.Column(Integer,nullable=False)
    item_36 = db.Column(Integer,nullable=False)

    
