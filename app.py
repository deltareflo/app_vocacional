import datetime
from smtplib import SMTPAuthenticationError, SMTPException, SMTPServerDisconnected
from flask_weasyprint import render_pdf, HTML
from flask import Flask, make_response, render_template, request, redirect, url_for, abort,flash
import pandas as pd
from werkzeug.urls import url_parse

from config import DeveloperConfig
from models import Usuarios, db, SegUser, ContactoSegUser, ConsultaSegUser, EvalSegUser, EvaluacionTipo, \
    ResultadoSegUser, Tipo, AcompSegUser, InfoSeg, InformeSegUser, Profesionales, ArchivoEnviado, \
        DatosRavenGeneral, TestRavenGeneral, TestRavenAvanzado, DatosTestVocacional, TestRokeach, TestNeoPIR, TestONet
from dataframe_all import dataframe_p1, cambio_baremo_one_p1, p1_dict_one, dataframe_p2, cambio_baremo_one_p2, \
    dataframe_p3, dataframe_s3, cambio_baremo_one_s3, cambio_baremo_one_p3, dataframe_s2, cambio_baremo_one_s2, \
        valores_neo
from rist_raven import info_test, carga_datos_Raven_gral,carga_datos_Raven_avanzadas, carga_archivo_enviado
from vocacional import carga_vocacional
from forms import EnvioMailForm, SignupForm, LoginForm, ContactoForm, SegForm, ConsultaForm, EvalForm, EvalTipoForm, ResultadoForm, \
    TipoAcompForm, AcompForm, InfoForm, ProfeForm, RavenGral, CustomTestForm, TestItemForm, ResetPasswordForm, ResetPasswordRequestForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from decorators import admin_required
from sqlalchemy import desc
from flask_mail import Mail, Message
#from send_whatsapp import envia_what
import io
import uuid
#para whatsapp
"""import webbrowser
import pyautogui
import time
import pyperclip"""

def insert_contacto():
    pass


app = Flask(__name__)

app.config.from_object(DeveloperConfig)
login_manager = LoginManager(app)
login_manager.login_view = "login"
mail = Mail(app)

db.app = app
db.init_app(app)


#df1 = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5NCVPoep7GUF5rFwqZ6jcaP84OVob42xcJjaBwo6YmWJM3MT89QmQaavTSo3Eqoi8cgsM1dOPv0S/pub?output=csv")
#df1= dataframe_p1()
"""df_2 = dataframe_p2()
df_3 = dataframe_p3()
df_s3 = dataframe_s3()
df_s2 = dataframe_s2()"""



@app.errorhandler(404)
def page_not_found(error):
    respuesta = error.description
    return render_template('404.html', respuesta=respuesta), 404


@app.errorhandler(500)
def internal_error(error):
    respuesta = error.description
    return render_template('500.html', respuesta=respuesta), 500


@app.errorhandler(401)
def internal_error(error):
    respuesta = error.description
    return render_template('401.html', respuesta=respuesta), 401


@login_manager.user_loader
def load_user(user_id):
    return Usuarios.get_by_id(int(user_id))


@app.route('/')
@login_required
def inicio():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')

    query = db.session.query(TestONet, DatosTestVocacional).join(DatosTestVocacional, TestONet.id_user == DatosTestVocacional.id)

    if search_query:
        query = query.filter(
            (DatosTestVocacional.nombre.ilike(f'%{search_query}%')) |
            (DatosTestVocacional.cedula.ilike(f'%{search_query}%'))
        )

    # Order by creation date in descending order
    query = query.order_by(desc(TestONet.created))

    # Paginate results
    per_page = 10  # Number of results per page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for onet_test, personal_data in pagination.items:
        neo_test = TestNeoPIR.query.filter_by(uuid=onet_test.uuid).first()
        rokeach_test = TestRokeach.query.filter_by(uuid=onet_test.uuid).first()

        results.append({
            'personal_data': personal_data,
            'onet_test': onet_test,
            'neo_test': neo_test,
            'rokeach_test': rokeach_test
        })

    return render_template('test_results.html', results=results, pagination=pagination, search_query=search_query)


@app.route('/archivos-enviados-total')
@login_required
def archivos_enviados_total():
    df = carga_archivo_enviado()
    
    df['Fecha envio'] = df.loc[:, 'created']
    df = df.loc[:,['id', 'Fecha envio', 'cedula', 'mail', 'telefono', 'metodo', 'test' ]]
    columns = df.columns.values
    datos = list(df.values.tolist())
    return render_template('archivos_enviados.html',
                           datos= datos,
                           columns=columns)



@app.route('/registro-success', methods=['GET'])
def registro_correcto():
    return render_template("registro-success.html")

