import bisect
from flask import abort
import pandas as pd
import numpy as np


valores_neo = ['No soy una persona que se preocupe mucho. ','Realmente me gustan casi todas las personas que llego a conocer','Tengo una imaginación muy activa. ','Tiendo a ser cínico y escéptico respecto a las intenciones de los demás. ','Se me conoce por mi prudencia y sentido común. ','Con frecuencia me irrita la forma en que me trata la gente. ','Me retraigo de grupos de personas','Los intereses estéticos y artísticos no son muy importantes para mí. ','No soy astuto(a) o artificioso(a).','Yo prefiero mantenerme abierto(a) a toda posibilidad que planearlo todo de antemano. ','Rara vez me siento solo(a) o triste. ','Soy dominante, fuerte y afirmativo(a). ','Sin emociones fuertes, la vida no tendría interés para mí. ','Algunas personas piensan que soy interesado(a) y egoísta.','Trato de realizar conscientemente todas las tareas que se me asignan.','En el trato con los demás siempre temo hacer un error social.','Tengo una manera reposada en el trabajo y en el recreo.','Estoy muy acostumbrado a mi manera de ser.','Preferiero cooperar con los demás que competir con ellos.','Soy indolente y tomo las cosas con calma.','Rara vez abuso de algo.','Con frecuencia busco situaciones emocionantes.','Con frecuencia disfruto darle vueltas en la cabeza a teorías e ideas abstractas','No me molesta alardear de mis talentos y logros','Soy muy hábil midiendo mis pasos para terminar las cosas a tiempo','A menudo me siento desvalido(a) y quiero que alguien resuelva mis problemas','En un sentido literal, nunca he saltado de alegría','Creo que el dejar a los estudiantes escuchar oradores controversiales sólo puede confundirlos y desorientarlos','Los líderes políticos necesitan ser más conscientes del lado humano de su política','A través de los años he hecho algunas cosas muy estúpidas','Fácilmente me da miedo','No me agrada mucho hablar con la gente','Trato de mantener todos mis pensamientos encaminados hacia la realidad y evitar las ilusiones','Creo que la mayoría de la gente tiene buenas intenciones','Las responsabilidades cívicas, como el sufragio, no las tomo muy en serio','Mi temperamento está bien equilibrado','Me gusta tener muchas personas a mi alrededor','A veces estoy completamente absorto(a) en la música que estoy escuchando','Si es necesario estoy dispuesto a manipular a la gente para conseguir lo que quiero','Mantengo mis pertenencias ordenadas y limpias','Algunas veces siento que no valgo','Algunas veces dejo de hacer valer mis ideas tanto como debería','Raramente siento emociones fuertes','Trato de ser cortés con todos los que me encuentro','Algunas veces no soy tan digno de confianza o tan fiable como debería serlo','Pocas veces me siento cohibido(a) cuando estoy entre la gente','Cuando hago las cosas, las hago vigorosamente','Creo que es interesante aprender y desarrollar nuevas aficiones','Puedo ser sarcástico(a) y cortante cuando necesito serlo','Tengo un conjunto de metas claras y me esfuerzo por alcanzarlas de una forma ordenada','Tengo problemas para resistir a mis deseos','No disfrutaría de unas vacaciones en las Vegas','Me aburren los argumentos filosóficos','Prefiero no hablar de mí ni de mis logros','Pierdo mucho tiempo antes de ponerme a trabajar','Siento que soy capaz de enfrentar casi todos mis problemas','Algunas veces he experimentado una intensa felicidad o éxtasis','Creo que las leyes y las normas sociales deberían cambiar para reflejar las necesidades de un mundo en transición','Soy testarudo(a) y obstinado(a) en mis actitudes','Pienso las cosas cuidadosamente antes de tomar una decisión','Raramente me siento atemorizado(a) o ansiosa(a)','Me conocen como una persona cálida y amigable','Tengo una vida imaginativa muy activa','Creo que casi toda la gente se aprovecharía de uno(a) si se lo permites','Me mantengo informado(a) y normalmente tomo decisiones inteligentes','Se me conoce como una persona apasionada y fácilmente irritable','Normalmente prefiero hacer las cosas solo(a)','Me aburre mirar el ballet o la danza moderna','No podría engañar a nadie aunque quisiera','No soy una persona muy metódica','Raras veces estoy triste o deprimido(a)','Con frecuencia he sido líder de los grupos a los que he pertenecido','Lo que siento respecto a las cosas me es muy importante','Algunas personas me consideran frío(a) y calculador(a)','Pago rápido mis deudas y en su totalidad','A veces me siento tan avergonzado(a) que sólo quisiera esconderme','Mi trabajo suele ser lento, pero  constante','Una vez que descubro la forma correcta de hacer algo, sigo haciéndola','Vacilo en expresar mi ira aún cuando esta sea justificada','Cuando empiezo un programa de superación personal, normalmente lo abandono después de unos días','Tengo poca dificultad para resistir a la tentación','Algunas veces he hecho cosas solamente por el gusto o la emoción','Disfruto resolviendo problemas o acertijos','Soy mejor que la mayoría de las personas y estoy seguro (a) de ello','Soy una persona productiva que siempre cumple con el trabajo','Cuando estoy bajo gran presión, a veces siento como si me rompiera a pedazos','No soy un(a) optimista animado(a)','Creo que debemos inspirarnos en nuestras autoridades religiosas para la resolución de cuestiones morales','Nunca podremos hacer demasiado bien por los pobres y los ancianos','En ocasiones actúo primero y pienso después','Con frecuencia me siento tenso(a) y sobresaltado(a)','Muchas personas piensan que soy algo frío(a) y distante','No me gusta perder el tiempo soñando despierto(a)','Creo que casi todos con los que trato son honrados y de confianza','Con frecuencia me meto en situaciones para las que no estoy completamente preparado(a)','No se me considera una persona quisquillosa o temperamental','Verdaderamente siento la necesidad de otras personas si estoy solo por mucho tiempo','Me siento intrigado(a) por las semejanzas que encuentro entre el arte y la naturaleza','El ser perfectamente honesto(a) es malo para los negocios','Me gusta dejarlo todo en su lugar para saber exactamente dónde está','Algunas veces he experimentado un profundo sentimiento de culpabilidad o de haber pecado','En las reuniones normalmente dejo que otros hablen','Rara vez le presto mucha atención a mis sentimientos del momento','Generalmente trato de ser atento(a) y considerado(a)','Algunas veces hago  trampas cuando juego al solitario','No me avergüenzo demasiado si la gente me ridiculiza y me fastidia','Con frecuencia me siento que estoy explotando de energía','Con frecuencia pruebo comidas nuevas y extranjeras','Si no me gusta alguien, se lo hago saber','Trabajo duro para conseguir mis metas','Cuando estoy comiendo mis comidas favoritas, tiendo a comer demasiado','Tiendo a evitar las películas de horror y sustos','A veces pierdo interés cuando la gente habla de cosas muy abstractas y teóricas','Trato de ser humilde','Tengo problemas obligándome a hacer lo que debo','Me mantengo en control durante las emergencias','Algunas veces reboso de felicidad','Creo que las diferentes ideas de lo bueno y lo malo que las personas tienen en otras sociedades pueden ser válidas para ellas','No siento ninguna simpatía por los limosneros','Siempre considero las consecuencias antes de actuar','Rara vez me siento preocupado(a) acerca del futuro','Verdaderamente disfruto hablando con las personas','Disfruto concentrándome en fantasías o en sueños, explorando todas su posibilidades, dejándolas crecer y desarrollarse','Soy suspicaz cuando alguien me hace algún bien','Me enorgullezco de mi buen juicio','A menudo me molesto con la gente con quien tengo que tratar','Prefiero los trabajos que me permiten laborar sólo(a) sin que otros me molesten','La poesía tiene poco o ningún efecto sobre mí','Odiaría que se me considerara un(a) hipócrita','Parece que nunca puedo organizarme','Tiendo a culparme cuando cualquier cosa sale mal','Con frecuencia otras personas esperan que yo tome las decisiones','Experimento una amplia gama de emociones y sentimientos','No se me conoce por mi generosidad','Cuando me comprometo siempre se puede esperar que lo lleve a cabo','Con frecuencia me siento inferior a los demás','No soy tan despierto(a) y animado(a) como otra gente','Prefiero pasar el tiempo en lugares familiares','Cuando se me ha insultado, sólo trato de perdonar y olvidar','No me siento impulsado(a) a superarme','Rara vez me dejo llevar por mis impulsos','Me gusta estar donde está la acción','Disfruto resolviendo acertijos enredados','Tengo una opinión muy elevada de mi persona','Una vez que comienzo un proyecto, casi siempre lo termino','Con frecuencia me es difícil decidirme','No me considero especialmente alegre','Creo que la lealtad a los ideales y principios de uno(a) es más importante que la imparcialidad frente a las ideas ajenas','Las necesidades humanas deben siempre tener prioridad sobre las consideraciones económicas','Con frecuencia hago cosas por impulso','Con frecuencia me preocupo de cosas que puedan salir mal','Me resulta fácil sonreír y ser sociable con los extraños','Si siento que mi mente se llena de fantasías, normalmente empiezo a trabajar y a concentrarme en alguna labor o actividad','Mi primera reacción es la de confiar en la gente','No parezco ser completamente exitoso en nada','Me cuesta mucho enojarme','Prefiero pasar las vacaciones en una playa frecuentada que en una cabaña aislada del bosque','Ciertos tipos de música me causan una fascinación interminable','A veces engaño a la gente para que haga lo que quiero','Tiendo a ser un poco quisquilloso(a) y exigente','Tengo una pobre opinión de mí mismo(a)','Preferiría seguir mi camino que ser líder de los demás','Rara vez me doy cuenta de los estados de ánimo o emociones que me producen ambientes diferentes','A la mayoría de la gente que conozco le caigo bien','Me rijo estrictamente por mis propios principios éticos','Me siento cómodo(a) en presencia de mis jefes o de otras autoridades','Usualmente parezco tener prisa','Algunas veces hago cambios en la casa sólo para probar algo diferente','Si alguien comienza una pelea, estoy listo(a) para contraatacar','Me esfuerzo por alcanzar todo lo que pueda','A veces como hasta hastiarme','Me encanta la emoción de la montaña rusa','Tengo poco interés en divagar sobre la naturaleza del universo y la condición humana','Pienso que no soy mejor que los demás, no importa sus condiciones','Cuando un proyecto se hace demasiado difícil, tiendo a empezar uno nuevo','Puedo controlarme muy bien durante una crisis','Soy una persona alegre y de buen ánimo','Me considero liberal y tolerante del estilo de vida de otras personas','Creo que todos los seres humanos son merecedores de respeto','Raramente tomo decisiones precipitadas','Tengo menos temores que la mayoría de la gente','Tengo fuertes lazos emocionales con mis amigos','Cuando era niño raramente disfrutaba de juegos en los que se pretendía ser alguien diferente (imaginación)','Tiendo a suponer lo mejor de la gente','Soy una persona muy competente','A veces me siento hostil y resentido(a)','Para mí las reuniones sociales son generalmente aburridas','Algunas veces cuando leo poesía o miro una obra de arte, siento un escalofrío u honda emoción','A veces intimido o adulo a la gente para que haga lo que quiero','No soy maniático(a) para la limpieza','Algunas veces las cosas me parecen poco prometedoras y sin esperanzas','En las conversaciones, tiendo a ser quien más habla','Me resulta fácil empatizar – sentir lo que sienten los demás','Me considero una persona caritativa','Trato de realizar los trabajos con cuidado para que no haya que hacerlos','Si he dicho o hecho algo malo a alguien, me es difícil enfrentarme con ellos otra vez','Mi vida es de un ritmo agitado','Cuando estoy de vacaciones prefiero ir a un lugar que conozco y al que estoy acostumbrado','Soy testarudo(a) y terco(a)','Me esfuerzo por alcanzar un nivel de excelencia en todo lo que hago','Algunas veces hago cosas impulsivamente que después lamento','Me siento atraído(a) a los colores brillantes y estilos llamativos','Tengo mucha curiosidad intelectual','Preferiría elogiar a otros que ser elogiado(a)','Hay tantos trabajos pequeños que necesitan realizarse, que algunas veces simplemente no les hago caso','Cuando todo parece ir mal, aún puedo tomar buenas decisiones','Raramente uso palabras como “¡fantástico!” o “¡sensacional!” para describir mis experiencias','Creo que si las personas  no saben en lo que creen para cuando llegan  a los 25, algo anda mal en ellos','Siento mucha compasión por los menos afortunados que yo','Hago planes cuidadosamente cuando me voy de viaje','A veces se me meten en la cabeza pensamientos atemorizantes','Tomo un interés personal con las personas con las que trabajo','Me sería difícil dejar que mi mente vagara sin control o dirección','Tengo mucha fe en la naturaleza humana','Soy efectivo y eficiente en mi trabajo','Aún las molestias pequeñas pueden frustrarme','Disfruto de las fiestas donde hay mucha gente','Disfruto leyendo poesía que enfatiza más los sentimientos y las imágenes que las historias narradas','Me enorgullezco de mi astucia  en el trato con la gente','Dedico mucho tiempo buscando cosas que he extraviado','Frecuentemente cuando las cosas salen mal, me desanimo y quiero rendirme','No me es fácil hacerle frente a una situación','Cosas raras- como ciertos olores o los nombres de los lugares distantes – pueden evocar fuertes estados de ánimo en mí','Si puedo dejo de hacer lo que hago para ayudar a los demás','Realmente tengo que estar enfermo para faltar un día al trabajo','Cuando las personas que conozco hacen cosas tontas, siento vergüenza en lugar de ellos','Soy una persona muy activa','Sigo la misma ruta cuando voy a algún lugar','Con frecuencia tengo discusiones con mi familia y compañeros de trabajo','Soy un adicto al trabajo','Siempre puedo mantener mis emociones bajo control','Me gusta sentirme parte de la muchedumbre en los eventos deportivos','Tengo una amplia gama de intereses intelectuales','Soy una persona superior','Tengo mucha autodisciplina','Soy muy estable emocionalmente','Río fácilmente','Creo que la permisividad de la “nueva moralidad” no es ninguna moralidad','Preferiría ser conocido(a) más por misericordioso que por justo(a)','Pienso dos veces antes de contestar una pregunta']