@app.route('/add-vocacional-test', methods=['GET', 'POST'])
def add_vocacional_test():
    form = CustomTestForm()
    listItemOneTest = ['Construir gabinetes para cocinas','Colocar ladrillos o losetas','Elaborar nueva medicina','Estudiar maneras para reducir la contaminación del agua','Escribir libros u obras de teatro','Tocar un instrumento musical','Enseñar a una persona un ejercicio de rutina','Ayudar a personas con problemas personales o emocionales','Comprar y vender acciones y bonos','Administrar una tienda de venta al por menor o menudeo','Desarrollar una hoja de cálculo utilizando software','Revisar y corregir errores en registros o formularios','Reparar electrodomésticos','Criar peces en un criadero de peces','Realizar experimentos químicos','Estudiar los movimientos de los planetas','Componer y hacer arreglos musicales','Hacer dibujos','Orientar a las personas sobre carreras','Realizar terapia de rehabilitación','Administrar un salón de belleza o barbería','Administrar un departamento en una compañía grande','Instala software en las computadoras en una gran red','Operar una calculadora','Ensamblar partes electrónicas','Manejar un camión para entregar paquetes a oficinas y hogares','Examinar muestras de sangre con el uso de un microscopio','Investigar las causas de un incendio','Crear efectos especiales para películas','Pintar escenografías para obras de teatro','Hacer trabajo voluntario en organizaciones sin fines de lucro','Enseñar a niños cómo jugar deportes','Comenzar su propio negocio','Negociar contratos comerciales','Mantener registros de envíos y recepción','Calcular los salarios de los empleados','Probar la calidad de las partes antes de un envío','Reparar e instalar cerraduras','Desarrollar una mejor manera de predecir el estado del tiempo o clima','Trabajar en un laboratorio de biología','Escribir libretos para películas o programas de televisión','Realizar un baile de jazz o tap','Enseñar lenguaje por señas a personas que son sordas o tienen problemas de audición','Ayudar a realizar sesiones de terapia de grupo','Representar a un cliente en una demanda','Comercializar una nueva línea de ropa','Identificar el inventario de suministros con una computadora de mano','Llevar registros de pagos de renta','Montar y operar máquinas para la elaboración de productos','Apagar fuegos forestales','Inventar un substituto de azúcar','Hacer pruebas de laboratorio para identificar enfermedades','Cantar en una banda o grupo','Editar películas','Cuidar niños en un centro de cuidado infantil','Enseñar una clase de high school','Vender mercancía en una tienda por departamentos','Administrar una tienda de ropa','Mantener registros de inventarios','Colocar sellos, separar y repartir correo para una organización']
    listItemNeoTest = ['Aplicar técnicas de programación','Resolver problemas de software','Desarrollar software a medida','Colaborar en proyectos de software','Diseñar interfaces de usuario','Desarrollar aplicaciones móviles','Administrar bases de datos','Mantener registros de cambios en el software','Realizar pruebas de software','Manejar herramientas de control de versiones','Administrar proyectos de software','Trabajar en equipo para desarrollar software','Desarrollar software para diferentes plataformas','Mantener registros de errores y problemas en el software','Colaborar en la documentación técnica del software','Trabajar en proyectos de software para empresas','Desarrollar software para satisfacer necesidades específicas','Mantener registros de cambios en el software','Realizar pruebas de software'] 
    listItemRokeTest = ['Amor maduro (intimidad sexual y espiritual)','Armonía interna (ausencia de conflictos internos)','Auténtica amistad (compañerismo)','Felicidad (satisfacción personal)','Igualdad (fraternidad, igualdad de oportunidades para todos)','Libertad (independencia, libre elección)','Placer (una vida agradable, de ocio)','Reconocimiento social (respeto, admiración)','Respeto por uno mismo (autoestima)','Sabiduría (una comprensión madura de la vida)','Salvación (vida eterna, salvado)','Seguridad familiar(cuidar de los seres queridos)','Seguridad nacional (protección ante ataques)','Sentimiento de realización (contribución duradera)','Un mundo bello (la belleza de la naturaleza y las artes)','Un mundo pacífico (sin guerras ni conflictos)','Una vida cómoda (una vida próspera)','Una vida excitante (una vida estimulante, activa)']
    listItemRoke2Test = ['Alegre (despreocupado, jubiloso)','Amante (afectivo, tierno)','Ambicioso (trabaja duro, tiene ambiciones)','Capaz (competente, eficiente)','Clemente (dispuesto a perdonar a los demás)','Con auto-control (comedido, con disciplina propia)','Cortés (bien educado, con buenas maneras)','Honesto (sincero, honrado)','Imaginativo (atrevido, creativo)','Independiente (depende de sí mismo, autosuficiente)','Intelectual (inteligente, reflexivo)','Limpio (aseado, ordenado)','Lógico (coherente, racional)','Mentalidad abierta (abierto a nuevas ideas)','Obediente (dedicado, respetuoso)','Responsable (fiable, cumplidor)','Servicial (se refuerza por el bienestar de los demás)','Valiente (defiende sus creencias)']
    # Populate test2_items dynamically for GET requests
    #if request.method == 'GET':
        #for _ in range(8):
        #form.test2_items.append_entry()

    if request.method == "POST":
        # Process personal data

        # Process Test 1 data (manual validation in HTML/JS)
        test1_results = {}
        for i in range(1, 11):
            test1_results[f'item{i}'] = request.form.get(f'test1_item{i}', type=int)

        # Process Test 3 data (JS validation in HTML)
        # Generate a single UUID for all tests related to this submission
        
        submission_uuid = str(uuid.uuid4())

        # Process Personal Data and save to TestVocacionalDatos
        # Convert fecha_nacimiento (string from input type=date) to a date object
        fecha_nac_str = request.form.get('fecha_nacimiento')
        fecha_nac_obj = None
        if fecha_nac_str:
            try:
                # HTML date input uses YYYY-MM-DD
                fecha_nac_obj = datetime.date.fromisoformat(fecha_nac_str)
            except Exception:
                # fallback parse
                try:
                    fecha_nac_obj = datetime.datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                except Exception:
                    fecha_nac_obj = None

        new_personal_data = DatosTestVocacional(
            nombre=request.form.get('nombre'),
            sexo=request.form.get('sexo'),
            cedula=request.form.get('cedula'),
            fecha_nacimiento=fecha_nac_obj,
            email=request.form.get('email'),
            telefono=request.form.get('telefono')
        )
        db.session.add(new_personal_data)
        db.session.flush() # To get the ID of the new_personal_data object

        # Process Test 1 (O NET) data and save
        zona = request.form.get('zona')
        onet_data = {'id_user': new_personal_data.id, 'uuid': submission_uuid, 'zona': zona}
        for i in range(1, 61):
            onet_data[f'item_{i}'] = request.form.get(f'test1_item{i}', type=int)
        new_onet_test = TestONet(**onet_data)
        db.session.add(new_onet_test)

        # Process Test 2 (NEO-PI-R) data and save
        neo_data = {'id_user': new_personal_data.id, 'uuid': submission_uuid}
        for i in range(1, 241):
            neo_data[f'item_{i}'] = request.form.get(f'test2_item{i}', type=int)
        new_neo_test = TestNeoPIR(**neo_data)
        db.session.add(new_neo_test)

        # Process Test 3 (Rokeach) data and save
        rokeach_data = {'id_user': new_personal_data.id, 'uuid': submission_uuid}
        for test_num in range(1, 3):
            for option_num in range(1, 19):
                key = f'test3_item{test_num}_option{option_num}'
                rokeach_data[f'item_{((test_num-1)*18)+option_num}'] = request.form.get(key, type=int,default=0)
        new_rokeach_test = TestRokeach(**rokeach_data)
        db.session.add(new_rokeach_test)

        db.session.commit()

        flash('Test personalizado guardado exitosamente!', 'success')
        return redirect(url_for('registro_correcto'))

    #listItemRokeTest = ["Paz mundial", "Armonía interior", "Igualdad", "Libertad", "Felicidad", "Seguridad familiar", "Sabiduría", "Amistad verdadera", "Madurez amorosa", "Reconocimiento social", "Belleza del mundo", "Vida emocionante", "Seguridad nacional", "Salvación", "Auto-respeto", "Un mundo de belleza", "Una vida cómoda", "Una vida excitante"]
    #listItemRoke2Test = ["Ambicioso", "De mente abierta", "Capaz", "Alegre", "Limpio", "Valiente", "Perdonador", "Servicial", "Honesto", "Imaginativo", "Independiente", "Intelectual", "Lógico", "Amoroso", "Obediente", "Pulcro", "Educado", "Responsable"]
    return render_template('add_test_custom.html', form=form, listItemOneTest=listItemOneTest, listItemNeoTest=valores_neo, listItemRokeTest=listItemRokeTest, listItemRoke2Test=listItemRoke2Test)
        

@app.route('/test-results', methods=['GET'])
@login_required
def show_vocacional_results():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')

    query = db.session.query(TestONet, DatosTestVocacional).join(DatosTestVocacional, TestONet.id_user == DatosTestVocacional.id)

    if search_query:
        query = query.filter(
            (DatosTestVocacional.nombre.ilike(f'%{search_query}%')) |
            (DatosTestVocacional.cedula.ilike(f'%{search_query}%'))
        )

    # Order by creation date in descending order
    query = query.order_by(desc(TestONet.created))

    # Paginate results
    per_page = 10  # Number of results per page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for onet_test, personal_data in pagination.items:
        neo_test = TestNeoPIR.query.filter_by(uuid=onet_test.uuid).first()
        rokeach_test = TestRokeach.query.filter_by(uuid=onet_test.uuid).first()

        results.append({
            'personal_data': personal_data,
            'onet_test': onet_test,
            'neo_test': neo_test,
            'rokeach_test': rokeach_test
        })

    return render_template('test_results.html', results=results, pagination=pagination, search_query=search_query)


@app.route('/informe-vocacional/<string:r1_id>', methods=['GET'])
@login_required
def informe_vocacional(r1_id):
    df_info,df_onet,df_neopi,df_rokeach, grafico_onet, graf_neo_dimen, graf_neo_sub = carga_vocacional(r1_id)
    df_neopi.columns = df_neopi.columns.str.replace(" ", "_")
    df_onet.columns = df_onet.columns.str.replace(" ", "_")
    df_rokeach.columns = df_rokeach.columns.str.replace(" ", "_")
    
    context = []
    context.append({"grafico_onet": grafico_onet, "graf_neo_dimen": graf_neo_dimen, "graf_neo_sub": graf_neo_sub,
                    
                    "datos_info":df_info, "datos_neo":df_neopi, "datos_onet":df_onet, "datos_rokeach":df_rokeach})

    return render_template('informe_test_vocacional.html',context=context)


@app.route('/informe-vocacional-download/<string:r1_id>', methods=['GET'])
@login_required
def informe_vocacional_download(r1_id):
    """Vista que muestra un botón para descargar el PDF del informe usando JS (FileSaver.js + fetch).
    Esta vista no genera el PDF en el servidor — reutiliza la ruta `/informe-vocacional-export/<r1_id>`.
    """
    # Obtener algunos datos para mostrar (nombre, miniatura) en la vista
    df_info,df_onet,df_neopi,df_rokeach, grafico_onet, graf_neo_dimen, graf_neo_sub = carga_vocacional(r1_id)
    # intentar extraer nombre para mostrar en la página
    try:
        nombre = df_info['nombre'].values.tolist()[0]
    except Exception:
        nombre = None

    return render_template('informe_vocacional_download.html', r1_id=r1_id, nombre=nombre, grafico_onet=grafico_onet)


@app.route('/informe-vocacional-pdf/<string:r1_id>', methods=['GET'])
def informe_vocacional_for_pdf(r1_id):
    df_info,df_onet,df_neopi,df_rokeach, grafico_onet, graf_neo_dimen, graf_neo_sub = carga_vocacional(r1_id)
    df_neopi.columns = df_neopi.columns.str.replace(" ", "_")
    df_onet.columns = df_onet.columns.str.replace(" ", "_")
    df_rokeach.columns = df_rokeach.columns.str.replace(" ", "_")
    
    context = []
    context.append({"grafico_onet": grafico_onet, "graf_neo_dimen": graf_neo_dimen, "graf_neo_sub": graf_neo_sub,
                    
                    "datos_info":df_info, "datos_neo":df_neopi, "datos_onet":df_onet, "datos_rokeach":df_rokeach})

    return render_template('informe_test_vocacional_pdf.html',context=context)