def convertir_pickle(archivo):
    excel = f"{archivo}.xlsx"
    dfs = pd.read_excel(excel)
    dfs.to_pickle(f"{archivo}.pkl")


# Función para obtener el baremo adecusado según el sexo y la edad del sujeto
def get_dataframe_p1(baremo, edad):
    if baremo == "General" and edad < 5:
        df2 = pd.read_pickle('baremos/P1_Gral_3_4.pkl')

    elif baremo == "Mujeres" and edad < 5:
        df2 = pd.read_pickle('baremos/P1_Muj_3_4.pkl')

    elif baremo == "Varones" and edad < 5:
        df2 = pd.read_pickle('baremos/P1_Var_3_4.pkl')

    elif baremo == "General" and edad < 7:
        df2 = pd.read_pickle('baremos/P1_Gral_5_6.pkl')

    elif baremo == "Varones" and edad < 7:
        df2 = pd.read_pickle('baremos/P1_Var_5_6.pkl')

    elif baremo == "Mujeres" and edad < 7:
        df2 = pd.read_pickle('baremos/P1_Muj_5_6.pkl')

    return df2


def transforma_a_numero(x):
    if x == "Nunca":
        return 0
    elif x == "Alguna vez":
        return 1
    elif x == "Frecuentemente":
        return 2
    elif x == "Casi siempre":
        return 3
    else:
        return 0


# De acuerdo a la nota T de la persona se obtienen los niveles
def get_niveles(df_final, dimension):
    opciones_niveles_adapta = ['Clínicamente significativo', 'En riesgo', 'Medio', 'Alto', 'Muy alto']
    opciones_niveles_clinico = ['Muy bajo', 'Bajo', 'Medio', 'En riesgo', 'Clínicamente significativo']
    clinico = ["Agresividad", "Ansiedad", "Atipicidad", "Depresion", "Hiperactividad", "Problemas de atencion",
               "Retraimiento", "Somatizacion", "Problemas de conducta", "Problemas de aprendizaje",
               "Actitud negativa hacia el colegio", "Actitud negativa hacia los profesores", "Locus de control",
               "Estres social", "Sentido de incapacidad", "Busqueda de sensaciones"]
    adaptable = ["Adaptabilidad", "Habilidades sociales"]
    condiciones = [df_final[f'T {dimension}'] <= 30, df_final[f'T {dimension}'] <= 40, df_final[f'T {dimension}'] <= 59,
                   df_final[f'T {dimension}'] <= 69, df_final[f'T {dimension}'] <= 129]
    if dimension in clinico:
        df_final[f'Nivel {dimension}'] = np.select(condiciones, opciones_niveles_clinico)
    else:
        df_final[f'Nivel {dimension}'] = np.select(condiciones, opciones_niveles_adapta)

    return df_final[f'Nivel {dimension}']


# De una lista de dimensiones se obtienen todos los niveles aplicando la funcion get_niveles
def niveles_all(df_final, prueba="P1"):
    dimensiones_p1 = ["Adaptabilidad", "Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion"]
    dimensiones_p2 = ["Adaptabilidad", "Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion",
                      "Problemas de conducta", "Liderazgo"]
    dimensiones_p3 = ["Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion",
                      "Problemas de conducta", "Liderazgo"]
    dimensiones_t1 = ["Adaptabilidad", "Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion"]
    dimensiones_t2 = ["Adaptabilidad", "Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion",
                      "Problemas de conducta", "Liderazgo", "Problemas de aprendizaje", "Habilidades para el estudio"]
    dimensiones_t3 = ["Agresividad", "Atipicidad", "Ansiedad", "Depresion", "Hiperactividad",
                      "Habilidades sociales", "Problemas de atencion", "Retraimiento", "Somatizacion",
                      "Problemas de conducta", "Liderazgo", "Problemas de aprendizaje", "Habilidades para el estudio"]
    dimensiones_s2 = ["Locus de control", "Atipicidad", "Ansiedad", "Depresion", "Estres social",
                      "Sentido de incapacidad","Relaciones interpersonales", "Relaciones con los padres",
                      "Autoestima", "Confianza en si mismo", "Actitud negativa hacia el colegio",
                      "Actitud negativa hacia los profesores"]
    dimensiones_s3 = ["Locus de control", "Somatizacion", "Atipicidad", "Ansiedad", "Depresion", "Estres social",
                      "Sentido de incapacidad","Relaciones interpersonales", "Relaciones con los padres",
                      "Autoestima", "Confianza en si mismo", "Actitud negativa hacia el colegio",
                      "Actitud negativa hacia los profesores", "Busqueda de sensaciones"]
    if prueba == "P1":
        for x in dimensiones_p1:
            get_niveles(df_final, x)
    elif prueba == "P2":
        for x in dimensiones_p2:
            get_niveles(df_final, x)
    elif prueba == "P3":
        for x in dimensiones_p3:
            get_niveles(df_final, x)
    elif prueba == "T1":
        for x in dimensiones_t1:
            get_niveles(df_final, x)
    elif prueba == "T2":
        for x in dimensiones_t2:
            get_niveles(df_final, x)
    elif prueba == "T3":
        for x in dimensiones_t3:
            get_niveles(df_final, x)
    elif prueba == "S2":
        for x in dimensiones_s2:
            get_niveles(df_final, x)
    elif prueba == "S3":
        for x in dimensiones_s3:
            get_niveles(df_final, x)