@app.route('/informe-vocacional-export/<string:r1_id>', methods=['GET'])
@login_required
def informe_vocacional_export(r1_id):
    """Exporta a PDF la misma vista que se muestra en pantalla (informe_test_vocacional.html)
    preservando los estilos CSS. Devuelve el PDF como descarga.
    """
    inicio = datetime.datetime.now()
    print(f"Iniciando generación de PDF: {inicio}")
    # Generar los mismos objetos que la vista HTML
    df_info,df_onet,df_neopi,df_rokeach, grafico_onet, graf_neo_dimen, graf_neo_sub = carga_vocacional(r1_id)
    print(f"Datos cargados: {datetime.datetime.now() - inicio}")
    df_neopi.columns = df_neopi.columns.str.replace(" ", "_")
    df_onet.columns = df_onet.columns.str.replace(" ", "_")
    df_rokeach.columns = df_rokeach.columns.str.replace(" ", "_")
    print(f"Columnas renombradas: {datetime.datetime.now() - inicio}")
    context = []
    context.append({"grafico_onet": grafico_onet, "graf_neo_dimen": graf_neo_dimen, "graf_neo_sub": graf_neo_sub,
                    "datos_info":df_info, "datos_neo":df_neopi, "datos_onet":df_onet, "datos_rokeach":df_rokeach})

    # Renderizar el HTML usando la plantilla que se ve en pantalla
    html = render_template('informe_test_vocacional_pdf.html', context=context)
    print(f"HTML renderizado: {datetime.datetime.now() - inicio}")
    # Estilos: incluir el css local de bootstrap y una copia remota por seguridad
    file_css = 'static/plugins/bootstrap/css/bootstrap.min.css'
    stylesheets = [file_css, "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"]

    # Generar el PDF
    pdf_response = render_pdf(HTML(string=html), stylesheets=stylesheets)
    print(f"PDF generado: {datetime.datetime.now() - inicio}")
    # Intentar obtener un nombre para el archivo desde los datos, si es posible
    try:
        nombre = df_info['nombre'].values.tolist()[0]
        filename = f"{nombre}.pdf"
    except Exception:
        filename = f"informe_vocacional_{r1_id}.pdf"

    # Forzar descarga con un filename amigable
    pdf_response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return pdf_response


@app.route('/vocacional-pdf/<string:r1_id>')
def informe_vocacional_pdf(r1_id):
    #df_info,df_onet,df_neopi,df_rokeach, grafico_onet, graf_neo_dimen, graf_neo_sub = carga_vocacional(r1_id)
    query = db.session.query(TestONet, DatosTestVocacional).join(DatosTestVocacional, TestONet.id_user == DatosTestVocacional.id).filter(TestONet.uuid == r1_id).first()
    nombre = query.DatosTestVocacional.nombre
    name = ["Test vocacional"]
    file_css = 'static/plugins/bootstrap/css/bootstrap.min.css'
    inicio = datetime.datetime.now()
    print(f"Iniciando generación de PDF: {inicio}")
    pdf = HTML(url_for('informe_vocacional_for_pdf', r1_id=r1_id)).write_pdf(stylesheets=[file_css, "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"])
    print(f"PDF generado: {datetime.datetime.now() - inicio}")
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={nombre}.pdf'
    return response


@app.route('/raven-gral-excel')
def informe_raven_excel():
    try:
        df1= carga_datos_Raven_gral(0,True)

    except:
        abort(404,"Revisar el formulario del Raven General")
    
     # Creating output and writer (pandas excel writer)
    
    df1 = df1.loc[df1['Pc General'] >= 90]
    df1.sort_values(['Institución', 'Curso', 'Sección', 'Pc General','Nombre'], ascending=[True,True,True,False,True], inplace=True)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')

   
    # Export data frame to excel
    df1.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    writer.save()
    writer.close()

   
    # Flask create response 

    response = make_response(out.getvalue())
    response.headers['Content-Type'] = 'application/x-xls'
    response.headers['Content-Disposition'] = f'attachment; filename=datos_raven_general_superior.xlsx'
    return response


@app.route('/raven-avan-excel')
def informe_raven_avan_excel():
    try:
        df1= carga_datos_Raven_avanzadas(0,True)

    except:
        abort(404,"Revisar el formulario del Raven Avanzado")
    
     # Creating output and writer (pandas excel writer)
    
    df1 = df1.loc[df1['Pc Avanzado'] >= 90]
    df1.sort_values(['Institución', 'Curso', 'Sección', 'Pc Avanzado','Nombre'], ascending=[True,True,True,False,True], inplace=True)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')

   
    # Export data frame to excel
    df1.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    writer.save()
    writer.close()

   
    # Flask create response 

    response = make_response(out.getvalue())
    response.headers['Content-Type'] = 'application/x-xls'
    response.headers['Content-Disposition'] = f'attachment; filename=datos_raven_avanzado_superior.xlsx'
    return response


@app.route('/enviar_mail/<int:r1_id>')
def mail_raven_pdf(r1_id):
    try:
        df1= carga_datos_Raven_gral(r1_id)

    except:
        abort(404,"Revisar el formulario del Raven General")

    email_sender = df1.loc[:,'Correo electrónico'].values.tolist()
    nombre = df1.loc[:,'Nombre'].values.tolist()
    user = current_user.email
    cedula = r1_id
    enviados = ArchivoEnviado.query.filter_by(cedula=r1_id).first()
    if not enviados is None:
        if enviados.metodo == 'correo':
            user_sender = Usuarios.get_by_email(enviados.sender)
            if not user_sender is None:
                flash(f'El usuario {user_sender.nombre} ya envío el correo a {email_sender[0]}', 'error')
            else:
                flash(f'Ya fue enviado desde la cuenta de correo {enviados.sender} al correo {email_sender[0]}', 'error')
        elif enviados.metodo != 'correo' and len(email_sender) > 0:
            pdf = HTML(url_for('informe_raven2', r1_id=r1_id)).write_pdf()
            envia_mail(r1_id, nombre, cedula, email_sender, user, pdf)
    elif len(email_sender) > 0 and enviados is None:
        pdf = HTML(url_for('informe_raven2', r1_id=r1_id)).write_pdf()
        envia_mail(r1_id, nombre, cedula, email_sender, user, pdf)
    return redirect(url_for('informe_raven', r1_id=r1_id))


@app.route('/enviar-mail-avan/<int:r1_id>')
def mail_raven_avan_pdf(r1_id):
    try:
        df1= carga_datos_Raven_avanzadas(r1_id)

    except:
        abort(404,"Revisar el formulario del Raven Avanzado")

    email_sender = df1.loc[:,'Correo electrónico'].values.tolist()
    nombre = df1.loc[:,'Nombre'].values.tolist()
    user = current_user.email
    cedula = r1_id
    enviados = ArchivoEnviado.query.filter_by(cedula=r1_id).first()
    if not enviados is None:
        if enviados.metodo == 'correo':
            user_sender = Usuarios.get_by_email(enviados.sender)
            if not user_sender is None:
                flash(f'El usuario {user_sender.nombre} ya envío el correo a {email_sender[0]}', "error")
            else:
                flash(f'Ya fue enviado desde la cuenta de correo {enviados.sender} al correo {email_sender[0]}',"error")
        elif enviados.metodo != 'correo' and len(email_sender) > 0:
            pdf = HTML(url_for('informe_raven_avan2', r1_id=r1_id)).write_pdf()
            envia_mail(r1_id, nombre, cedula, email_sender, user, pdf, "Raven Avanzado")
    elif len(email_sender) > 0 and enviados is None:
        envia_mail(r1_id, nombre, cedula, email_sender, user, "Raven Avanzado")
    return redirect(url_for('informe_raven_avan', r1_id=r1_id))


@app.route('/enviar_whatsapp/<int:r1_id>', methods=['GET', 'POST'])
def what_raven_pdf(r1_id):
    try:
        df1= carga_datos_Raven_gral(r1_id)

    except:
        abort(404,"Revisar el formulario del Raven General")
    test = "Raven General"
    tab = request.form.get('tabulacion', 17)
    tab = int(tab)
    if request.form.get('isReenvio'):
        reenvio = True
    else:
        reenvio = False
    nro_sender = df1.loc[:,'Nro Teléfono'].values.tolist()
    nombre = df1.loc[:,'Info Contacto'].values.tolist()
    nombre_alumno = df1.loc[:,'Nombre'].values.tolist()
    list_pc_gral = df1.loc[:, ['Pc General']].astype(int).values.tolist()
    user = current_user.email
    cedula = r1_id
    
    enviados = ArchivoEnviado.query.filter_by(cedula=r1_id, telefono=nro_sender[0]).first()
    if (len(nro_sender) > 0 and enviados is None) or reenvio:
        pdf = HTML(url_for('informe_raven2', r1_id=r1_id)).write_pdf()
        try:
            print(f"Enviando whatsapp a {nro_sender[0]}, con {tab} tabulaciones")
            envia_what(r1_id,nro_sender[0], nombre, nombre_alumno, pdf, list_pc_gral, tab, test)
        except:
            flash("Ocurrió un error al enviar el whatsapp", "error")
        try:
            new_sender = ArchivoEnviado(cedula=cedula, telefono=nro_sender[0], metodo='whatsapp', sender=user, test=test)
            db.session.add(new_sender)
            db.session.commit() 
            flash(f'Whatsapp enviado a {nro_sender[0]}')
        except:
            flash(f'Error al guardar en la base de datos.')
    else:
        flash(f'Ya se envío el whatsapp a {nro_sender[0]} anteriormente', "error")
    return redirect(url_for('informe_raven', r1_id=r1_id))


@app.route('/enviar_whatsapp_avan/<int:r1_id>', methods=['GET', 'POST'])
def what_raven_avan_pdf(r1_id):
    try:
        df1= carga_datos_Raven_avanzadas(r1_id)

    except:
        abort(404,"Revisar el formulario del Raven Avanzado")
    test = "Raven Avanzado"
    tab = request.form.get('tabulacion', 17)
    tab = int(tab)
    if request.form.get('isReenvio'):
        reenvio = True
    else:
        reenvio = False
    nro_sender = df1.loc[:,'Nro Teléfono'].values.tolist()
    nombre = df1.loc[:,'Info Contacto'].values.tolist()
    nombre_alumno = df1.loc[:,'Nombre'].values.tolist()
    list_pc_avan = df1.loc[:, ['Pc Avanzado']].astype(int).values.tolist()
    user = current_user.email
    cedula = r1_id
    
    enviados = ArchivoEnviado.query.filter_by(cedula=r1_id, telefono=nro_sender[0]).first()
    if (len(nro_sender) > 0 and enviados is None) or reenvio:
        pdf = HTML(url_for('informe_raven_avan2', r1_id=r1_id)).write_pdf()
        try:
            print(f"Enviando whatsapp a {nro_sender[0]}, con {tab} tabulaciones. Reenvio: {reenvio}")
            envia_what(r1_id,nro_sender[0], nombre, nombre_alumno, pdf, list_pc_avan,tab, test)
        except:
            flash("Ocurrió un error al enviar el whatsapp", "error")
        try:
            flash(f'Whatsapp enviado a {nro_sender[0]}')
            new_sender = ArchivoEnviado(cedula=cedula, telefono=nro_sender[0], metodo='whatsapp', sender=user, test=test)
            db.session.add(new_sender)
            db.session.commit()
        except:
            flash(f'Error al guardar en la base de datos.')
    else:
        flash(f'Ya se envío el whatsapp a {nro_sender[0]} anteriormente', "error")
    return redirect(url_for('informe_raven_avan', r1_id=r1_id))



@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('inicio'))