# Se obtiene la nota T de las personas de acuerdo a su puntaje en una dimensión
def puntaje_p1(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []

    for j in range(len(valores)):
        #df2 = pd.read_pickle('baremos/P1_Gral_3_4.pkl')
        if baremos[j] == "General" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/P1_Gral_3_4.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/P1_Muj_3_4.pkl')

        elif baremos[j] == "Varones" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/P1_Var_3_4.pkl')

        elif baremos[j] == "General" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/P1_Gral_5_6.pkl')

        elif baremos[j] == "Varones" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/P1_Var_5_6.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/P1_Muj_5_6.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_p2(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/P2_Gral_6_8.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/P2_Muj_6_8.pkl')

        elif baremos[j] == "Varones" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/P2_Var_6_8.pkl')

        elif baremos[j] == "General" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/P2_Gral_9_12.pkl')

        elif baremos[j] == "Varones" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/P2_Var_9_12.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/P2_Muj_9_12.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_p3(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):
        df2 = pd.read_pickle('baremos/P3_Gral_12_14.pkl')
        if baremos[j] == "General" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/P3_Gral_12_14.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/P3_Muj_12_14.pkl')

        elif baremos[j] == "Varones" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/P3_Var_12_14.pkl')

        elif baremos[j] == "General" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/P3_Gral_15_16.pkl')

        elif baremos[j] == "Varones" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/P3_Var_15_16.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/P3_Muj_15_16.pkl')

        elif baremos[j] == "General" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/P3_Gral_17_18.pkl')

        elif baremos[j] == "Varones" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/P3_Var_17_18.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/P3_Muj_17_18.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        print(pc)
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_s2(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 11:
            df2 = pd.read_pickle('baremos/S2_Gral_8_10.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 11:
            df2 = pd.read_pickle('baremos/S2_Muj_8_10.pkl')

        elif baremos[j] == "Varones" and edades[j] < 11:
            df2 = pd.read_pickle('baremos/S2_Var_8_10.pkl')

        elif baremos[j] == "General" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/S2_Gral_11_12.pkl')

        elif baremos[j] == "Varones" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/S2_Var_11_12.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/S2_Muj_11_12.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_s3(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/S3_Gral_12_14.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/S3_Muj_12_14.pkl')

        elif baremos[j] == "Varones" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/S3_Var_12_14.pkl')

        elif baremos[j] == "General" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/S3_Gral_15_16.pkl')

        elif baremos[j] == "Varones" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/S3_Var_15_16.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/S3_Muj_15_16.pkl')

        elif baremos[j] == "General" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/S3_Gral_17_18.pkl')

        elif baremos[j] == "Varones" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/S3_Var_17_18.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/S3_Muj_17_18.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_T1(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/T1_Gral_3_4.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/T1_Muj_3_4.pkl')

        elif baremos[j] == "Varones" and edades[j] < 5:
            df2 = pd.read_pickle('baremos/T1_Var_3_4.pkl')

        elif baremos[j] == "General" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/T1_Gral_5_6.pkl')

        elif baremos[j] == "Varones" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/T1_Var_5_6.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 7:
            df2 = pd.read_pickle('baremos/T1_Muj_5_6.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_t2(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/T2_Gral_6_8.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/T2_Muj_6_8.pkl')

        elif baremos[j] == "Varones" and edades[j] < 9:
            df2 = pd.read_pickle('baremos/T2_Var_6_8.pkl')

        elif baremos[j] == "General" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/T2_Gral_9_12.pkl')

        elif baremos[j] == "Varones" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/T2_Var_9_12.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 13:
            df2 = pd.read_pickle('baremos/T2_Muj_9_12.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def puntaje_t3(valores, edades, baremos, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):

        if baremos[j] == "General" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/T3_Gral_12_14.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/T3_Muj_12_14.pkl')

        elif baremos[j] == "Varones" and edades[j] < 15:
            df2 = pd.read_pickle('baremos/T3_Var_12_14.pkl')

        elif baremos[j] == "General" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/T3_Gral_15_16.pkl')

        elif baremos[j] == "Varones" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/T3_Var_15_16.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 17:
            df2 = pd.read_pickle('baremos/T3_Muj_15_16.pkl')

        elif baremos[j] == "General" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/T3_Gral_17_18.pkl')

        elif baremos[j] == "Varones" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/T3_Var_17_18.pkl')

        elif baremos[j] == "Mujeres" and edades[j] < 19:
            df2 = pd.read_pickle('baremos/T3_Muj_17_18.pkl')

        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado


def get_value_t(df, bare):
    edad1 = df.loc[:, 'Edad'].values.tolist()
    baremo1 = [bare, ]
    agresividad = df.loc[:, 'PD Agresividad'].values.tolist()
    adaptabilidad = df.loc[:, 'PD Adaptabilidad'].values.tolist()
    ansiedad = df.loc[:, 'PD Ansiedad'].values.tolist()
    atipicidad = df.loc[:, 'PD Atipicidad'].values.tolist()
    depresion = df.loc[:, 'PD Depresion'].values.tolist()
    hiperactividad = df.loc[:, 'PD Hiperactividad'].values.tolist()
    habilidades_sociales = df.loc[:, 'PD Habilidades sociales'].values.tolist()
    problemas_atencion = df.loc[:, 'PD Problemas de atencion'].values.tolist()
    retraimiento = df.loc[:, 'PD Retraimiento'].values.tolist()
    somatizacion = df.loc[:, 'PD Somatizacion'].values.tolist()

    puntaje_t = {
        "T Agresividad": puntaje_p1(agresividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Agresividad'),
        "T Adaptabilidad": puntaje_p1(adaptabilidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Adaptabilidad'),
        "T Ansiedad": puntaje_p1(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_p1(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_p1(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Hiperactividad": puntaje_p1(hiperactividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Hiperactividad'),
        "T Habilidades sociales": puntaje_p1(habilidades_sociales, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                             columna_recuperar='T Habilidades sociales'),
        "T Problemas de atencion": puntaje_p1(problemas_atencion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de atención'),
        "T Retraimiento": puntaje_p1(retraimiento, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Retraimiento'),
        "T Somatizacion": puntaje_p1(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Somatización'),
    }
    df_t = pd.DataFrame(puntaje_t)
    return df_t


def get_value_t_p2(df, bare):
    edad1 = df.loc[:, 'Edad'].values.tolist()
    #problema a resolver, usar lista y no texto
    baremo1 = bare
    agresividad = df.loc[:, 'PD Agresividad'].values.tolist()
    adaptabilidad = df.loc[:, 'PD Adaptabilidad'].values.tolist()
    ansiedad = df.loc[:, 'PD Ansiedad'].values.tolist()
    atipicidad = df.loc[:, 'PD Atipicidad'].values.tolist()
    depresion = df.loc[:, 'PD Depresion'].values.tolist()
    hiperactividad = df.loc[:, 'PD Hiperactividad'].values.tolist()
    habilidades_sociales = df.loc[:, 'PD Habilidades sociales'].values.tolist()
    problemas_atencion = df.loc[:, 'PD Problemas de atencion'].values.tolist()
    retraimiento = df.loc[:, 'PD Retraimiento'].values.tolist()
    somatizacion = df.loc[:, 'PD Somatizacion'].values.tolist()
    problemas_conducta = df['PD Problemas de conducta'].values.tolist()
    liderazgo = df['PD Liderazgo'].values.tolist()

    puntaje_t = {
        "T Agresividad": puntaje_p2(agresividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Agresividad'),
        "T Adaptabilidad": puntaje_p2(adaptabilidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Adaptabilidad'),
        "T Ansiedad": puntaje_p2(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_p2(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_p2(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Hiperactividad": puntaje_p2(hiperactividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Hiperactividad'),
        "T Habilidades sociales": puntaje_p2(habilidades_sociales, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                             columna_recuperar='T Habilidades sociales'),
        "T Problemas de atencion": puntaje_p2(problemas_atencion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de atención'),
        "T Retraimiento": puntaje_p2(retraimiento, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Retraimiento'),
        "T Somatizacion": puntaje_p2(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Somatización'),
        "T Problemas de conducta": puntaje_p2(problemas_conducta, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de conducta'),
        "T Liderazgo": puntaje_p2(liderazgo, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Liderazgo'),
    }
    df_t = pd.DataFrame(puntaje_t)
    return df_t


def get_value_t_p3(df, bare):
    edad1 = df.loc[:, 'Edad'].values.tolist()
    #problema a resolver, usar lista y no texto
    baremo1 = bare
    agresividad = df.loc[:, 'PD Agresividad'].values.tolist()
    habilidades_sociales = df.loc[:, 'PD Habilidades sociales'].values.tolist()
    ansiedad = df.loc[:, 'PD Ansiedad'].values.tolist()
    atipicidad = df.loc[:, 'PD Atipicidad'].values.tolist()
    depresion = df.loc[:, 'PD Depresion'].values.tolist()
    hiperactividad = df.loc[:, 'PD Hiperactividad'].values.tolist()
    problemas_atencion = df.loc[:, 'PD Problemas de atencion'].values.tolist()
    retraimiento = df.loc[:, 'PD Retraimiento'].values.tolist()
    somatizacion = df.loc[:, 'PD Somatizacion'].values.tolist()
    problemas_conducta = df['PD Problemas de conducta'].values.tolist()
    liderazgo = df['PD Liderazgo'].values.tolist()
    print(depresion)
    print(edad1)
    print(baremo1)
    puntaje_t = {
        "T Agresividad": puntaje_p3(agresividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Agresividad'),
        "T Habilidades sociales": puntaje_p3(habilidades_sociales, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Habilidades sociales'),
        "T Ansiedad": puntaje_p3(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_p3(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_p3(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Hiperactividad": puntaje_p3(hiperactividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Hiperactividad'),
        "T Problemas de atencion": puntaje_p3(problemas_atencion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de atención'),
        "T Retraimiento": puntaje_p3(retraimiento, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Retraimiento'),
        "T Somatizacion": puntaje_p3(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Somatización'),
        "T Problemas de conducta": puntaje_p3(problemas_conducta, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de conducta'),
        "T Liderazgo": puntaje_p3(liderazgo, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Liderazgo'),
    }
    df_t = pd.DataFrame(puntaje_t)
    return df_t

def get_value_t_s2(df, bare):
    edad1 = df.loc[:, 'Edad'].values.tolist()
    #problema a resolver, usar lista y no texto
    baremo1 = bare
    act_colegio = df.loc[:, 'PD Actitud negativa hacia el colegio'].values.tolist()
    act_prof = df.loc[:, 'PD Actitud negativa hacia los profesores'].values.tolist()
    ansiedad = df.loc[:, 'PD Ansiedad'].values.tolist()
    atipicidad = df.loc[:, 'PD Atipicidad'].values.tolist()
    depresion = df.loc[:, 'PD Depresion'].values.tolist()
    locus = df.loc[:, 'PD Locus de control'].values.tolist()
    estres = df.loc[:, 'PD Estres social'].values.tolist()
    incapacidad = df.loc[:, 'PD Sentido de incapacidad'].values.tolist()
    interpersonal = df.loc[:, 'PD Relaciones interpersonales'].values.tolist()
    rel_padres = df['PD Relaciones con los padres'].values.tolist()
    autoestima = df['PD Autoestima'].values.tolist()
    confianza = df['PD Confianza en si mismo'].values.tolist()
    puntaje_t = {
        "T Actitud negativa hacia el colegio": puntaje_s2(act_colegio, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Actitud negativa hacia el colegio'),
        "T Actitud negativa hacia los profesores": puntaje_s2(act_prof, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Actitud negativa hacia los profesores'),
        "T Ansiedad": puntaje_s2(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_s2(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_s2(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Locus de control": puntaje_s2(locus, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Locus de control'),
        "T Estres social": puntaje_s2(estres, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Estrés social'),
        "T Sentido de incapacidad": puntaje_s2(incapacidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Sentido de incapacidad'),
        "T Relaciones interpersonales": puntaje_s2(interpersonal, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Relaciones interpersonales'),
        "T Relaciones con los padres": puntaje_s2(rel_padres, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Relaciones con los padres'),
        "T Autoestima": puntaje_s2(autoestima, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Autoestima'),
        "T Confianza en si mismo": puntaje_s2(confianza, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Confianza en si mismo'),
    }
    df_t = pd.DataFrame(puntaje_t)
    return df_t


def get_value_t_s3(df, bare):
    edad1 = df.loc[:, 'Edad'].values.tolist()
    #problema a resolver, usar lista y no texto
    baremo1 = bare
    act_colegio = df.loc[:, 'PD Actitud negativa hacia el colegio'].values.tolist()
    act_prof = df.loc[:, 'PD Actitud negativa hacia los profesores'].values.tolist()
    ansiedad = df.loc[:, 'PD Ansiedad'].values.tolist()
    atipicidad = df.loc[:, 'PD Atipicidad'].values.tolist()
    depresion = df.loc[:, 'PD Depresion'].values.tolist()
    locus = df.loc[:, 'PD Locus de control'].values.tolist()
    estres = df.loc[:, 'PD Estres social'].values.tolist()
    incapacidad = df.loc[:, 'PD Sentido de incapacidad'].values.tolist()
    interpersonal = df.loc[:, 'PD Relaciones interpersonales'].values.tolist()
    rel_padres = df['PD Relaciones con los padres'].values.tolist()
    autoestima = df['PD Autoestima'].values.tolist()

    confianza = df['PD Confianza en si mismo'].values.tolist()
    busqueda = df['PD Busqueda de sensaciones'].values.tolist()
    somatizacion = df['PD Somatizacion'].values.tolist()

    puntaje_t = {
        "T Actitud negativa hacia el colegio": puntaje_s3(act_colegio, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Actitud negativa hacia el colegio'),
        "T Actitud negativa hacia los profesores": puntaje_s3(act_prof, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Actitud negativa hacia los profesores'),
        "T Ansiedad": puntaje_s3(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_s3(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_s3(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Locus de control": puntaje_s3(locus, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Locus de control'),
        "T Estres social": puntaje_s3(estres, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Estrés social'),
        "T Sentido de incapacidad": puntaje_s3(incapacidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Sentido de incapacidad'),
        "T Relaciones interpersonales": puntaje_s3(interpersonal, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Relaciones interpersonales'),
        "T Relaciones con los padres": puntaje_s3(rel_padres, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Relaciones con los padres'),
        "T Autoestima": puntaje_s3(autoestima, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Autoestima'),
        "T Confianza en si mismo": puntaje_s3(confianza, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Confianza en si mismo'),
        "T Busqueda de sensaciones": puntaje_s3(busqueda, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Busqueda de sensaciones'),
        "T Somatizacion": puntaje_s3(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                                columna_recuperar='T Somatizacion'),
    }
    df_t = pd.DataFrame(puntaje_t)
    return df_t
# Transforma los valores de texto a numeros (se podría cambiar por la función map
"""
def recodifica_var(df_columns):
    # print(df.iloc[:,1].map({"Nunca":0, "Alguna vez":1, "Frecuentemente":2,"Casi siempre":3}))
    for i in range(df_columns):
        df.iloc[:, i] = df.iloc[:, i].apply(transforma_a_numero)
    return df
"""


# Se obtiene la edad de una persona según el calendario gregoriano
def date_diff(date1, date2):
    return (date1 - date2).days / 365.2425


def cargar_dataframe(url1):
    url = ""

    # Se lee la página web, el argumento header=1 indica que el nombre de las columnas está en la segunda fila
    # El encoding="UTF-8" asegura que se reconozca los acentos y la ñ
    #tablas = pd.read_html(url1, header=1, encoding="UTF-8")
    #df = tablas[0]
    df = pd.read_csv(url1)
    # Agregar columna con el número de filas empezando desde 0 al comienzo del dataframe
    df.insert(0, '1', range(len(df)))
    df.columns = df.columns.str.strip()
    return df


def dataframe_calculos_iniciales(url2, prueba="P1"):
    # Se declara la url de la cual se va a leer los datos
    url = ""
    df = cargar_dataframe(url2)
    df_info = df.iloc[1:, :8]

    # Convertir a formato datetime

    df_info.loc[df_info.iloc[:, 2] == 'Avril Napout', 'Fecha de nacimiento'] = '04/17/2015'

    df_info['Fecha de nacimiento'] = pd.to_datetime(df_info['Fecha de nacimiento'], infer_datetime_format=True)
    df_info['Fecha'] = pd.to_datetime(df_info['Fecha'], infer_datetime_format=True)

    """df_info['Fecha de nacimiento'] = pd.to_datetime(df_info['Fecha de nacimiento'], infer_datetime_format=True)
    df_info['Fecha'] = pd.to_datetime(df_info['Fecha'], infer_datetime_format=True)"""

    # Calculamos la edad
    df_info['dias'] = (df_info['Fecha'] - df_info['Fecha de nacimiento']).dt.days
    df_info['Edad'] = df_info['dias'] / 365.2425
    df_info['Edad'] = df_info['Edad'].astype(int)

    # Añadimos la columna baremo en función del sexo de la persona mediante map
    df_info['Baremo'] = df_info['Sexo'].map({'Varón': 'Varones',
                                             'Mujer': 'Mujeres'})

    # Se selecciona solo las columnas de los items
    df = df.iloc[1:, 8:]

    # Se recodifican todas las columnas
    if prueba == "S2" or prueba == "S3":
        for i in range(len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].map({'Verdadero': 1,'Falso': 0})
        df = df.fillna(0)
    else:
        for i in range(len(df.columns)):
            df.iloc[:, i] = df.iloc[:, i].apply(transforma_a_numero)
    # df = recodifica_var(len(df.columns))

    df1 = pd.concat([df_info, df], axis=1)
    return df1


def dataframe_s3():
    # Se declara la url de la cual se va a leer los datos

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR25wTAMvC1MoJFfbregZx1ngybD6mzYA3u-hytaRMvlYWM4RKJC7yYqr2KWzfYuEXcrvBE4-pmcGyA/pubhtml"
    df = dataframe_calculos_iniciales(url, prueba="S3")
    # df = recodifica_var(len(df.columns))
    df_info = df.iloc[:, :11]
    df = df.iloc[:, 11:]


    # Se calculan los puntajes directos
    puntaje_directo = {
        "PD Actitud negativa hacia el colegio": df.iloc[:, 2] + df.iloc[:, 17] + df.iloc[:, 32] + df.iloc[:, 46] + df.iloc[:, 61] \
                          + (1- df.iloc[:, 75]) + df.iloc[:, 90] + df.iloc[:, 119] + df.iloc[:, 145],
        "PD Actitud negativa hacia los profesores": (1- df.iloc[:, 11]) + (1 - df.iloc[:, 24]) + df.iloc[:, 41] + df.iloc[:, 70] + \
                            df.iloc[:, 81] + df.iloc[:, 98] + (1 - df.iloc[:, 127]) + (1 - df.iloc[:, 153]) + (1 - df.iloc[:, 171]),
        "PD Ansiedad": df.iloc[:, 4] + df.iloc[:, 18] + df.iloc[:, 28] + df.iloc[:, 34] + df.iloc[:, 47] \
                       + df.iloc[:, 56] + df.iloc[:, 63]+ df.iloc[:, 76]+ df.iloc[:, 92] + df.iloc[:, 104] \
                      + df.iloc[:, 121]+ df.iloc[:, 147]+ df.iloc[:, 152]+ df.iloc[:, 158]+ df.iloc[:, 172],
        "PD Atipicidad": df.iloc[:, 10] + df.iloc[:, 23] + df.iloc[:, 40] + df.iloc[:, 52] + df.iloc[:, 57] \
                         + df.iloc[:, 69] + df.iloc[:, 80] + df.iloc[:, 86] + df.iloc[:, 97] + df.iloc[:, 109] \
                        + df.iloc[:, 115] + df.iloc[:, 137] + df.iloc[:, 142] + df.iloc[:, 163] + df.iloc[:, 168] \
                        + df.iloc[:, 173],
        "PD Depresion": df.iloc[:, 6] + df.iloc[:, 20] + df.iloc[:, 36] + df.iloc[:, 49] + df.iloc[:, 65] \
                        + df.iloc[:, 78] + df.iloc[:, 94] + df.iloc[:, 99] + df.iloc[:, 106] + df.iloc[:, 123]
                        + df.iloc[:, 149] + df.iloc[:, 160] + df.iloc[:, 175] + (1 - df.iloc[:, 178]),
        "PD Locus de control": df.iloc[:, 1] + df.iloc[:, 16] + df.iloc[:, 31] + df.iloc[:, 45] + df.iloc[:, 53] \
                             + (1 - df.iloc[:, 59]) + df.iloc[:, 60] + df.iloc[:, 74] + df.iloc[:, 89] + df.iloc[:, 103] \
                             + df.iloc[:, 118] + df.iloc[:, 132] +  df.iloc[:, 157] + df.iloc[:, 180],
        "PD Estres social": df.iloc[:, 7] + df.iloc[:, 21] + df.iloc[:, 37] + df.iloc[:, 50] + df.iloc[:, 66] + df.iloc[:, 82] + df.iloc[:, 95]+ df.iloc[:, 107] + df.iloc[:, 124] + df.iloc[:, 135] + df.iloc[:, 150] + df.iloc[:, 161] + df.iloc[:, 179],
        "PD Sentido de incapacidad": df.iloc[:, 13] + df.iloc[:, 43] + df.iloc[:, 54] + df.iloc[:, 72] + df.iloc[:, 83] \
                           + df.iloc[:, 100] + df.iloc[:, 110] + df.iloc[:, 112] + df.iloc[:, 129] + df.iloc[:, 140] \
                            + df.iloc[:, 154] + df.iloc[:, 183],
        "PD Relaciones interpersonales": df.iloc[:, 0] + df.iloc[:, 15] + (1 - df.iloc[:, 30]) + \
                                         df.iloc[:, 44] + (1 - df.iloc[:, 85]) + df.iloc[:, 88] \
                           + df.iloc[:, 102] + (1- df.iloc[:, 114]) + df.iloc[:, 117] \
                            + df.iloc[:, 131] + (1 - df.iloc[:, 141]) + df.iloc[:, 144] + (1 -df.iloc[:, 156]) \
                            + (1 -df.iloc[:, 167]) + df.iloc[:, 182],
        "PD Relaciones con los padres": df.iloc[:, 9] + df.iloc[:, 39] + df.iloc[:, 68] + df.iloc[:, 96] \
                                        + df.iloc[:, 126] + df.iloc[:, 138] + df.iloc[:, 151] + df.iloc[:, 164]\
                                    + df.iloc[:, 181],
        "PD Autoestima": df.iloc[:, 3] + (1 - df.iloc[:, 33]) + (1 -df.iloc[:, 62]) + (1- df.iloc[:, 91]) + df.iloc[:, 120] \
                        + df.iloc[:, 133] + (1 - df.iloc[:, 146])+ df.iloc[:, 176],
        "PD Confianza en si mismo": df.iloc[:, 29] + df.iloc[:, 38] + df.iloc[:, 58] + df.iloc[:, 87] + df.iloc[:, 116] \
                         + df.iloc[:, 143] + df.iloc[:, 166] + df.iloc[:, 169] + (1 -df.iloc[:, 177]),
        "PD Busqueda de sensaciones": df.iloc[:, 5] + df.iloc[:, 12] + df.iloc[:, 19] + df.iloc[:, 35] + df.iloc[:, 48] \
                                    + df.iloc[:, 64] + df.iloc[:, 77] + df.iloc[:, 93] + df.iloc[:, 105] \
                                      + df.iloc[:, 122] + df.iloc[:, 134] + df.iloc[:, 148] + df.iloc[:, 159] \
                                    + df.iloc[:, 174],
        "PD Somatizacion": (1 -df.iloc[:, 14]) + df.iloc[:, 55] + df.iloc[:, 73] + df.iloc[:, 84] + df.iloc[:, 101] \
                                      + df.iloc[:, 113] + df.iloc[:, 130] + df.iloc[:, 155] + df.iloc[:, 184],

    }

    # inicio=time.time()
    # Convertir a lista los baremos, edad y los puntajes directos de cada dimensión
    df_puntaje = pd.DataFrame(puntaje_directo)

    df_puntaje = df_puntaje[df_puntaje.columns].fillna(0.0).astype(int)

    # Se une el dataframe de la info y los puntajes
    df_unido = pd.concat([df_info, df_puntaje], axis=1)
    baremo1 = df_info['Baremo'].values.tolist()
    df_t = get_value_t_s3(df_unido, baremo1)

    # print(time.time()-inicio)

    # Se resetea los indices de todos los dataframes
    df_info = df_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df_puntaje = df_puntaje.reset_index(drop=True)
    df_t = df_t.reset_index(drop=True)
    df_info_filtrado = df_info.loc[:, ['1', 'Nombre y apellido', 'Edad', 'Baremo']]
    # Se unen todos los dataframes
    df_final = pd.concat([df_info_filtrado, df_puntaje, df_t], axis=1)
    # Se generan las columnas de los niveles basados en el puntaje T con la funcion niveles_all()
    niveles_all(df_final, prueba="S3")
    df_final.iloc[:, 0] = df_final.iloc[:, 0].map(int)
    df_final.rename(columns={'1': 'Id'}, inplace=True)
    df_final = df_final.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Actitud negativa hacia el colegio', 'T Actitud negativa hacia el colegio',
                                         'Nivel Actitud negativa hacia el colegio',
                                         'PD Actitud negativa hacia los profesores',
                                         'T Actitud negativa hacia los profesores',
                                         'Nivel Actitud negativa hacia los profesores',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Locus de control', 'T Locus de control', 'Nivel Locus de control',
                                         'PD Estres social', 'T Estres social',
                                         'Nivel Estres social',
                                         'PD Sentido de incapacidad', 'T Sentido de incapacidad',
                                         'Nivel Sentido de incapacidad',
                                         'PD Relaciones interpersonales', 'T Relaciones interpersonales',
                                         'Nivel Relaciones interpersonales',
                                         'PD Relaciones con los padres', 'T Relaciones con los padres',
                                         'Nivel Relaciones con los padres',
                                         'PD Autoestima', 'T Autoestima',
                                         'Nivel Autoestima',
                                         'PD Confianza en si mismo', 'T Confianza en si mismo',
                                         'Nivel Confianza en si mismo',
                                         'PD Busqueda de sensaciones', 'T Busqueda de sensaciones',
                                         'Nivel Busqueda de sensaciones',
                                         'PD Somatizacion', 'T Somatizacion',
                                         'Nivel Somatizacion'])
    # Guardar en csv
    # df_final.to_csv('resultados1.csv', encoding='utf-8')
    return df_final


def dataframe_s2():
    # Se declara la url de la cual se va a leer los datos

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1-GbOxaijA7BRMixTuoRynuQiYXyfjsPUlGx5CzHm-TSTev5PWP03YEQLrR00aMRKxfsof3fc4ul2/pubhtml"
    df = dataframe_calculos_iniciales(url, prueba="S2")
    # df = recodifica_var(len(df.columns))
    df_info = df.iloc[:, :11]
    df = df.iloc[:, 11:]
    # Se calculan los puntajes directos
    puntaje_directo = {
        "PD Actitud negativa hacia el colegio": df.iloc[:, 0] + df.iloc[:, 11] + df.iloc[:, 20] + df.iloc[:, 23] + df.iloc[:, 35] \
                          + df.iloc[:, 44] + (1- df.iloc[:, 68]) + df.iloc[:, 92] + df.iloc[:, 115],
        "PD Actitud negativa hacia los profesores": df.iloc[:, 6] + (1 - df.iloc[:, 13]) + df.iloc[:, 22] + df.iloc[:, 29] + \
                            df.iloc[:, 51] + (1- df.iloc[:, 74]) + df.iloc[:, 98] + (1 - df.iloc[:, 121]) + (1 - df.iloc[:, 138]),
        "PD Ansiedad": df.iloc[:, 2] + df.iloc[:, 12] + df.iloc[:, 26] + df.iloc[:, 36] + df.iloc[:, 40] \
                       + df.iloc[:, 47] + df.iloc[:, 58]+ df.iloc[:, 64]+ df.iloc[:, 71] + df.iloc[:, 81] \
                      + df.iloc[:, 88]+ df.iloc[:, 105]+ df.iloc[:, 111]+ df.iloc[:, 118]+ df.iloc[:, 128] \
                      + df.iloc[:, 135] + df.iloc[:, 139],
        "PD Atipicidad": df.iloc[:, 4] + df.iloc[:, 14] + df.iloc[:, 21] + df.iloc[:, 42] + df.iloc[:, 49] \
                         + df.iloc[:, 60] + df.iloc[:, 73] + df.iloc[:, 83] + df.iloc[:, 96] + df.iloc[:, 107] \
                        + df.iloc[:, 120] + df.iloc[:, 130] + df.iloc[:, 140],
        "PD Depresion": df.iloc[:, 5] + df.iloc[:, 15] + df.iloc[:, 28] + df.iloc[:, 41] + df.iloc[:, 50] \
                        + df.iloc[:, 61] + df.iloc[:, 65] + df.iloc[:, 84] + df.iloc[:, 89] + df.iloc[:, 97]
                        + df.iloc[:, 108] + df.iloc[:, 112] + df.iloc[:, 131] + df.iloc[:, 136] + df.iloc[:, 141],
        "PD Locus de control": df.iloc[:, 1] + df.iloc[:, 10] + df.iloc[:, 18] + df.iloc[:, 24] + df.iloc[:, 34] \
                             + df.iloc[:, 39] + df.iloc[:, 45] + df.iloc[:, 56] + df.iloc[:, 69] + df.iloc[:, 79] \
                             + df.iloc[:, 87] + df.iloc[:, 93] + (1 - df.iloc[:, 94]) + df.iloc[:, 103] \
                             + df.iloc[:, 116] + df.iloc[:, 126] + df.iloc[:, 143],
        "PD Estres social": df.iloc[:, 8] + df.iloc[:, 17] + df.iloc[:, 32] + df.iloc[:, 38] + \
                                    df.iloc[:, 54] + df.iloc[:, 63] + df.iloc[:, 77]+ df.iloc[:, 86] \
                            + df.iloc[:, 101] + df.iloc[:, 124] + df.iloc[:, 133] + df.iloc[:, 142],
        "PD Sentido de incapacidad": df.iloc[:, 16] + df.iloc[:, 30] + df.iloc[:, 37] + df.iloc[:, 52] + df.iloc[:, 62] \
                           + df.iloc[:, 75] + df.iloc[:, 85] + df.iloc[:, 99] + df.iloc[:, 109] + df.iloc[:, 122] \
                            + df.iloc[:, 132] + df.iloc[:, 145],
        "PD Relaciones interpersonales": df.iloc[:, 25] + (1 - df.iloc[:, 46]) + (1 - df.iloc[:, 66]) + \
                                         (1 - df.iloc[:, 70]) + df.iloc[:, 82] + df.iloc[:, 90] \
                           + (1 - df.iloc[:, 104]) + (1- df.iloc[:, 117]) + (1 - df.iloc[:, 125]),
        "PD Relaciones con los padres": df.iloc[:, 3] + (1 - df.iloc[:, 27]) + df.iloc[:, 48] + df.iloc[:, 59] \
                                        + df.iloc[:, 72] + df.iloc[:, 95] + df.iloc[:, 110] + df.iloc[:, 119]\
                                    + df.iloc[:, 134] + df.iloc[:, 144],
        "PD Autoestima": (1-df.iloc[:, 7]) + df.iloc[:, 31] + df.iloc[:, 53] + (1- df.iloc[:, 76]) + df.iloc[:, 100] \
                        + df.iloc[:, 123],
        "PD Confianza en si mismo": df.iloc[:, 9] + df.iloc[:, 33] + df.iloc[:, 43] + df.iloc[:, 55] + df.iloc[:, 67] \
                         + df.iloc[:, 78] + df.iloc[:, 91] + df.iloc[:, 102] + df.iloc[:, 113] + df.iloc[:, 114] \
                         + df.iloc[:, 125] + df.iloc[:, 137],

    }

    # inicio=time.time()
    # Convertir a lista los baremos, edad y los puntajes directos de cada dimensión
    df_puntaje = pd.DataFrame(puntaje_directo)
    # Se une el dataframe de la info y los puntajes
    df_unido = pd.concat([df_info, df_puntaje], axis=1)
    baremo1 = df_info['Baremo'].values.tolist()
    df_t = get_value_t_s2(df_unido, baremo1)

    # print(time.time()-inicio)

    # Se resetea los indices de todos los dataframes
    df_info = df_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df_puntaje = df_puntaje.reset_index(drop=True)
    df_t = df_t.reset_index(drop=True)
    df_info_filtrado = df_info.loc[:, ['1', 'Nombre y apellido', 'Edad', 'Baremo']]
    # Se unen todos los dataframes
    df_final = pd.concat([df_info_filtrado, df_puntaje, df_t], axis=1)
    prueba = "S2"
    # Se generan las columnas de los niveles basados en el puntaje T con la funcion niveles_all()
    niveles_all(df_final, prueba="S2")
    df_final.iloc[:, 0] = df_final.iloc[:, 0].map(int)
    df_final.rename(columns={'1': 'Id'}, inplace=True)
    df_final = df_final.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Actitud negativa hacia el colegio', 'T Actitud negativa hacia el colegio',
                                         'Nivel Actitud negativa hacia el colegio',
                                         'PD Actitud negativa hacia los profesores',
                                         'T Actitud negativa hacia los profesores',
                                         'Nivel Actitud negativa hacia los profesores',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Locus de control', 'T Locus de control', 'Nivel Locus de control',
                                         'PD Estres social', 'T Estres social',
                                         'Nivel Estres social',
                                         'PD Sentido de incapacidad', 'T Sentido de incapacidad',
                                         'Nivel Sentido de incapacidad',
                                         'PD Relaciones interpersonales', 'T Relaciones interpersonales',
                                         'Nivel Relaciones interpersonales',
                                         'PD Relaciones con los padres', 'T Relaciones con los padres',
                                         'Nivel Relaciones con los padres',
                                         'PD Autoestima', 'T Autoestima',
                                         'Nivel Autoestima',
                                         'PD Confianza en si mismo', 'T Confianza en si mismo',
                                         'Nivel Confianza en si mismo'])
    # Guardar en csv
    # df_final.to_csv('resultados1.csv', encoding='utf-8')
    return df_final


def dataframe_p3():
    # Se declara la url de la cual se va a leer los datos

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgBOXN5DEWrbtzdLKE5iHShqOWphkRzhkD08EyIJ5E51if_2tO531nNvC9_1oG4Bz8bpMKF9Pl-1bF/pub?output=csv"
    df = dataframe_calculos_iniciales(url)
    # df = recodifica_var(len(df.columns))
    df_info = df.iloc[:, :11]
    df = df.iloc[:, 11:]
    # Se calculan los puntajes directos
    puntaje_directo = {
        "PD Agresividad": df.iloc[:, 1] + df.iloc[:, 11] + df.iloc[:, 22] + df.iloc[:, 32] + df.iloc[:, 41] \
                          + df.iloc[:, 52] + df.iloc[:, 61] + df.iloc[:, 72] + df.iloc[:, 87] + df.iloc[:, 97] \
                          + df.iloc[:, 116],
        "PD Habilidades sociales": df.iloc[:, 0] + df.iloc[:, 10] + df.iloc[:, 21] + df.iloc[:, 31] + \
                            df.iloc[:, 51] + df.iloc[:, 60] + df.iloc[:, 71] + df.iloc[:, 79] + df.iloc[:, 86] \
                          + df.iloc[:, 96]+ df.iloc[:, 107]+ df.iloc[:, 121],
        "PD Ansiedad": df.iloc[:, 2] + df.iloc[:, 12] + df.iloc[:, 23] + df.iloc[:, 33] + df.iloc[:, 42] \
                       + df.iloc[:, 53] + df.iloc[:, 62]+ df.iloc[:, 73]+ df.iloc[:, 98],
        "PD Atipicidad": df.iloc[:, 4] + df.iloc[:, 14] + df.iloc[:, 35] + df.iloc[:, 44] + df.iloc[:, 54] \
                         + df.iloc[:, 64] + df.iloc[:, 89] + df.iloc[:, 100] + df.iloc[:, 110],
        "PD Depresion": df.iloc[:, 6] + df.iloc[:, 16] + df.iloc[:, 26] + df.iloc[:, 36] + df.iloc[:, 46] \
                        + df.iloc[:, 56] + df.iloc[:, 66] + df.iloc[:, 76] + df.iloc[:, 82] + df.iloc[:, 91]
                        + df.iloc[:, 102],
        "PD Hiperactividad": df.iloc[:, 7] + df.iloc[:, 17] + df.iloc[:, 27] + df.iloc[:, 47] + df.iloc[:, 57] \
                             + df.iloc[:, 67] + df.iloc[:, 92] + df.iloc[:, 103] + df.iloc[:, 119],
        "PD Problemas de atencion": df.iloc[:, 3] + df.iloc[:, 34] + (3-df.iloc[:, 43]) + df.iloc[:, 63] + \
                                    (3 - df.iloc[:, 74]) + (3 - df.iloc[:, 88]) + df.iloc[:, 99]+ df.iloc[:, 117],
        "PD Retraimiento": df.iloc[:, 20] + df.iloc[:, 40] + df.iloc[:, 50] + df.iloc[:, 70] + df.iloc[:, 78] \
                           + df.iloc[:, 95] + df.iloc[:, 106] + df.iloc[:, 120],
        "PD Somatizacion": df.iloc[:, 9] + df.iloc[:, 19] + df.iloc[:, 29] + df.iloc[:, 39] + df.iloc[:, 49] \
                           + df.iloc[:, 69] + df.iloc[:, 85] + df.iloc[:, 94] + df.iloc[:, 105] + df.iloc[:, 115]
                           + df.iloc[:, 122],
        "PD Problemas de conducta": df.iloc[:, 5] + df.iloc[:, 15] + df.iloc[:, 25] + df.iloc[:, 30] + df.iloc[:, 45] \
                                    + df.iloc[:, 55] + df.iloc[:, 59] + df.iloc[:, 65] + df.iloc[:, 75] \
                                    + df.iloc[:,81]+ df.iloc[:,90]+ df.iloc[:,101]+ df.iloc[:,111]+ df.iloc[:,118],
        "PD Liderazgo": df.iloc[:, 8] + df.iloc[:, 18] + df.iloc[:, 28] + df.iloc[:, 38] + df.iloc[:, 48] \
                        + df.iloc[:, 58] + df.iloc[:, 68] + df.iloc[:, 77] + df.iloc[:, 84] + df.iloc[:, 93] \
                        + df.iloc[:, 104]+ df.iloc[:, 114],

    }

    # inicio=time.time()
    # Convertir a lista los baremos, edad y los puntajes directos de cada dimensión
    df_puntaje = pd.DataFrame(puntaje_directo)
    # Se une el dataframe de la info y los puntajes
    df_unido = pd.concat([df_info, df_puntaje], axis=1)
    baremo1 = df_info['Baremo'].values.tolist()
    df_t = get_value_t_p3(df_unido, baremo1)

    # print(time.time()-inicio)

    # Se resetea los indices de todos los dataframes
    df_info = df_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df_puntaje = df_puntaje.reset_index(drop=True)
    df_t = df_t.reset_index(drop=True)
    df_info_filtrado = df_info.loc[:, ['1', 'Nombre y apellido', 'Edad', 'Baremo']]
    # Se unen todos los dataframes
    df_final = pd.concat([df_info_filtrado, df_puntaje, df_t], axis=1)
    prueba = "P2"
    # Se generan las columnas de los niveles basados en el puntaje T con la funcion niveles_all()
    niveles_all(df_final, prueba="P3")
    df_final.iloc[:, 0] = df_final.iloc[:, 0].map(int)
    df_final.rename(columns={'1': 'Id'}, inplace=True)
    df_final = df_final.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                         'PD Habilidades sociales', 'T Habilidades sociales',
                                         'Nivel Habilidades sociales',
                                         'PD Problemas de atencion', 'T Problemas de atencion',
                                         'Nivel Problemas de atencion',
                                         'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                         'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion',
                                         'PD Problemas de conducta', 'T Problemas de conducta',
                                         'Nivel Problemas de conducta',
                                         'PD Liderazgo', 'T Liderazgo', 'Nivel Liderazgo'])
    # Guardar en csv
    # df_final.to_csv('resultados1.csv', encoding='utf-8')
    return df_final


def dataframe_p2():
    # Se declara la url de la cual se va a leer los datos

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7vGtlwPr73WmlOAKR3lK4223ytE9mQzodJJtABdyewRjeLpc91aJv-9MeGPEzIsJoBfYFG1h_HXJG/pubhtml"
    df = dataframe_calculos_iniciales(url)
    # df = recodifica_var(len(df.columns))
    df_info = df.iloc[:, :11]
    df = df.iloc[:, 11:]
    # Se calculan los puntajes directos
    puntaje_directo = {
        "PD Agresividad": df.iloc[:, 1] + df.iloc[:, 20] + df.iloc[:, 28] + df.iloc[:, 31] + df.iloc[:, 42] \
                          + df.iloc[:, 53] + df.iloc[:, 65] + df.iloc[:, 77] + df.iloc[:, 88] + df.iloc[:, 98]
                          + df.iloc[:, 110] + df.iloc[:, 121] + df.iloc[:, 130],
        "PD Adaptabilidad": df.iloc[:, 0] + df.iloc[:, 30] + (3 - df.iloc[:, 41]) + df.iloc[:, 64] + \
                            df.iloc[:, 76] + df.iloc[:, 97] + df.iloc[:, 109] + df.iloc[:, 129],
        "PD Ansiedad": df.iloc[:, 2] + df.iloc[:, 43] + df.iloc[:, 54] + df.iloc[:, 66] + df.iloc[:, 78] \
                       + df.iloc[:, 99] + df.iloc[:, 111],
        "PD Atipicidad": df.iloc[:, 4] + df.iloc[:, 12] + df.iloc[:, 22] + df.iloc[:, 33] + df.iloc[:, 45] \
                         + df.iloc[:, 55] + df.iloc[:, 68] + df.iloc[:, 80] + df.iloc[:, 89] + df.iloc[:, 101]
                         + df.iloc[:, 113] + df.iloc[:, 122],
        "PD Depresion": df.iloc[:, 5] + df.iloc[:, 14] + df.iloc[:, 23] + df.iloc[:, 35] + df.iloc[:, 47] \
                        + df.iloc[:, 57] + df.iloc[:, 70] + df.iloc[:, 82] + df.iloc[:, 91] + df.iloc[:, 103]
                        + df.iloc[:, 115] + df.iloc[:, 124],
        "PD Hiperactividad": df.iloc[:, 15] + df.iloc[:, 36] + df.iloc[:, 48] + df.iloc[:, 58] + df.iloc[:,71] \
                             + df.iloc[:, 83] + df.iloc[:, 104] + df.iloc[:, 116] + df.iloc[:, 132],
        "PD Habilidades sociales": df.iloc[:, 7] + df.iloc[:, 17] + df.iloc[:, 26] + df.iloc[:, 38] + df.iloc[:, 50]\
                                   + df.iloc[:, 60] + df.iloc[:, 73] + df.iloc[:, 85] + df.iloc[:, 94] + df.iloc[:, 96]
                                   + df.iloc[:, 106] + df.iloc[:, 118] + df.iloc[:, 126] + df.iloc[:, 128],
        "PD Problemas de atencion": (3 - df.iloc[:, 3]) + df.iloc[:, 32] + df.iloc[:, 44] + df.iloc[:, 67] + \
                                    (3 - df.iloc[:, 79]) + (3 -df.iloc[:, 100]) + (3 -df.iloc[:, 112]),
        "PD Retraimiento": (3 -df.iloc[:, 9]) + df.iloc[:, 19] + df.iloc[:, 40] + df.iloc[:, 52] + df.iloc[:, 75]\
                           + df.iloc[:, 87] + df.iloc[:, 108] + df.iloc[:, 120] + df.iloc[:, 133],
        "PD Somatizacion": df.iloc[:, 8] + df.iloc[:, 18] + df.iloc[:, 27] + df.iloc[:, 39] + df.iloc[:, 51] \
                           + df.iloc[:, 61] + df.iloc[:, 63] + df.iloc[:, 74] + df.iloc[:, 86] + df.iloc[:, 95]
                           + df.iloc[:, 107] + df.iloc[:, 119] + df.iloc[:, 127],
        "PD Problemas de conducta": df.iloc[:, 13] + df.iloc[:, 34] + df.iloc[:, 46] + df.iloc[:, 102] + df.iloc[:, 56] \
                           + df.iloc[:, 69] + df.iloc[:, 81] + df.iloc[:, 90] + df.iloc[:, 114] + df.iloc[:, 131],
        "PD Liderazgo": df.iloc[:, 6] + df.iloc[:, 16] + df.iloc[:, 37] + df.iloc[:, 49] + df.iloc[:, 59] \
                           + df.iloc[:, 72] + df.iloc[:, 84] + df.iloc[:, 93] + df.iloc[:, 105] + df.iloc[:, 117],

    }

    # inicio=time.time()
    # Convertir a lista los baremos, edad y los puntajes directos de cada dimensión
    df_puntaje = pd.DataFrame(puntaje_directo)
    #Se une el dataframe de la info y los puntajes
    df_unido = pd.concat([df_info, df_puntaje], axis=1)
    baremo1 = df_info['Baremo'].values.tolist()
    df_t = get_value_t_p2(df_unido, baremo1)
    """
    
    edad1 = df_info['Edad'].values.tolist()

    
    adaptabilidad = df_puntaje['PD Adaptabilidad'].values.tolist()
    agresividad = df_puntaje['PD Agresividad'].values.tolist()
    ansiedad = df_puntaje['PD Ansiedad'].values.tolist()
    atipicidad = df_puntaje['PD Atipicidad'].values.tolist()
    depresion = df_puntaje['PD Depresion'].values.tolist()
    hiperactividad = df_puntaje['PD Hiperactividad'].values.tolist()
    habilidades_sociales = df_puntaje['PD Habilidades sociales'].values.tolist()
    problemas_atencion = df_puntaje['PD Problemas de atencion'].values.tolist()
    retraimiento = df_puntaje['PD Retraimiento'].values.tolist()
    somatizacion = df_puntaje['PD Somatizacion'].values.tolist()
    problemas_conducta = df_puntaje['PD Problemas de conducta'].values.tolist()
    liderazgo = df_puntaje['PD Liderazgo'].values.tolist()

    # Declarar una variable para los valores de una columna en base a la funcion puntaje_p1
    somatizacion_valores = puntaje_p2(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Somatización')

    # Crear un diccionario con el nombre de las columnas y los puntajes T
    puntaje_T = {
        "T Agresividad": puntaje_p2(agresividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Agresividad'),
        "T Adaptabilidad": puntaje_p2(adaptabilidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Adaptabilidad'),
        "T Ansiedad": puntaje_p2(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_p2(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_p2(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Hiperactividad": puntaje_p2(hiperactividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Hiperactividad'),
        "T Habilidades sociales": puntaje_p2(habilidades_sociales, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                             columna_recuperar='T Habilidades sociales'),
        "T Problemas de atencion": puntaje_p2(problemas_atencion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de atención'),
        "T Retraimiento": puntaje_p2(retraimiento, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Retraimiento'),
        "T Somatizacion": somatizacion_valores,
        "T Problemas de conducta": puntaje_p2(problemas_conducta, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Problemas de conducta'),
        "T Liderazgo": puntaje_p2(liderazgo, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Liderazgo'),
    }
    # Se convierte a dataframe el diccionario creado anteriormente
    df_T = pd.DataFrame(puntaje_T)"""
    # print(time.time()-inicio)

    # Se resetea los indices de todos los dataframes
    df_info = df_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df_puntaje = df_puntaje.reset_index(drop=True)
    df_t = df_t.reset_index(drop=True)
    df_info_filtrado = df_info.loc[:, ['1', 'Nombre y apellido', 'Edad', 'Baremo']]
    # Se unen todos los dataframes
    df_final = pd.concat([df_info_filtrado, df_puntaje, df_t], axis=1)
    prueba = "P2"
    # Se generan las columnas de los niveles basados en el puntaje T con la funcion niveles_all()
    niveles_all(df_final, prueba="P2")
    df_final.iloc[:, 0] = df_final.iloc[:, 0].map(int)
    df_final.rename(columns={'1': 'Id'}, inplace=True)
    df_final = df_final.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                         'PD Adaptabilidad', 'T Adaptabilidad', 'Nivel Adaptabilidad',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                         'PD Habilidades sociales', 'T Habilidades sociales',
                                         'Nivel Habilidades sociales',
                                         'PD Problemas de atencion', 'T Problemas de atencion',
                                         'Nivel Problemas de atencion',
                                         'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                         'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion',
                                         'PD Problemas de conducta', 'T Problemas de conducta', 'Nivel Problemas de conducta',
                                         'PD Liderazgo', 'T Liderazgo', 'Nivel Liderazgo'])
    # Guardar en csv
    # df_final.to_csv('resultados1.csv', encoding='utf-8')
    return df_final


def dataframe_p1():
    # Se declara la url de la cual se va a leer los datos
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRsel6HneM_DSW0LGJf-GCDAmKXIMk2hMgHcefQ0B5GlwwlCBgyhhiEYUSvY4fMMqC5Y2u7d4ExiImH/pubhtml"
    df = dataframe_calculos_iniciales(url)
    # df = recodifica_var(len(df.columns))
    df_info = df.iloc[:, :11]
    df = df.iloc[:, 11:]
    # Se calculan los puntajes directos
    puntaje_directo = {
        "PD Agresividad": df.iloc[:, 1] + df.iloc[:, 11] + df.iloc[:, 19] + df.iloc[:, 27] + df.iloc[:, 31]\
                          + df.iloc[:,42] + df.iloc[:,52] + df.iloc[:,64] + df.iloc[:,75] + df.iloc[:,85] \
                          + df.iloc[:,96] + df.iloc[:,105] + df.iloc[:,115],
        "PD Adaptabilidad": df.iloc[:, 0] + (3 - df.iloc[:, 10]) + (3 - df.iloc[:, 30]) + df.iloc[:, 41]\
                            + df.iloc[:,63] + df.iloc[:,74] + df.iloc[:,84] + (3 - df.iloc[:, 95]) + df.iloc[:, 104]\
                            + df.iloc[:, 114] + df.iloc[:, 125],
        "PD Ansiedad": df.iloc[:, 20] + df.iloc[:, 32] + df.iloc[:, 43] + df.iloc[:, 53] + df.iloc[:, 65] \
                       + df.iloc[:,76] + df.iloc[:, 86] + df.iloc[:, 106] + df.iloc[:, 116],
        "PD Atipicidad": df.iloc[:, 3] + df.iloc[:, 13] + df.iloc[:, 21] + df.iloc[:, 34] + df.iloc[:, 45] \
                         + df.iloc[:, 54] + df.iloc[:, 67] + df.iloc[:, 78] + df.iloc[:, 87] + df.iloc[:, 108] \
                         + df.iloc[:, 117],
        "PD Depresion": df.iloc[:, 4] + df.iloc[:, 14] + df.iloc[:, 22] + df.iloc[:, 35] + df.iloc[:, 46]\
                        + df.iloc[:,55] + df.iloc[:, 60] + df.iloc[:, 68] + df.iloc[:, 79] + df.iloc[:, 88] \
                        + df.iloc[:, 98] + df.iloc[:, 109] + df.iloc[:, 118],
        "PD Hiperactividad": df.iloc[:, 5] + df.iloc[:, 15] + df.iloc[:, 23] + df.iloc[:, 28] + df.iloc[:, 36] \
                             + df.iloc[:, 47] + df.iloc[:, 56] + df.iloc[:, 61] + df.iloc[:, 69] + df.iloc[:, 80]\
                             + df.iloc[:, 93] + df.iloc[:, 99] + df.iloc[:, 110] + df.iloc[:, 119] + df.iloc[:, 124]\
                             + df.iloc[:, 127],
        "PD Habilidades sociales": df.iloc[:, 6] + df.iloc[:, 16] + df.iloc[:, 24] + df.iloc[:, 37] + df.iloc[:, 48]\
                                   + df.iloc[:, 57] + df.iloc[:, 70] + df.iloc[:, 81] + df.iloc[:, 90]\
                                   + df.iloc[:, 100]+ df.iloc[:, 111] + df.iloc[:, 120] + df.iloc[:, 123]\
                                   + df.iloc[:, 129],
        "PD Problemas de atencion": df.iloc[:, 2] + (3 - df.iloc[:, 33]) + df.iloc[:, 44] + df.iloc[:, 66]\
                                    + df.iloc[:, 77] + df.iloc[:, 97] + df.iloc[:, 107] + df.iloc[:, 126],
        "PD Retraimiento": df.iloc[:, 8] + df.iloc[:, 39] + df.iloc[:, 50] + df.iloc[:, 59] + df.iloc[:, 72]\
                           + df.iloc[:, 83] + df.iloc[:, 92] + (3 - df.iloc[:, 102]) + df.iloc[:, 113] + \
                           df.iloc[:, 122] + df.iloc[:, 128],
        "PD Somatizacion": df.iloc[:, 7] + df.iloc[:, 17] + df.iloc[:, 25] + df.iloc[:, 29] + df.iloc[:, 38] \
                           + df.iloc[:, 49] + df.iloc[:, 58] + df.iloc[:, 62] + df.iloc[:, 71] + df.iloc[:, 82]\
                           + df.iloc[:, 91] + df.iloc[:, 101] + df.iloc[:, 112] + df.iloc[:, 121],

    }

    # inicio=time.time()
    # Convertir a lista los baremos, edad y los puntajes directos de cada dimensión
    baremo1 = df_info['Baremo'].values.tolist()
    edad1 = df_info['Edad'].values.tolist()
    df_puntaje = pd.DataFrame(puntaje_directo)
    adaptabilidad = df_puntaje['PD Adaptabilidad'].values.tolist()
    agresividad = df_puntaje['PD Agresividad'].values.tolist()
    ansiedad = df_puntaje['PD Ansiedad'].values.tolist()
    atipicidad = df_puntaje['PD Atipicidad'].values.tolist()
    depresion = df_puntaje['PD Depresion'].values.tolist()
    hiperactividad = df_puntaje['PD Hiperactividad'].values.tolist()
    habilidades_sociales = df_puntaje['PD Habilidades sociales'].values.tolist()
    problemas_atencion = df_puntaje['PD Problemas de atencion'].values.tolist()
    retraimiento = df_puntaje['PD Retraimiento'].values.tolist()
    somatizacion = df_puntaje['PD Somatizacion'].values.tolist()

    # Declarar una variable para los valores de una columna en base a la funcion puntaje_p1
    somatizacion_valores = puntaje_p1(somatizacion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Somatización')

    # Crear un diccionario con el nombre de las columnas y los puntajes T
    puntaje_T = {
        "T Agresividad": puntaje_p1(agresividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                    columna_recuperar='T Agresividad'),
        "T Adaptabilidad": puntaje_p1(adaptabilidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                      columna_recuperar='T Adaptabilidad'),
        "T Ansiedad": puntaje_p1(ansiedad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                 columna_recuperar='T Ansiedad'),
        "T Atipicidad": puntaje_p1(atipicidad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                   columna_recuperar='T Atipicidad'),
        "T Depresion": puntaje_p1(depresion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                  columna_recuperar='T Depresión'),
        "T Hiperactividad": puntaje_p1(hiperactividad, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                       columna_recuperar='T Hiperactividad'),
        "T Habilidades sociales": puntaje_p1(habilidades_sociales, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                             columna_recuperar='T Habilidades sociales'),
        "T Problemas de atencion": puntaje_p1(problemas_atencion, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                              columna_recuperar='T Problemas de atención'),
        "T Retraimiento": puntaje_p1(retraimiento, edades=edad1, baremos=baremo1, columna_comparar='PD',
                                     columna_recuperar='T Retraimiento'),
        "T Somatizacion": somatizacion_valores,
    }
    # Se convierte a dataframe el diccionario creado anteriormente
    df_T = pd.DataFrame(puntaje_T)
    # print(time.time()-inicio)

    # Se resetea los indices de todos los dataframes
    df_info = df_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    df_puntaje = df_puntaje.reset_index(drop=True)
    df_T = df_T.reset_index(drop=True)
    df_info_filtrado = df_info.loc[:, ['1', 'Nombre y apellido', 'Edad', 'Baremo']]
    # Se unen todos los dataframes
    df_final = pd.concat([df_info_filtrado, df_puntaje, df_T], axis=1)
    prueba = "P1"
    # Se generan las columnas de los niveles basados en el puntaje T con la funcion niveles_all()
    niveles_all(df_final)
    df_final.iloc[:, 0] = df_final.iloc[:, 0].map(int)
    df_final.rename(columns={'1': 'Id'}, inplace=True)
    df_final = df_final.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                         'PD Adaptabilidad', 'T Adaptabilidad', 'Nivel Adaptabilidad',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                         'PD Habilidades sociales', 'T Habilidades sociales',
                                         'Nivel Habilidades sociales',
                                         'PD Problemas de atencion', 'T Problemas de atencion',
                                         'Nivel Problemas de atencion',
                                         'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                         'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion'])
    # Guardar en csv
    # df_final.to_csv('resultados1.csv', encoding='utf-8')
    return df_final


def cambio_baremo_one_p1(df3, p1_id, baremo_p2):
    datos = df3['Id'] == p1_id
    dato_filtrado = df3[datos]
    if len(dato_filtrado) > 0:
        dat_valor_t = get_value_t_p2(dato_filtrado, bare=baremo_p2)
        niveles_all(dat_valor_t)
        datos_gral = dato_filtrado.loc[:, ['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                           'PD Agresividad', 'PD Adaptabilidad',
                                           'PD Ansiedad', 'PD Atipicidad', 'PD Depresion',
                                           'PD Hiperactividad', 'PD Habilidades sociales',
                                           'PD Problemas de atencion', 'PD Retraimiento',
                                           'PD Somatizacion']]
        datos_gral = datos_gral.reset_index(drop=True)
        dat_valor_t = dat_valor_t.reset_index(drop=True)
        df_final_p1 = pd.concat([datos_gral, dat_valor_t], axis=1)

        df_final_p1.iloc[0, 3] = baremo_p2
        df_final_p1 = df_final_p1.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                                   'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                                   'PD Adaptabilidad', 'T Adaptabilidad', 'Nivel Adaptabilidad',
                                                   'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                                   'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                                   'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                                   'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                                   'PD Habilidades sociales', 'T Habilidades sociales',
                                                   'Nivel Habilidades sociales',
                                                   'PD Problemas de atencion', 'T Problemas de atencion',
                                                   'Nivel Problemas de atencion',
                                                   'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                                   'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion'])

        df3.iloc[p1_id - 2, :] = df_final_p1.iloc[0, :]
    return df3


def cambio_baremo_one_p2(df3, p2_id, baremo_p1):
    datos = df3['Id'] == p2_id
    dato_filtrado = df3[datos]
    if len(dato_filtrado) > 0:
        dat_valor_t = get_value_t_p2(dato_filtrado, bare=baremo_p1)
        niveles_all(dat_valor_t, prueba="P2")
        datos_gral = dato_filtrado.loc[:, ['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                           'PD Agresividad', 'PD Adaptabilidad',
                                           'PD Ansiedad', 'PD Atipicidad', 'PD Depresion',
                                           'PD Hiperactividad', 'PD Habilidades sociales',
                                           'PD Problemas de atencion', 'PD Retraimiento',
                                           'PD Somatizacion', 'PD Problemas de conducta',
                                           'PD Liderazgo']]
        datos_gral = datos_gral.reset_index(drop=True)
        dat_valor_t = dat_valor_t.reset_index(drop=True)
        df_final_p1 = pd.concat([datos_gral, dat_valor_t], axis=1)

        df_final_p1.iloc[0, 3] = baremo_p1[0]
        df_final_p1 = df_final_p1.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                         'PD Adaptabilidad', 'T Adaptabilidad', 'Nivel Adaptabilidad',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                         'PD Habilidades sociales', 'T Habilidades sociales',
                                         'Nivel Habilidades sociales',
                                         'PD Problemas de atencion', 'T Problemas de atencion',
                                         'Nivel Problemas de atencion',
                                         'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                         'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion',
                                         'PD Problemas de conducta', 'T Problemas de conducta', 'Nivel Problemas de conducta',
                                         'PD Liderazgo', 'T Liderazgo', 'Nivel Liderazgo'])

        df3.iloc[p2_id - 2, :] = df_final_p1.iloc[0, :]
    return df3


def cambio_baremo_one_p3(df3, p3_id, baremo_p3):
    datos = df3['Id'] == p3_id
    dato_filtrado = df3[datos]
    if len(dato_filtrado) > 0:
        dat_valor_t = get_value_t_p3(dato_filtrado, bare=baremo_p3)
        niveles_all(dat_valor_t, prueba="P3")
        datos_gral = dato_filtrado.loc[:, ['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                           'PD Agresividad','PD Ansiedad', 'PD Atipicidad',
                                           'PD Depresion','PD Hiperactividad',
                                           'PD Habilidades sociales', 'PD Problemas de atencion',
                                           'PD Retraimiento', 'PD Somatizacion',
                                           'PD Problemas de conducta', 'PD Liderazgo']]
        datos_gral = datos_gral.reset_index(drop=True)
        dat_valor_t = dat_valor_t.reset_index(drop=True)
        df_final_p1 = pd.concat([datos_gral, dat_valor_t], axis=1)

        df_final_p1.iloc[0, 3] = baremo_p3[0]
        df_final_p1 = df_final_p1.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                                   'PD Agresividad', 'T Agresividad', 'Nivel Agresividad',
                                                   'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                                   'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                                   'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                                   'PD Hiperactividad', 'T Hiperactividad', 'Nivel Hiperactividad',
                                                   'PD Habilidades sociales', 'T Habilidades sociales',
                                                   'Nivel Habilidades sociales',
                                                   'PD Problemas de atencion', 'T Problemas de atencion',
                                                   'Nivel Problemas de atencion',
                                                   'PD Retraimiento', 'T Retraimiento', 'Nivel Retraimiento',
                                                   'PD Somatizacion', 'T Somatizacion', 'Nivel Somatizacion',
                                                   'PD Problemas de conducta', 'T Problemas de conducta',
                                                   'Nivel Problemas de conducta',
                                                   'PD Liderazgo', 'T Liderazgo', 'Nivel Liderazgo',])

        df3.iloc[p3_id - 2, :] = df_final_p1.iloc[0, :]
    return df3


def cambio_baremo_one_s2(df3, s2_id, baremo_s2):
    datos = df3['Id'] == s2_id
    dato_filtrado = df3[datos]
    if len(dato_filtrado) > 0:
        dat_valor_t = get_value_t_s2(dato_filtrado, bare=baremo_s2)
        niveles_all(dat_valor_t,prueba="S2")
        datos_gral = dato_filtrado.loc[:, ['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                           'PD Actitud negativa hacia el colegio',
                                           'PD Actitud negativa hacia los profesores', 'PD Ansiedad', 'PD Atipicidad',
                                           'PD Depresion','PD Locus de control',
                                           'PD Estres social', 'PD Sentido de incapacidad',
                                           'PD Relaciones interpersonales',
                                           'PD Relaciones con los padres', 'PD Autoestima',
                                           'PD Confianza en si mismo']]
        datos_gral = datos_gral.reset_index(drop=True)
        dat_valor_t = dat_valor_t.reset_index(drop=True)
        df_final_p1 = pd.concat([datos_gral, dat_valor_t], axis=1)

        df_final_p1.iloc[0, 3] = baremo_s2[0]
        df_final_p1 = df_final_p1.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                                   'PD Actitud negativa hacia el colegio',
                                                   'T Actitud negativa hacia el colegio',
                                                   'Nivel Actitud negativa hacia el colegio',
                                                   'PD Actitud negativa hacia los profesores',
                                                   'T Actitud negativa hacia los profesores',
                                                   'Nivel Actitud negativa hacia los profesores',
                                                   'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                                   'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                                   'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                                   'PD Locus de control', 'T Locus de control', 'Nivel Locus de control',
                                                   'PD Estres social', 'T Estres social',
                                                   'Nivel Estres social',
                                                   'PD Sentido de incapacidad', 'T Sentido de incapacidad',
                                                   'Nivel Sentido de incapacidad',
                                                   'PD Relaciones interpersonales', 'T Relaciones interpersonales',
                                                   'Nivel Relaciones interpersonales',
                                                   'PD Relaciones con los padres', 'T Relaciones con los padres',
                                                   'Nivel Relaciones con los padres',
                                                   'PD Autoestima', 'T Autoestima', 'Nivel Autoestima',
                                                   'PD Confianza en si mismo', 'T Confianza en si mismo',
                                                   'Nivel Confianza en si mismo'])

        df3.iloc[s2_id - 2, :] = df_final_p1.iloc[0, :]
    return df3


def cambio_baremo_one_s3(df3, s3_id, baremo_s3):
    datos = df3['Id'] == s3_id
    dato_filtrado = df3[datos]

    if len(dato_filtrado) > 0:
        dat_valor_t = get_value_t_s3(dato_filtrado, bare=baremo_s3)
        niveles_all(dat_valor_t, prueba="S3")
        datos_gral = dato_filtrado.loc[:, ['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                           'PD Actitud negativa hacia el colegio',
                                           'PD Actitud negativa hacia los profesores', 'PD Ansiedad', 'PD Atipicidad',
                                           'PD Depresion','PD Locus de control',
                                           'PD Estres social', 'PD Sentido de incapacidad',
                                           'PD Relaciones interpersonales', 'PD Somatizacion',
                                           'PD Relaciones con los padres', 'PD Autoestima',
                                           'PD Confianza en si mismo', 'PD Busqueda de sensaciones']]
        datos_gral = datos_gral.reset_index(drop=True)
        dat_valor_t = dat_valor_t.reset_index(drop=True)
        df_final_p1 = pd.concat([datos_gral, dat_valor_t], axis=1)

        df_final_p1.iloc[0, 3] = baremo_s3[0]
        df_final_p1 = df_final_p1.reindex(columns=['Id', 'Nombre y apellido', 'Edad', 'Baremo',
                                         'PD Actitud negativa hacia el colegio', 'T Actitud negativa hacia el colegio',
                                         'Nivel Actitud negativa hacia el colegio',
                                         'PD Actitud negativa hacia los profesores',
                                         'T Actitud negativa hacia los profesores',
                                         'Nivel Actitud negativa hacia los profesores',
                                         'PD Ansiedad', 'T Ansiedad', 'Nivel Ansiedad',
                                         'PD Atipicidad', 'T Atipicidad', 'Nivel Atipicidad',
                                         'PD Depresion', 'T Depresion', 'Nivel Depresion',
                                         'PD Locus de control', 'T Locus de control', 'Nivel Locus de control',
                                         'PD Estres social', 'T Estres social',
                                         'Nivel Estres social',
                                         'PD Sentido de incapacidad', 'T Sentido de incapacidad',
                                         'Nivel Sentido de incapacidad',
                                         'PD Relaciones interpersonales', 'T Relaciones interpersonales',
                                         'Nivel Relaciones interpersonales',
                                         'PD Relaciones con los padres', 'T Relaciones con los padres',
                                         'Nivel Relaciones con los padres',
                                         'PD Autoestima', 'T Autoestima',
                                         'Nivel Autoestima',
                                         'PD Confianza en si mismo', 'T Confianza en si mismo',
                                         'Nivel Confianza en si mismo',
                                         'PD Busqueda de sensaciones', 'T Busqueda de sensaciones',
                                         'Nivel Busqueda de sensaciones',
                                         'PD Somatizacion', 'T Somatizacion',
                                         'Nivel Somatizacion'])

        df3.iloc[s3_id - 2, :] = df_final_p1.iloc[0, :]
    return df3


def p1_dict_one(df_gral, datos_cambiados, p1_id):
    datos = datos_cambiados['Id'] == p1_id
    dato_filtrado = df_gral[datos]
    if len(dato_filtrado) == 0:
        abort(404, description="Upss! Parece que hubo un error")
    dato_filtrado.columns = dato_filtrado.columns.str.replace(" ", "_")
    dato_dict = dato_filtrado.to_dict('records')
    return dato_dict


if __name__ == '__main__':
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7vGtlwPr73WmlOAKR3lK4223ytE9mQzodJJtABdyewRjeLpc91aJv-9MeGPEzIsJoBfYFG1h_HXJG/pub?output=csv"
    #df = cargar_dataframe(url)
    #df = dataframe_calculos_iniciales(url)
    #df = df.iloc[:, 11:]
    frame_p2 = dataframe_p1()
    """id_p1 = 3
    barem_p1 = "General"
    datos_finales = cambio_baremo_one_p1(frame_p1,id_p1, barem_p1)
    diccionario= p1_dict_one(frame_p1, datos_finales, id_p1)
    dato_filtrados.columns = dato_filtrados.columns.str.replace(" ", "_")
    dato_dict = dato_filtrados.to_dict('records')
    # print(datos_finales)
    # df_pic = pd.read_pickle("baremos/P1_Gral_3_4.pkl")
    # print(df_pic)"""
    #convertir_pickle(archivo="P3_Var_15_16")
    print(frame_p2.columns)
    datos = frame_p2['Id'] == 2
    dato_filtrado = frame_p2[datos]
    name = dato_filtrado['Nombre y apellido'].values[0]
    print(name)
    print(frame_p2.iloc[:, [1,3,4]])
    print(frame_p2.iloc[:, [2]])