@app.route('/login/', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    form= LoginForm()
    if form.validate_on_submit():
        user = Usuarios.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('inicio')
            return redirect(next_page)
    return render_template('auth-signin.html', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            token = user.get_reset_password_token()
            # Send email with reset link
            send_password_reset_email(user, token)
            flash('Check your email for instructions to reset your password')
            return redirect(url_for('login'))
        else:
            flash('Email address not found')
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    user = Usuarios.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Tu contraseña ha sido modificada.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/signup/',  methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        edad = form.edad.data
        password = form.password.data
        # Comprobamos que no hubiera un usuario con ese email
        user = Usuarios.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = Usuarios(nombre=name, email=email, edad=edad)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('inicio')
            return redirect(next_page)
    return render_template('signup.html', form=form, error=error)


def envia_mail(r1_id, nombre, cedula, email_sender, user, pdf, test="Raven General"):
    
    msg = Message(
        subject='Informe de evaluación del Proyecto MAPA DE TALENTOS 2.0', 
        sender='mapadetalentos@aikumby.com', 
        recipients= email_sender
    )
    msg.body = f"""Hola {nombre[0]}! Saludos desde Aikumby Centro de Altas Capacidades y Creatividad.
Nos complace informarle que hemos completado la evaluación de su hijo/a en el marco del Proyecto MAPA DE TALENTOS 2.0, y adjunto a este correo encontrará el informe con los resultados de su participación.
Además del informe, hemos incluido un enlace a un video explicativo que le ayudará a comprender mejor los resultados, ofreciéndole una guía clara sobre cómo interpretarlos.
Es importante destacar que este informe no constituye un diagnóstico definitivo por sí solo, sino que refleja el rendimiento de su hijo/a en el momento de la prueba.
En conjunto con OMAPA y el Consejo Nacional de Ciencia y Tecnología - CONACYT Paraguay, agradecemos su confianza en el Proyecto MAPA DE TALENTOS 2.0 y esperamos que estos resultados sean valiosos para el desarrollo educativo de su hijo/a."""
    msg.attach("resultadoRaven.pdf", "application/pdf", pdf)
    with app.open_resource("archivos/Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf") as fp: 
        msg.attach("Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf", "application/pdf", fp.read())
    try:
        mail.send(msg)
        
    except SMTPAuthenticationError as e:
        flash(f'Error al enviar correo a {email_sender[0]}. Error de autenticación: {e.message}')
    except SMTPServerDisconnected as e:
        flash(f'Error al enviar correo a {email_sender[0]}. Error en el servidor SMTP: {e.message}')
    except SMTPException as e:
        flash(f'Error al enviar correo a {email_sender[0]}. Error: {e.message}')
    try:
        new_sender = ArchivoEnviado(cedula=cedula, mail=email_sender[0], metodo='correo', sender=user, test=test)
        db.session.add(new_sender)
        db.session.commit() 
        flash(f'Correo enviado a {email_sender[0]}')
    except:
        flash(f'Error al guardar en la base de datos.')


def send_password_reset_email(user):
    """Envía un correo con un enlace para restablecer la contraseña al `user` dado.

    Usa el token generado por `Usuarios.get_reset_password_token` y las credenciales
    configuradas en `config.py` (vía Flask-Mail `mail`).
    """
    if user is None or not user.email:
        return
    try:
        token = user.get_reset_password_token()
    except Exception as e:
        app.logger.error(f"Error generando token de reset para user {getattr(user, 'id', None)}: {e}")
        return

    reset_url = url_for('reset_password', token=token, _external=True)
    subject = 'Restablecer la contraseña - App Vocacional'
    sender = app.config.get('MAIL_USERNAME') or 'no-reply@example.com'
    recipients = [user.email]

    text_body = f"Hola {getattr(user, 'nombre', '')},\n\nPara restablecer tu contraseña, visita el siguiente enlace:\n{reset_url}\n\nSi no solicitaste este correo, puedes ignorarlo." 
    html_body = f"<p>Hola {getattr(user, 'nombre', '')},</p>\n<p>Para restablecer tu contraseña, haz click en el siguiente enlace:</p>\n<p><a href=\"{reset_url}\">{reset_url}</a></p>\n<p>Si no solicitaste este correo, puedes ignorarlo.</p>"

    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    try:
        mail.send(msg)
        app.logger.info(f"Enviado correo de reset a {user.email}")
    except Exception as e:
        app.logger.error(f"Error enviando correo de reset a {user.email}: {e}")


@app.route('/envio-mail-total')
@login_required
def send_bulk_email():
    form = EnvioMailForm()
    if request.method == "POST":
    
        raven_gral = carga_datos_Raven_gral(0,True)
        list_email = raven_gral.loc[:, ['Correo electrónico']].fillna("").values.tolist()
        list_cedula = raven_gral.loc[:, ['C.I. Nº']].fillna(0).values.tolist()
        list_nombre = raven_gral.loc[:, ['Info Contacto']].fillna("").values.tolist()
        list_pc_gral = raven_gral.loc[:, ['Pc General']].fillna(0).values.tolist()
        list_institucion = raven_gral.loc[:, ['Institución']].fillna("").values.tolist()
        cole = request.form.get('instituto')
        contador = 0
        with mail.connect() as conn:
            for x in range(len(list_email)):
                enviados = ArchivoEnviado.query.filter_by(cedula=list_cedula[x][0]).first()
                if not enviados is None:
                    if contador < 11 and enviados.metodo != "correo" and list_email[x][0] != "" and list_institucion[x][0] == cole:
                        print(list_email[x])
                        print(list_cedula[x][0])
                        print(list_nombre[x][0])
                        msg = Message(
                                subject='Informe de evaluación del Proyecto MAPA DE TALENTOS 2.0', 
                                sender='mapadetalentos@aikumby.com', 
                                recipients= list_email[x]
                            )
                        pdf = HTML(url_for('informe_raven2', r1_id=list_cedula[x][0])).write_pdf()
                        msg.body = f"""Hola {list_nombre[x][0]}! Saludos desde Aikumby Centro de Altas Capacidades y Creatividad.
    Nos complace informarle que hemos completado la evaluación de su hijo/a en el marco del Proyecto MAPA DE TALENTOS 2.0, y adjunto a este correo encontrará el informe con los resultados de su participación.
    Además del informe, hemos incluido un enlace a un video explicativo que le ayudará a comprender mejor los resultados, ofreciéndole una guía clara sobre cómo interpretarlos.
    Es importante destacar que este informe no constituye un diagnóstico definitivo por sí solo, sino que refleja el rendimiento de su hijo/a en el momento de la prueba.
    En conjunto con OMAPA y el Consejo Nacional de Ciencia y Tecnología - CONACYT Paraguay, agradecemos su confianza en el Proyecto MAPA DE TALENTOS 2.0 y esperamos que estos resultados sean valiosos para el desarrollo educativo de su hijo/a."""
                        msg.attach("resultadoRaven.pdf", "application/pdf", pdf)
                        if list_pc_gral[x][0] > 89:
                            with app.open_resource("archivos/Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf") as fp:
                                msg.attach("Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf", "application/pdf", fp.read())
                        try:
                            conn.send(msg)
                        except SMTPAuthenticationError as e:
                            print(f'Error al enviar correo a {list_email[x][0]}. Error de autenticación: {e.message}')
                            continue
                        except SMTPServerDisconnected as e:
                            print(f'Error al enviar correo a {list_email[x][0]}. Error en el servidor SMTP: {e.message}')
                            continue
                        except SMTPException as e:
                            print(f'Error al enviar correo a {list_email[x][0]}.')
                            continue
                        try:
                            contador += 1
                            new_sender = ArchivoEnviado(cedula=list_cedula[x][0], mail=list_email[x][0], metodo='correo', sender='mapadetalentos@aikumby.com', test='Raven General')
                            db.session.add(new_sender)
                            db.session.commit()
                            
                            print(f'Correo enviado a {list_email[x][0]}')
                        except:
                            print(f'Error al guardar en la base de datos. el envio al correo {list_email[x][0]}')
                elif enviados is None and contador < 11 and list_email[x][0] != "" and list_institucion[x][0] == cole:
                    print(list_email[x])
                    print(list_cedula[x][0])
                    print(list_nombre[x][0])
                    msg = Message(
                        subject='Informe de evaluación del Proyecto MAPA DE TALENTOS 2.0', 
                        sender='mapadetalentos@aikumby.com', 
                        recipients= list_email[x]
                    )
                    pdf = HTML(url_for('informe_raven2', r1_id=list_cedula[x][0])).write_pdf()
                    msg.body = f"""Hola {list_nombre[x][0]}! Saludos desde Aikumby Centro de Altas Capacidades y Creatividad.
    Nos complace informarle que hemos completado la evaluación de su hijo/a en el marco del Proyecto MAPA DE TALENTOS 2.0, y adjunto a este correo encontrará el informe con los resultados de su participación.
    Además del informe, hemos incluido un enlace a un video explicativo que le ayudará a comprender mejor los resultados, ofreciéndole una guía clara sobre cómo interpretarlos.
    Es importante destacar que este informe no constituye un diagnóstico definitivo por sí solo, sino que refleja el rendimiento de su hijo/a en el momento de la prueba.
    En conjunto con OMAPA y el Consejo Nacional de Ciencia y Tecnología - CONACYT Paraguay, agradecemos su confianza en el Proyecto MAPA DE TALENTOS 2.0 y esperamos que estos resultados sean valiosos para el desarrollo educativo de su hijo/a."""
                    msg.attach("resultadoRaven.pdf", "application/pdf", pdf)
                    if list_pc_gral[x][0] > 89:
                        with app.open_resource("archivos/Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf") as fp:
                            msg.attach("Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf", "application/pdf", fp.read())
                    try:
                        conn.send(msg)
                    except SMTPAuthenticationError as e:
                        print(f'Error al enviar correo a {list_email[x][0]}. Error de autenticación: {e.message}')
                        continue
                    except SMTPServerDisconnected as e:
                        print(f'Error al enviar correo a {list_email[x][0]}. Error en el servidor SMTP: {e.message}')
                        continue
                    except SMTPException as e:
                        print(f'Error al enviar correo a {list_email[x][0]}.')
                        continue
                    try:
                        contador += 1
                        new_sender = ArchivoEnviado(cedula=list_cedula[x][0], mail=list_email[x][0], metodo='correo', sender='mapadetalentos@aikumby.com', test='Raven General')
                        db.session.add(new_sender)
                        db.session.commit()
                        
                        print(f'Correo enviado a {list_email[x][0]}')
                    except:
                        print(f'Error al guardar en la base de datos el envio al correo {list_email[x][0]}')
        contador_avan = 0
        raven_avan = carga_datos_Raven_avanzadas(0,True)
        list_email_avan = raven_avan.loc[:, ['Correo electrónico']].fillna("").values.tolist()
        list_cedula_avan = raven_avan.loc[:, ['C.I. Nº']].fillna(0).values.tolist()
        list_nombre_avan = raven_avan.loc[:, ['Info Contacto']].fillna("").values.tolist()
        list_pc_avan = raven_avan.loc[:, ['Pc Avanzado']].fillna(0).values.tolist()
        list_institucion_avan = raven_avan.loc[:, ['Institución']].fillna("").values.tolist()
        with mail.connect() as conn:
            for x in range(len(list_email_avan)):
                enviados = ArchivoEnviado.query.filter_by(cedula=list_cedula_avan[x][0]).first()
                if not enviados is None:
                    if contador_avan < 11 and enviados.metodo != "correo" and list_email_avan[x][0] != "" and list_institucion_avan[x][0] == cole:
                        print(list_email_avan[x])
                        print(list_cedula_avan[x][0])
                        print(list_nombre_avan[x][0])
                        msg = Message(
                                subject='Informe de evaluación del Proyecto MAPA DE TALENTOS 2.0', 
                                sender='mapadetalentos@aikumby.com', 
                                recipients= list_email_avan[x]
                            )
                        pdf = HTML(url_for('informe_raven_avan2', r1_id=list_cedula_avan[x][0])).write_pdf()
                        msg.body = f"""Hola {list_nombre_avan[x][0]}! Saludos desde Aikumby Centro de Altas Capacidades y Creatividad.
    Nos complace informarle que hemos completado la evaluación de su hijo/a en el marco del Proyecto MAPA DE TALENTOS 2.0, y adjunto a este correo encontrará el informe con los resultados de su participación.
    Además del informe, hemos incluido un enlace a un video explicativo que le ayudará a comprender mejor los resultados, ofreciéndole una guía clara sobre cómo interpretarlos.
    Es importante destacar que este informe no constituye un diagnóstico definitivo por sí solo, sino que refleja el rendimiento de su hijo/a en el momento de la prueba.
    En conjunto con OMAPA y el Consejo Nacional de Ciencia y Tecnología - CONACYT Paraguay, agradecemos su confianza en el Proyecto MAPA DE TALENTOS 2.0 y esperamos que estos resultados sean valiosos para el desarrollo educativo de su hijo/a."""
                        msg.attach("resultadoRavenAvanzado.pdf", "application/pdf", pdf)
                        if list_pc_avan[x][0] > 89:
                            with app.open_resource("archivos/Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf") as fp:
                                msg.attach("Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf", "application/pdf", fp.read())
                        try:
                            conn.send(msg)
                        except SMTPAuthenticationError as e:
                            print(f'Error al enviar correo a {list_email_avan[x][0]}. Error de autenticación: {e.message}')
                            continue
                        except SMTPServerDisconnected as e:
                            print(f'Error al enviar correo a {list_email_avan[x][0]}. Error en el servidor SMTP: {e.message}')
                            continue
                        except SMTPException as e:
                            print(f'Error al enviar correo a {list_email_avan[x][0]}.')
                            continue
                        try:
                            contador_avan += 1
                            new_sender = ArchivoEnviado(cedula=list_cedula_avan[x][0], mail=list_email_avan[x][0], metodo='correo', sender='mapadetalentos@aikumby.com', test='Raven Avanzado')
                            db.session.add(new_sender)
                            db.session.commit()
                            
                            print(f'Correo enviado a {list_email_avan[x][0]}')
                        except:
                            print(f'Error al guardar en la base de datos. el envio al correo {list_email_avan[x][0]}')
                elif enviados is None and contador_avan < 11 and list_email_avan[x][0] != "" and list_institucion_avan[x][0] == cole:
                    print(list_email_avan[x])
                    print(list_cedula_avan[x][0])
                    print(list_nombre_avan[x][0])
                    msg = Message(
                        subject='Informe de evaluación del Proyecto MAPA DE TALENTOS 2.0', 
                        sender='mapadetalentos@aikumby.com', 
                        recipients= list_email_avan[x]
                    )
                    pdf = HTML(url_for('informe_raven_avan2', r1_id=list_cedula_avan[x][0])).write_pdf()
                    msg.body = f"""Hola {list_nombre_avan[x][0]}! Saludos desde Aikumby Centro de Altas Capacidades y Creatividad.
    Nos complace informarle que hemos completado la evaluación de su hijo/a en el marco del Proyecto MAPA DE TALENTOS 2.0, y adjunto a este correo encontrará el informe con los resultados de su participación.
    Además del informe, hemos incluido un enlace a un video explicativo que le ayudará a comprender mejor los resultados, ofreciéndole una guía clara sobre cómo interpretarlos.
    Es importante destacar que este informe no constituye un diagnóstico definitivo por sí solo, sino que refleja el rendimiento de su hijo/a en el momento de la prueba.
    En conjunto con OMAPA y el Consejo Nacional de Ciencia y Tecnología - CONACYT Paraguay, agradecemos su confianza en el Proyecto MAPA DE TALENTOS 2.0 y esperamos que estos resultados sean valiosos para el desarrollo educativo de su hijo/a."""
                    msg.attach("resultadoRavenAvanzado.pdf", "application/pdf", pdf)
                    if list_pc_avan[x][0] > 89:
                        with app.open_resource("archivos/Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf") as fp:
                            msg.attach("Anexo para resultados superiores. MAPA DE TALENTOS 2.0.pdf", "application/pdf", fp.read())
                    try:
                        conn.send(msg)
                    except SMTPAuthenticationError as e:
                        print(f'Error al enviar correo a {list_email_avan[x][0]}. Error de autenticación: {e.message}')
                        continue
                    except SMTPServerDisconnected as e:
                        print(f'Error al enviar correo a {list_email_avan[x][0]}. Error en el servidor SMTP: {e.message}')
                        continue
                    except SMTPException as e:
                        print(f'Error al enviar correo a {list_email_avan[x][0]}.')
                        continue
                    try:
                        contador_avan += 1
                        new_sender = ArchivoEnviado(cedula=list_cedula_avan[x][0], mail=list_email_avan[x][0], metodo='correo', sender='mapadetalentos@aikumby.com', test='Raven Avanzado')
                        db.session.add(new_sender)
                        db.session.commit()
                        
                        print(f'Correo enviado a {list_email_avan[x][0]}')
                    except:
                        print(f'Error al guardar en la base de datos el envio al correo {list_email_avan[x][0]}')
        return redirect(url_for('raven_gral_list_total'))



if __name__ == '__main__':

    #print jdata
    app.app_context().push()
    db.create_all()
    app.run(debug=True)




