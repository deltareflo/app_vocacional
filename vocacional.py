import bisect
import pandas as pd
import numpy as np
from dataframe_all import cargar_dataframe
import os
import pathlib
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import base64
from io import BytesIO
import matplotlib.font_manager as fm
from models import DatosTestVocacional, TestONet, TestNeoPIR, TestRokeach
import matplotlib as mpl
from matplotlib.figure import Figure
from datetime import datetime

mpl.use('agg')
base_path = pathlib.Path(__file__).resolve().parent


def graf_alt(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    fig = Figure(figsize=(12, 5))
    
    ax = fig.subplots()
    fig.subplots_adjust(top=0.90, bottom=0.08, left=0.11, right=0.85)
    ax.set_title(title,  position=(0.5, 1.1), ha='center')


def grafico_bar_alt(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'  # Fallback
    x = labels
    y = values
    colores = ["#27A612","#C00000","#92D050","#7030A0", "#ED7D31", "#002060"]
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.subplots_adjust(top=0.90, bottom=0.08, left=0.11, right=0.85)
    ax.set_title(title,  position=(0.5, 1.1), ha='center')
    bars = ax.bar(x, y, color=colores)
    #ax.barh(x, width = y, color=colores)
    list_patch = []
    for i in range(len(labels)):
        patch = mpatches.Patch(color=colores[i], label=labels[i])
        list_patch.append(patch)
    #ax.legend(handles=list_patch, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=2)
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    # Add annotation to bars
    """for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5,str(round((i.get_width()))),
                 fontsize=10, fontweight='bold',color='grey')"""
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, str(height),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='grey')
    #ax.set_ylim([0, max(y) + 10])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontproperties=prop, fontweight='bold')
    #ax.set_yticks(np.arange(0, max(y)+11, 5))  # Mostrar ticks cada 5 unidades
    
    #ax.invert_yaxis()
    ax.set_ylim([0,40])
    
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    #plt.xticks([])
    #plt.yticks([])
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png',transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    return graphic


def carga_vocacional(id, ispdf = False):
    df_onet_total, list_onet = carga_onet_db(id)
    df_neo_pi_total, df_datos, lista_neo_dimension = carga_neo_pi_db(id)
    df_rokeach_total = carga_rokeach_db(id)
    label_graf_onet = ['R', 'I', 'A', 'S', 'E', 'C']
    
    label_graf_neo = ['Neuroticismo', 'Extraversión', 'Apertura', 'Amabilidad', 'Responsabilidad']
    label_graf_neo_sub = ['Ansiedad','Hostilidad','Depresión','Ansiedad Social','Impulsividad','Vulnerabilidad','Cordialidad','Gregarismo','Asertividad','Actividad','Busqueda de emociones','Emociones positivas','Fantasía','Estética','Sentimientos','Acciones','Ideas','Valores','Confianza','Franqueza','Altruismo','Actitud conciliadora','Modestia','Sensibilidad a los demás','Competencia','Orden','Sentido del deber','Necesidad de logro','Autodisciplina','Deliberación']
    if ispdf:
        graphic_onet = grafico_bar_pdf(label_graf_onet, list_onet, title="Perfil O*NET")    
        grafico_neo_dimension = grafico_linea_personalidad_pdf(label_graf_neo, lista_neo_dimension[30:], title="Perfil Dimensión global NEOPI-R")
        grafico_neo_subdimension = grafico_linea_subdimension_pdf(label_graf_neo_sub, lista_neo_dimension[:30], title="Perfil Subdimensiones NEOPI-R")
    else:
        graphic_onet = grafico_bar_alt(label_graf_onet, list_onet, title="Perfil O*NET")    
        grafico_neo_dimension = grafico_linea_personalidad(label_graf_neo, lista_neo_dimension[30:], title="Perfil Dimensión global NEOPI-R")
        grafico_neo_subdimension = grafico_linea_subdimension(label_graf_neo_sub, lista_neo_dimension[:30], title="Perfil Subdimensiones NEOPI-R")
    return df_datos, df_onet_total, df_neo_pi_total, df_rokeach_total, graphic_onet, grafico_neo_dimension, grafico_neo_subdimension


def _item_key(col_name):
        try:
            # extraer la parte numérica después del guion bajo
            return int(col_name.split('_', 1)[1])
        except Exception:
            return col_name


def carga_onet_db(id):
    df_onet_inicial = TestONet.query.filter_by(uuid=id).first()
    df_onet_inicial = pd.DataFrame([df_onet_inicial.__dict__])
    # Seleccionar solo las columnas que empiezan por 'item_' y ordenarlas
    item_cols = [col for col in df_onet_inicial.columns if isinstance(col, str) and col.startswith('item_')]
    item_cols_sorted = sorted(item_cols, key=_item_key)
    df_onet = df_onet_inicial[item_cols_sorted]
    df_zona = df_onet_inicial['zona'] if 'zona' in df_onet_inicial.columns else None
    
    df_onet_pd, lista_onet = df_calculo_onet(df_onet, df_zona)
    df_onet_pd["created"] = df_onet_inicial["created"]
    df_onet_pd["uuid"] = df_onet_inicial["uuid"]
    return df_onet_pd, lista_onet


def carga_neo_pi_db(id):
    neo_pi_inicial = TestNeoPIR.query.filter_by(uuid=id).first()
    df_neo_pi_inicial = pd.DataFrame([neo_pi_inicial.__dict__])
    user = int(neo_pi_inicial.id_user)
    data = DatosTestVocacional.query.filter_by(id=neo_pi_inicial.id_user).first()
    if data.sexo == 'M':
        baremo = "Varones"
    elif data.sexo == 'F':
        baremo = "Mujeres"
    else:
        baremo = "General"
    df_data = pd.DataFrame([data.__dict__])
    try:
        # Coerce to Timestamp; df_data['fecha_nacimiento'] may be a single-element Series
        bd = pd.to_datetime(df_data.loc[0, 'fecha_nacimiento'], errors='coerce')
        if pd.isna(bd):
            edad_val = 0
        else:
            today = pd.Timestamp.now().normalize()
            # compute year difference and adjust if birthday hasn't occurred yet this year
            edad_val = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            # guard against negative or absurd values
            if edad_val < 0:
                edad_val = 0
        df_data['edad'] = int(edad_val)
    except Exception:
        # Fallback: if anything unexpected happens, set edad to 0 rather than crashing
        df_data['edad'] = 0
    # Seleccionar solo las columnas que empiezan por 'item_' y ordenarlas
    item_cols = [col for col in df_neo_pi_inicial.columns if isinstance(col, str) and col.startswith('item_')]
    item_cols_sorted = sorted(item_cols, key=_item_key)
    df_neo_pi = df_neo_pi_inicial[item_cols_sorted]
    df_neo_pi_pd, lista_dimensiones = df_calculo_neo_pi(df_neo_pi, baremo)
    return df_neo_pi_pd, df_data, lista_dimensiones


def carga_rokeach_db(id):
    rokeach_inicial = TestRokeach.query.filter_by(uuid=id).first()
    df_rokeach_inicial = pd.DataFrame([rokeach_inicial.__dict__])
    # Seleccionar solo las columnas que empiezan por 'item_' y ordenarlas
    item_cols = [col for col in df_rokeach_inicial.columns if isinstance(col, str) and col.startswith('item_')]
    item_cols_sorted = sorted(item_cols, key=_item_key)
    df_rokeach = df_rokeach_inicial[item_cols_sorted]
    df_rokeach_pd = df_calculo_rokeach(df_rokeach)
    return df_rokeach_pd

def carga_onet(id):
    url ="https://docs.google.com/spreadsheets/d/e/2PACX-1vRRUQM0cyfC0M2jlzV9cwfQ-4L1tjCirLQ9tWLoieXAs6ZwJK_X__Ew-YOUJMMg9BP3A55G2pNm8Knd/pub?output=csv"
    df = cargar_dataframe(url)
    df = df[df['1'] == id]
    info = df.iloc[:,0:9]
    df_onet = df.iloc[:,9:-1]
    df_zona = df.iloc[:,-1]
    df_onet_pd, lista_onet = df_calculo_onet(df_onet, df_zona)
    return df_onet_pd, lista_onet

def carga_neo_pi(id, baremo="General"):
    url ="https://docs.google.com/spreadsheets/d/e/2PACX-1vRXNTEeZii1cRu2M6A6izfKbrPkY1uPdafQofddJG8uxxKd5JpJqQ6nD1ROFD4yb2jPpz06Lsl_CMtF/pub?output=csv"
    df = cargar_dataframe(url)
    df = df[df['1'] == id]
    info = df.iloc[:,0:4]
    df_neo_pi = df.iloc[:,4:]
    df_neo_pi_pd = df_calculo_neo_pi(df_neo_pi, baremo)
    return df_neo_pi_pd

def carga_rokeach(id, baremo="General"):
    url ="https://docs.google.com/spreadsheets/d/e/2PACX-1vRk9bX4Yk3eX1YH"
    df = cargar_dataframe(url)
    df = df[df['1'] == id]
    info = df.iloc[:,0:4]
    df_rokeach = df.iloc[:,4:]
    df_rokeach_pd = df_calculo_rokeach(df_rokeach, baremo)
    return df_rokeach_pd


def df_calculo_onet(df, df_zona):
    # puntaje directo
    pd_onet = {
        "Realista": df.iloc[:, 0] + df.iloc[:, 1] + df.iloc[:, 12] + df.iloc[:, 13] + df.iloc[:, 24] \
                          + df.iloc[:, 25] + df.iloc[:, 36] + df.iloc[:, 37] + df.iloc[:, 48] + df.iloc[:, 49],
        "Investigación": df.iloc[:, 2] + df.iloc[:, 3] + df.iloc[:, 14] + df.iloc[:, 15] + df.iloc[:, 26] \
                          + df.iloc[:, 27] + df.iloc[:, 38] + df.iloc[:, 39] + df.iloc[:, 50] + df.iloc[:, 51],
        "Artístico": df.iloc[:, 4] + df.iloc[:, 5] + df.iloc[:, 16] + df.iloc[:, 17] + df.iloc[:, 28] \
                          + df.iloc[:, 29] + df.iloc[:, 40] + df.iloc[:, 41] + df.iloc[:, 52] + df.iloc[:, 53],
        "Social": df.iloc[:, 6] + df.iloc[:, 7] + df.iloc[:, 18] + df.iloc[:, 19] + df.iloc[:, 30] \
                          + df.iloc[:, 31] + df.iloc[:, 42] + df.iloc[:, 43] + df.iloc[:, 54] + df.iloc[:, 55],
        "Empresarial": df.iloc[:, 8] + df.iloc[:, 9] + df.iloc[:, 20] + df.iloc[:, 21] + df.iloc[:, 32] \
                          + df.iloc[:, 33] + df.iloc[:, 44] + df.iloc[:, 45] + df.iloc[:, 56] + df.iloc[:, 57],
        "Convencional": df.iloc[:, 10] + df.iloc[:, 11] + df.iloc[:, 22] + df.iloc[:, 23] + df.iloc[:, 34] \
                          + df.iloc[:, 35] + df.iloc[:, 46] + df.iloc[:, 47] + df.iloc[:, 58] + df.iloc[:, 59],
    }
    df_pd = pd.DataFrame(pd_onet)
    df_pd = df_pd.fillna(0).astype(int)
    df_pd = df_pd.reset_index(drop=True)
    df_pd_sort = df_pd.sort_values(by=0, axis=1)
    #lista valores para grafico
    list_onet = df_pd.iloc[0].values.tolist()
    

    onet_max_pd = {
        "PD MAX ONET 1": df_pd_sort.iloc[:, -1].values.tolist(),
        "PD MAX ONET 2": df_pd_sort.iloc[:, -2].values.tolist(),
        "PD MAX ONET 3": df_pd_sort.iloc[:, -3].values.tolist(),
    }
    df_onet_max_pd = pd.DataFrame(onet_max_pd)
    onet_max = {
        "Max Onet 1": [df_pd_sort.columns[-1]],
        "Max Onet 2": [df_pd_sort.columns[-2]],
        "Max Onet 3": [df_pd_sort.columns[-3]],
    }
    df_onet_max = pd.DataFrame(onet_max)
    # Descripciones
    onet_max_desc = {
        "Desc Max Onet 1": get_desc(df_onet_max["Max Onet 1"].values.tolist(), "onet_tipos", "Tipo", "Descripcion"),
        "Desc Max Onet 2": get_desc(df_onet_max["Max Onet 2"].values.tolist(), "onet_tipos", "Tipo", "Descripcion"),
        "Desc Max Onet 3": get_desc(df_onet_max["Max Onet 3"].values.tolist(), "onet_tipos", "Tipo", "Descripcion"),
    }
    # Zona
    df_zona = df_zona.fillna(0).astype(int)
    zona_desc = {
        "Desc Zona": get_desc([df_zona.iloc[0]], "zonas_desc", "Zona", "Descripcion"),
        "Tipo Trabajo 1": get_desc(df_onet_max["Max Onet 1"].values.tolist(), "zona_onet", "Tipo", f"{df_zona.iloc[0]}"),
        "Tipo Trabajo 2": get_desc(df_onet_max["Max Onet 2"].values.tolist(), "zona_onet", "Tipo", f"{df_zona.iloc[0]}"),
        "Tipo Trabajo 3": get_desc(df_onet_max["Max Onet 3"].values.tolist(), "zona_onet", "Tipo", f"{df_zona.iloc[0]}"),
    }
    df_zona_desc = pd.DataFrame(zona_desc)
    df_zona_desc = df_zona_desc.reset_index(drop=True)
    df_zona_desc["zona"] = df_zona.iloc[0]
    df_onet_max_desc = pd.DataFrame(onet_max_desc)
    df_onet_max = pd.concat([df_pd,df_onet_max_pd, df_onet_max, df_onet_max_desc, df_zona_desc], axis=1)

    return df_onet_max, list_onet


def get_desc(valores, baremo, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):
        df2 = pd.read_pickle(os.path.join('baremos', f'{baremo}.pkl'))
        
        try:
            value = int(valores[j])
            df2 = df2.loc[df2[columna_comparar] == value, [columna_recuperar]]
        except ValueError:
            df2 = df2.loc[df2[columna_comparar] == valores[j], [columna_recuperar]]
        df2 = df2.values.tolist()
        try:
            resultado.append(df2[0][0])
        except IndexError:
            resultado.append("-")
    
    return resultado

def df_calculo_neo_pi(df, df_baremo):
    # Puntaje Neo PI
    neopi_pd = {
        "N1": df.iloc[:, 0] + df.iloc[:, 30] + df.iloc[:, 60] + df.iloc[:, 90] + df.iloc[:, 120]\
            + df.iloc[:,150] + df.iloc[:,180] + df.iloc[:,210],
        "E1": df.iloc[:, 1] + df.iloc[:, 31] + df.iloc[:, 61] + df.iloc[:, 91] + df.iloc[:, 121]\
            + df.iloc[:,151] + df.iloc[:,181] + df.iloc[:,211],
        "O1": df.iloc[:, 2] + df.iloc[:, 32] + df.iloc[:, 62] + df.iloc[:, 92] + df.iloc[:, 122]\
            + df.iloc[:,152] + df.iloc[:,182] + df.iloc[:,212],
        "A1": df.iloc[:, 3] + df.iloc[:, 33] + df.iloc[:, 63] + df.iloc[:, 93] + df.iloc[:, 123]\
            + df.iloc[:,153] + df.iloc[:,183] + df.iloc[:,213],
        "C1": df.iloc[:, 4] + df.iloc[:, 34] + df.iloc[:, 64] + df.iloc[:, 94] + df.iloc[:, 124]\
            + df.iloc[:,154] + df.iloc[:,184] + df.iloc[:,214],
        "N2": df.iloc[:, 5] + df.iloc[:, 35] + df.iloc[:, 65] + df.iloc[:, 95] + df.iloc[:, 125]\
            + df.iloc[:,155] + df.iloc[:,185] + df.iloc[:,215],
        "E2": df.iloc[:, 6] + df.iloc[:, 36] + df.iloc[:, 66] + df.iloc[:, 96] + df.iloc[:, 126]\
            + df.iloc[:,156] + df.iloc[:,186] + df.iloc[:,216],
        "O2": df.iloc[:, 7] + df.iloc[:, 37] + df.iloc[:, 67] + df.iloc[:, 97] + df.iloc[:, 127]\
            + df.iloc[:,157] + df.iloc[:,187] + df.iloc[:,217],
        "A2": df.iloc[:, 8] + df.iloc[:, 38] + df.iloc[:, 68] + df.iloc[:, 98] + df.iloc[:, 128]\
            + df.iloc[:,158] + df.iloc[:,188] + df.iloc[:,218],
        "C2": df.iloc[:, 9] + df.iloc[:, 39] + df.iloc[:, 69] + df.iloc[:, 99] + df.iloc[:, 129]\
            + df.iloc[:,159] + df.iloc[:,189] + df.iloc[:,219],
        "N3": df.iloc[:, 10] + df.iloc[:, 40] + df.iloc[:, 70] + df.iloc[:, 100] + df.iloc[:, 130]\
            + df.iloc[:,160] + df.iloc[:,190] + df.iloc[:,220],
        "E3": df.iloc[:, 11] + df.iloc[:, 41] + df.iloc[:, 71] + df.iloc[:, 101] + df.iloc[:, 131]\
            + df.iloc[:,161] + df.iloc[:,191] + df.iloc[:,221],
        "O3": df.iloc[:, 12] + df.iloc[:, 42] + df.iloc[:, 72] + df.iloc[:, 102] + df.iloc[:, 132]\
            + df.iloc[:,162] + df.iloc[:,192] + df.iloc[:,222],
        "A3": df.iloc[:, 13] + df.iloc[:, 43] + df.iloc[:, 73] + df.iloc[:, 103] + df.iloc[:, 133]\
            + df.iloc[:,163] + df.iloc[:,193] + df.iloc[:,223],
        "C3": df.iloc[:, 14] + df.iloc[:, 44] + df.iloc[:, 74] + df.iloc[:, 104] + df.iloc[:, 134]\
            + df.iloc[:,164] + df.iloc[:,194] + df.iloc[:,224],
        "N4": df.iloc[:, 15] + df.iloc[:, 45] + df.iloc[:, 75] + df.iloc[:, 105] + df.iloc[:, 135]\
            + df.iloc[:,165] + df.iloc[:,195] + df.iloc[:,225],
        "E4": df.iloc[:, 16] + df.iloc[:, 46] + df.iloc[:, 76] + df.iloc[:, 106] + df.iloc[:, 136]\
            + df.iloc[:,166] + df.iloc[:,196] + df.iloc[:,226],
        "O4": df.iloc[:, 17] + df.iloc[:, 47] + df.iloc[:, 77] + df.iloc[:, 107] + df.iloc[:, 137]\
            + df.iloc[:,167] + df.iloc[:,197] + df.iloc[:,227],
        "A4": df.iloc[:, 18] + df.iloc[:, 48] + df.iloc[:, 78] + df.iloc[:, 108] + df.iloc[:, 138]\
            + df.iloc[:,168] + df.iloc[:,198] + df.iloc[:,228],
        "C4": df.iloc[:, 19] + df.iloc[:, 49] + df.iloc[:, 79] + df.iloc[:, 109] + df.iloc[:, 139]\
            + df.iloc[:,169] + df.iloc[:,199] + df.iloc[:,229],
        "N5": df.iloc[:, 20] + df.iloc[:, 50] + df.iloc[:, 80] + df.iloc[:, 110] + df.iloc[:, 140]\
            + df.iloc[:,170] + df.iloc[:,200] + df.iloc[:,230],
        "E5": df.iloc[:, 21] + df.iloc[:, 51] + df.iloc[:, 81] + df.iloc[:, 111] + df.iloc[:, 141]\
            + df.iloc[:,171] + df.iloc[:,201] + df.iloc[:,231],
        "O5": df.iloc[:, 22] + df.iloc[:, 52] + df.iloc[:, 82] + df.iloc[:, 112] + df.iloc[:, 142]\
            + df.iloc[:,172] + df.iloc[:,202] + df.iloc[:,232],
        "A5": df.iloc[:, 23] + df.iloc[:, 53] + df.iloc[:, 83] + df.iloc[:, 113] + df.iloc[:, 143]\
            + df.iloc[:,173] + df.iloc[:,203] + df.iloc[:,233],
        "C5": df.iloc[:, 24] + df.iloc[:, 54] + df.iloc[:, 84] + df.iloc[:, 114] + df.iloc[:, 144]\
            + df.iloc[:,174] + df.iloc[:,204] + df.iloc[:,234],
        "N6": df.iloc[:, 25] + df.iloc[:, 55] + df.iloc[:, 85] + df.iloc[:, 115] + df.iloc[:, 145]\
            + df.iloc[:,175] + df.iloc[:,205] + df.iloc[:,235],
        "E6": df.iloc[:, 26] + df.iloc[:, 56] + df.iloc[:, 86] + df.iloc[:, 116] + df.iloc[:, 146]\
            + df.iloc[:,176] + df.iloc[:,206] + df.iloc[:,236],
        "O6": df.iloc[:, 27] + df.iloc[:, 57] + df.iloc[:, 87] + df.iloc[:, 117] + df.iloc[:, 147]\
            + df.iloc[:,177] + df.iloc[:,207] + df.iloc[:,237],
        "A6": df.iloc[:, 28] + df.iloc[:, 58] + df.iloc[:, 88] + df.iloc[:, 118] + df.iloc[:, 148]\
            + df.iloc[:,178] + df.iloc[:,208] + df.iloc[:,238],
        "C6": df.iloc[:, 29] + df.iloc[:, 59] + df.iloc[:, 89] + df.iloc[:, 119] + df.iloc[:, 149]\
            + df.iloc[:,179] + df.iloc[:,209] + df.iloc[:,239],
    }
    df_pd_neo = pd.DataFrame(neopi_pd)
    perfil_neo = {
        "NNEO": df_pd_neo["N1"] + df_pd_neo["N2"] + df_pd_neo["N3"] + df_pd_neo["N4"] + df_pd_neo["N5"] + df_pd_neo["N6"],
        "ENEO": df_pd_neo["E1"] + df_pd_neo["E2"] + df_pd_neo["E3"] + df_pd_neo["E4"] + df_pd_neo["E5"] + df_pd_neo["E6"],
        "ONEO": df_pd_neo["O1"] + df_pd_neo["O2"] + df_pd_neo["O3"] + df_pd_neo["O4"] + df_pd_neo["O5"] + df_pd_neo["O6"],
        "ANEO": df_pd_neo["A1"] + df_pd_neo["A2"] + df_pd_neo["A3"] + df_pd_neo["A4"] + df_pd_neo["A5"] + df_pd_neo["A6"],
        "CNEO": df_pd_neo["C1"] + df_pd_neo["C2"] + df_pd_neo["C3"] + df_pd_neo["C4"] + df_pd_neo["C5"] + df_pd_neo["C6"],
    }
    df_perfil_neo = pd.DataFrame(perfil_neo)
    pc_neo_pi = {
        "PC N1": get_pc_t(df_pd_neo["N1"].values.tolist(), df_baremo,'N', 'N1', 'Pc'),
        "PC E1": get_pc_t(df_pd_neo["E1"].values.tolist(), df_baremo,'E', 'E1', 'Pc'),
        "PC O1": get_pc_t(df_pd_neo["O1"].values.tolist(), df_baremo,'O', 'O1', 'Pc'),
        "PC A1": get_pc_t(df_pd_neo["A1"].values.tolist(), df_baremo,'A', 'A1', 'Pc'),
        "PC C1": get_pc_t(df_pd_neo["C1"].values.tolist(), df_baremo,'C', 'C1', 'Pc'),
        "PC N2": get_pc_t(df_pd_neo["N2"].values.tolist(), df_baremo,'N', 'N2', 'Pc'),
        "PC E2": get_pc_t(df_pd_neo["E2"].values.tolist(), df_baremo,'E', 'E2', 'Pc'),
        "PC O2": get_pc_t(df_pd_neo["O2"].values.tolist(), df_baremo,'O', 'O2', 'Pc'),
        "PC A2": get_pc_t(df_pd_neo["A2"].values.tolist(), df_baremo,'A', 'A2', 'Pc'),
        "PC C2": get_pc_t(df_pd_neo["C2"].values.tolist(), df_baremo,'C', 'C2', 'Pc'),
        "PC N3": get_pc_t(df_pd_neo["N3"].values.tolist(), df_baremo,'N', 'N3', 'Pc'),
        "PC E3": get_pc_t(df_pd_neo["E3"].values.tolist(), df_baremo,'E', 'E3', 'Pc'),
        "PC O3": get_pc_t(df_pd_neo["O3"].values.tolist(), df_baremo,'O', 'O3', 'Pc'),
        "PC A3": get_pc_t(df_pd_neo["A3"].values.tolist(), df_baremo,'A', 'A3', 'Pc'),
        "PC C3": get_pc_t(df_pd_neo["C3"].values.tolist(), df_baremo,'C', 'C3', 'Pc'),
        "PC N4": get_pc_t(df_pd_neo["N4"].values.tolist(), df_baremo,'N', 'N4', 'Pc'),
        "PC E4": get_pc_t(df_pd_neo["E4"].values.tolist(), df_baremo,'E', 'E4', 'Pc'),
        "PC O4": get_pc_t(df_pd_neo["O4"].values.tolist(), df_baremo,'O', 'O4', 'Pc'),
        "PC A4": get_pc_t(df_pd_neo["A4"].values.tolist(), df_baremo,'A', 'A4', 'Pc'),
        "PC C4": get_pc_t(df_pd_neo["C4"].values.tolist(), df_baremo,'C', 'C4', 'Pc'),
        "PC N5": get_pc_t(df_pd_neo["N5"].values.tolist(), df_baremo,'N', 'N5', 'Pc'),
        "PC E5": get_pc_t(df_pd_neo["E5"].values.tolist(), df_baremo,'E', 'E5', 'Pc'),
        "PC O5": get_pc_t(df_pd_neo["O5"].values.tolist(), df_baremo,'O', 'O5', 'Pc'),
        "PC A5": get_pc_t(df_pd_neo["A5"].values.tolist(), df_baremo,'A', 'A5', 'Pc'),
        "PC C5": get_pc_t(df_pd_neo["C5"].values.tolist(), df_baremo,'C', 'C5', 'Pc'),
        "PC N6": get_pc_t(df_pd_neo["N6"].values.tolist(), df_baremo,'N', 'N6', 'Pc'),
        "PC E6": get_pc_t(df_pd_neo["E6"].values.tolist(), df_baremo,'E', 'E6', 'Pc'),
        "PC O6": get_pc_t(df_pd_neo["O6"].values.tolist(), df_baremo,'O', 'O6', 'Pc'),
        "PC A6": get_pc_t(df_pd_neo["A6"].values.tolist(), df_baremo,'A', 'A6', 'Pc'),
        "PC C6": get_pc_t(df_pd_neo["C6"].values.tolist(), df_baremo,'C', 'C6', 'Pc'),
        "PC NNEO": get_pc_t(df_perfil_neo["NNEO"].values.tolist(), df_baremo,'Neo', 'N', 'Pc'),
        "PC ENEO": get_pc_t(df_perfil_neo["ENEO"].values.tolist(), df_baremo,'Neo', 'E', 'Pc'),
        "PC ONEO": get_pc_t(df_perfil_neo["ONEO"].values.tolist(), df_baremo,'Neo', 'O', 'Pc'),
        "PC ANEO": get_pc_t(df_perfil_neo["ANEO"].values.tolist(), df_baremo,'Neo', 'A', 'Pc'),
        "PC CNEO": get_pc_t(df_perfil_neo["CNEO"].values.tolist(), df_baremo,'Neo', 'C', 'Pc'),
    }
    df_pc_neo = pd.DataFrame(pc_neo_pi)
    pnt_t_neo = {
        "T N1": get_pc_t(df_pd_neo["N1"].values.tolist(), df_baremo,'N', 'N1', 'T'),
        "T E1": get_pc_t(df_pd_neo["E1"].values.tolist(), df_baremo,'E', 'E1', 'T'),
        "T O1": get_pc_t(df_pd_neo["O1"].values.tolist(), df_baremo,'O', 'O1', 'T'),
        "T A1": get_pc_t(df_pd_neo["A1"].values.tolist(), df_baremo,'A', 'A1', 'T'),
        "T C1": get_pc_t(df_pd_neo["C1"].values.tolist(), df_baremo,'C', 'C1', 'T'),
        "T N2": get_pc_t(df_pd_neo["N2"].values.tolist(), df_baremo,'N', 'N2', 'T'),
        "T E2": get_pc_t(df_pd_neo["E2"].values.tolist(), df_baremo,'E', 'E2', 'T'),
        "T O2": get_pc_t(df_pd_neo["O2"].values.tolist(), df_baremo,'O', 'O2', 'T'),
        "T A2": get_pc_t(df_pd_neo["A2"].values.tolist(), df_baremo,'A', 'A2', 'T'),
        "T C2": get_pc_t(df_pd_neo["C2"].values.tolist(), df_baremo,'C', 'C2', 'T'),
        "T N3": get_pc_t(df_pd_neo["N3"].values.tolist(), df_baremo,'N', 'N3', 'T'),
        "T E3": get_pc_t(df_pd_neo["E3"].values.tolist(), df_baremo,'E', 'E3', 'T'),
        "T O3": get_pc_t(df_pd_neo["O3"].values.tolist(), df_baremo,'O', 'O3', 'T'),
        "T A3": get_pc_t(df_pd_neo["A3"].values.tolist(), df_baremo,'A', 'A3', 'T'),
        "T C3": get_pc_t(df_pd_neo["C3"].values.tolist(), df_baremo,'C', 'C3', 'T'),
        "T N4": get_pc_t(df_pd_neo["N4"].values.tolist(), df_baremo,'N', 'N4', 'T'),
        "T E4": get_pc_t(df_pd_neo["E4"].values.tolist(), df_baremo,'E', 'E4', 'T'),
        "T O4": get_pc_t(df_pd_neo["O4"].values.tolist(), df_baremo,'O', 'O4', 'T'),
        "T A4": get_pc_t(df_pd_neo["A4"].values.tolist(), df_baremo,'A', 'A4', 'T'),
        "T C4": get_pc_t(df_pd_neo["C4"].values.tolist(), df_baremo,'C', 'C4', 'T'),
        "T N5": get_pc_t(df_pd_neo["N5"].values.tolist(), df_baremo,'N', 'N5', 'T'),
        "T E5": get_pc_t(df_pd_neo["E5"].values.tolist(), df_baremo,'E', 'E5', 'T'),
        "T O5": get_pc_t(df_pd_neo["O5"].values.tolist(), df_baremo,'O', 'O5', 'T'),
        "T A5": get_pc_t(df_pd_neo["A5"].values.tolist(), df_baremo,'A', 'A5', 'T'),
        "T C5": get_pc_t(df_pd_neo["C5"].values.tolist(), df_baremo,'C', 'C5', 'T'),
        "T N6": get_pc_t(df_pd_neo["N6"].values.tolist(), df_baremo,'N', 'N6', 'T'),
        "T E6": get_pc_t(df_pd_neo["E6"].values.tolist(), df_baremo,'E', 'E6', 'T'),
        "T O6": get_pc_t(df_pd_neo["O6"].values.tolist(), df_baremo,'O', 'O6', 'T'),
        "T A6": get_pc_t(df_pd_neo["A6"].values.tolist(), df_baremo,'A', 'A6', 'T'),
        "T C6": get_pc_t(df_pd_neo["C6"].values.tolist(), df_baremo,'C', 'C6', 'T'),
        "T NNEO": get_pc_t(df_perfil_neo["NNEO"].values.tolist(), df_baremo,'Neo', 'N', 'T'),
        "T ENEO": get_pc_t(df_perfil_neo["ENEO"].values.tolist(), df_baremo,'Neo', 'E', 'T'),
        "T ONEO": get_pc_t(df_perfil_neo["ONEO"].values.tolist(), df_baremo,'Neo', 'O', 'T'),
        "T ANEO": get_pc_t(df_perfil_neo["ANEO"].values.tolist(), df_baremo,'Neo', 'A', 'T'),
        "T CNEO": get_pc_t(df_perfil_neo["CNEO"].values.tolist(), df_baremo,'Neo', 'C', 'T'),
    }
    df_t_neo = pd.DataFrame(pnt_t_neo)
    # Reordenar columnas: agrupar por rasgo (N, E, O, A, C) y luego por subindice 1..6
    

    df_t_neo_orden = reorder_df_t_neo(df_t_neo)
    #list para grafico

    list_neo_dimension = df_t_neo_orden.iloc[0].values.tolist()
    # Niveles
    df_t_neo_nivel = df_t_neo.applymap(set_nivel_neo)
    df_t_neo_nivel = df_t_neo_nivel.rename(columns=lambda x: x.replace('T ', 'Nivel '))
    # Descripcion niveles
    desc_niveles_neo = {
        "Desc Nivel N1": get_desc(df_t_neo_nivel["Nivel N1"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N1'),
        "Desc Nivel E1": get_desc(df_t_neo_nivel["Nivel E1"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E1'),
        "Desc Nivel O1": get_desc(df_t_neo_nivel["Nivel O1"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O1'),
        "Desc Nivel A1": get_desc(df_t_neo_nivel["Nivel A1"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A1'),
        "Desc Nivel C1": get_desc(df_t_neo_nivel["Nivel C1"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C1'),
        "Desc Nivel N2": get_desc(df_t_neo_nivel["Nivel N2"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N2'),
        "Desc Nivel E2": get_desc(df_t_neo_nivel["Nivel E2"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E2'),
        "Desc Nivel O2": get_desc(df_t_neo_nivel["Nivel O2"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O2'),
        "Desc Nivel A2": get_desc(df_t_neo_nivel["Nivel A2"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A2'),
        "Desc Nivel C2": get_desc(df_t_neo_nivel["Nivel C2"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C2'),
        "Desc Nivel N3": get_desc(df_t_neo_nivel["Nivel N3"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N3'),
        "Desc Nivel E3": get_desc(df_t_neo_nivel["Nivel E3"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E3'),
        "Desc Nivel O3": get_desc(df_t_neo_nivel["Nivel O3"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O3'),
        "Desc Nivel A3": get_desc(df_t_neo_nivel["Nivel A3"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A3'),
        "Desc Nivel C3": get_desc(df_t_neo_nivel["Nivel C3"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C3'),
        "Desc Nivel N4": get_desc(df_t_neo_nivel["Nivel N4"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N4'),
        "Desc Nivel E4": get_desc(df_t_neo_nivel["Nivel E4"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E4'),
        "Desc Nivel O4": get_desc(df_t_neo_nivel["Nivel O4"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O4'),
        "Desc Nivel A4": get_desc(df_t_neo_nivel["Nivel A4"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A4'),
        "Desc Nivel C4": get_desc(df_t_neo_nivel["Nivel C4"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C4'),
        "Desc Nivel N5": get_desc(df_t_neo_nivel["Nivel N5"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N5'),
        "Desc Nivel E5": get_desc(df_t_neo_nivel["Nivel E5"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E5'),
        "Desc Nivel O5": get_desc(df_t_neo_nivel["Nivel O5"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O5'),
        "Desc Nivel A5": get_desc(df_t_neo_nivel["Nivel A5"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A5'),
        "Desc Nivel C5": get_desc(df_t_neo_nivel["Nivel C5"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C5'),
        "Desc Nivel N6": get_desc(df_t_neo_nivel["Nivel N6"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N6'),
        "Desc Nivel E6": get_desc(df_t_neo_nivel["Nivel E6"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E6'),
        "Desc Nivel O6": get_desc(df_t_neo_nivel["Nivel O6"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O6'),
        "Desc Nivel A6": get_desc(df_t_neo_nivel["Nivel A6"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A6'),
        "Desc Nivel C6": get_desc(df_t_neo_nivel["Nivel C6"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C6'),
        "Desc Nivel N": get_desc(df_t_neo_nivel["Nivel NNEO"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'N'),
        "Desc Nivel E": get_desc(df_t_neo_nivel["Nivel ENEO"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'E'),
        "Desc Nivel O": get_desc(df_t_neo_nivel["Nivel ONEO"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'O'),
        "Desc Nivel A": get_desc(df_t_neo_nivel["Nivel ANEO"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'A'),
        "Desc Nivel C": get_desc(df_t_neo_nivel["Nivel CNEO"].values.tolist(), 'nivel_neo_pi', 'Niveles', 'C'),
    }
    df_desc_niveles_neo = pd.DataFrame(desc_niveles_neo)
    # Concatenar todo
    df_pd_neo = df_pd_neo.reset_index(drop=True)
    df_perfil_neo = df_perfil_neo.reset_index(drop=True)
    df_pc_neo = df_pc_neo.reset_index(drop=True)
    df_t_neo = df_t_neo.reset_index(drop=True)
    df_t_neo_nivel = df_t_neo_nivel.reset_index(drop=True)
    df_desc_niveles_neo = df_desc_niveles_neo.reset_index(drop=True)
    df_total = pd.concat([df_pd_neo, df_perfil_neo, df_pc_neo, df_t_neo, df_t_neo_nivel, df_desc_niveles_neo], axis=1)
    #df_total = df_total.fillna(0).astype(int)
    return df_total, list_neo_dimension

def reorder_df_t_neo(df):
        # Orden deseado: T N1,T N2,...,T N6, T E1...T E6, T O1...T O6, T A1...T A6, T C1...T C6
        traits = ['N', 'E', 'O', 'A', 'C']
        desired = []
        for t in traits:
            for i in range(1, 7):
                col = f'T {t}{i}'
                if col in df.columns:
                    desired.append(col)
        # Añadir scores globales al final si existen
        for col in ['T NNEO', 'T ENEO', 'T ONEO', 'T ANEO', 'T CNEO']:
            if col in df.columns:
                desired.append(col)
        ordered = desired 
        return df[ordered]

def get_pc_t(valores, baremo, colBaremo, columna_comparar, columna_recuperar):
    resultado = []
    for j in range(len(valores)):
        df2 = pd.read_pickle(os.path.join(base_path,'baremos' ,f'{colBaremo}_{baremo}.pkl'))
        
        df2 = df2.loc[:, [columna_recuperar, columna_comparar]]
        df2 = df2.dropna()
        
        sintomas = df2.loc[:, columna_comparar].values.tolist()
        sintomas = sorted(sintomas)
        pc = df2.loc[:, columna_recuperar].values.tolist()
        if baremo == 'B':
            pc = sorted(pc, reverse=True)
        else:
            pc = sorted(pc)
        i = bisect.bisect_left(sintomas, valores[j])
        resultado.append(int(pc[i]))
    return resultado

def set_nivel_neo(valor):
    
    if valor <= 35:
        return "Muy bajo"
    elif valor <= 45:
        return "Bajo"
    elif valor <= 55:
        return "Medio"
    elif valor <= 65:
        return "Alto"
    else:
        return "Muy alto"
    
def df_calculo_rokeach(df):
    # Puntaje Rokeach
    df_pd = df.fillna(0).astype(int)
    new_col = ["Amor maduro (intimidad sexual y espiritual)", "Armonía interna (ausencia de conflictos internos)", "Auténtica amistad (compañerismo)", "Felicidad (satisfacción personal)", "Igualdad (fraternidad, igualdad de oportunidades para todos)", "Libertad (independencia, libre elección)", "Placer (una vida agradable, de ocio)", "Reconocimiento social (respeto, admiración)", "Respeto por uno mismo (autoestima)", "Sabiduría (una comprensión madura de la vida)", "Salvación (vida eterna, salvado)", "Seguridad familiar(cuidar de los seres queridos)", "Seguridad nacional (protección ante ataques)", "Sentimiento de realización (contribución duradera)", "Un mundo bello (la belleza de la naturaleza y las artes)", "Un mundo pacífico (sin guerras ni conflictos)", "Una vida cómoda (una vida próspera)", "Una vida excitante (una vida estimulante, activa)", "Alegre (despreocupado, jubiloso)", "Amante (afectivo, tierno)", "Ambicioso (trabaja duro, tiene ambiciones)", "Capaz (competente, eficiente)", "Clemente (dispuesto a perdonar a los demás)", "Con auto-control (comedido, con disciplina propia)", "Cortés (bien educado, con buenas maneras)", "Honesto (sincero, honrado)", "Imaginativo (atrevido, creativo)", "Independiente (depende de sí mismo, autosuficiente)", "Intelectual (inteligente, reflexivo)", "Limpio (aseado, ordenado)", "Lógico (coherente, racional)", "Mentalidad abierta (abierto a nuevas ideas)", "Obediente (dedicado, respetuoso)", "Responsable (fiable, cumplidor)", "Servicial (se refuerza por el bienestar de los demás)", "Valiente (defiende sus creencias)"]
    df_pd.columns = new_col
    df_pd = df_pd.reset_index(drop=True)
    df_rok_inst = df_pd.iloc[:,:18]
    df_rok_ter = df_pd.iloc[:,18:]
    
    df_rok_inst = df_rok_inst .sort_values(by=0, axis=1)
    df_rok_ter = df_rok_ter.sort_values(by=0, axis=1)
    rokeach_max_inst = {
        "Max Rokeach Inst 1": [df_rok_inst.columns[-1]],
        "Max Rokeach Inst 2": [df_rok_inst.columns[-2]],
        "Max Rokeach Inst 3": [df_rok_inst.columns[-3]],
    }
    df_rokeach_max_inst = pd.DataFrame(rokeach_max_inst)
    
    rokeach_max_ter = {
        "Max Rokeach Ter 1": [df_rok_ter.columns[-1]],
        "Max Rokeach Ter 2": [df_rok_ter.columns[-2]],
        "Max Rokeach Ter 3": [df_rok_ter.columns[-3]],
    }
    df_rokeach_max_ter = pd.DataFrame(rokeach_max_ter)
    
    df_rokeach_total = pd.concat([df_pd,df_rokeach_max_inst,df_rokeach_max_ter],axis=1)
    
    return df_rokeach_total

def grafico_linea_personalidad(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'
        prop = None

    x = np.arange(len(labels))
    y = values
    fig, ax = plt.subplots(figsize=(12, 5))
    plt.subplots_adjust(left=0.1)
    fig.subplots_adjust(top=0.90, bottom=0.18, left=0.1, right=0.95)
    ax.set_title(title,fontsize=18, position=(0.5, 1.05), ha='center', fontproperties=prop)
    # Dibujar líneas horizontales entre 30 y 70
    for val in range(30, 71, 10):
        color = "#6EB0C0" if val == 30 or val == 70 else '#CCCCCC'
        lw = 2 if val == 30 or val == 70 else 1
        ax.axhline(y=val, color=color, linestyle='--', linewidth=lw, zorder=0)
    # Línea principal
    ax.plot(x, y, color="#122DA6", linewidth=2, marker='o', markersize=8, zorder=2)
    # Etiquetas de los puntos
    for i, (xi, yi) in enumerate(zip(x, y)):
        ax.text(xi, yi + 2, str(yi), ha='center', va='bottom', fontsize=10, fontweight='bold', color='grey', fontproperties=prop)
    ax.set_xticks(x)
    # Ajustar el primer label desplazándolo a la derecha
    ticklabels = []
    for i, label in enumerate(labels):
        if i == 0:
            ticklabels.append('\u200A' * 6 + label)  # Unicode thin space para desplazar
        else:
            ticklabels.append(label)
    ax.set_xticklabels(labels, fontproperties=prop, fontweight='bold', fontsize=10)
    ax.set_ylim([0, 100])
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    for s in ['top', 'right', 'left', 'bottom']:
        ax.spines[s].set_visible(False)
    #plt.tight_layout()
    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    return graphic

def grafico_linea_subdimension(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'
        prop = None

    # Dividir en 5 grupos de 6 valores
    n = 6
    grupos_labels = [labels[i:i+n] for i in range(0, len(labels), n)]
    grupos_values = [values[i:i+n] for i in range(0, len(values), n)]

    fig, axes = plt.subplots(1, 5, figsize=(22, 9), sharey=True)
    fig.subplots_adjust(top=0.85, bottom=0.25, left=0.07, right=0.98, wspace=0.15)
    fig.suptitle(title, fontsize=18, fontproperties=prop)

    for idx, ax in enumerate(axes):
        x = np.arange(len(grupos_labels[idx]))
        y = grupos_values[idx]
        # Líneas horizontales entre 30 y 70
        for val in range(30, 71, 10):
            color = "#6EB0C0" if val == 30 or val == 70 else "#4E4D4D" if val == 50 else '#CCCCCC'
            lw = 2 if val == 30 or val == 70 else 1
            ax.axhline(y=val, color=color, linestyle='--', linewidth=lw, zorder=0)
        # Línea principal
        ax.plot(x, y, color="#122DA6", linewidth=2, marker='o', markersize=7, zorder=2)
        # Etiquetas de los puntos
        for i, (xi, yi) in enumerate(zip(x, y)):
            ax.text(xi, yi + 2, str(yi), ha='center', va='bottom', fontsize=12, fontweight='bold', color='black', fontproperties=prop)
        ax.set_xticks(x)
        ax.set_xticklabels(grupos_labels[idx], fontproperties=prop, fontweight='bold', fontsize=13, rotation=40, ha='right')
        ax.set_ylim([0, 100])
        if idx == 0:
            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
            ax.tick_params(axis='y', length=0)
        else:
            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
            ax.tick_params(axis='y', length=0)
            #ax.set_yticks([])
            #ax.set_yticklabels([])
        ax.tick_params(axis='x', length=0)
        for s in ['top', 'right', 'bottom']:
            ax.spines[s].set_visible(False)
        if idx != 0:
            ax.spines['left'].set_visible(False)
        else:
            ax.spines['left'].set_visible(False)  # Opcional: si quieres ocultar también la línea del eje y

    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    return graphic


def grafico_linea_personalidad_pdf(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'
        prop = None
    print(f"Font Name lineplot: {plt.rcParams['font.family']}")
    x = np.arange(len(labels))
    y = values
    fig, ax = plt.subplots(figsize=(12, 5))
    plt.subplots_adjust(left=0.1)
    fig.subplots_adjust(top=0.90, bottom=0.18, left=0.1, right=0.95)
    plt.suptitle(title, fontsize=18, fontproperties=prop)
    # Dibujar líneas horizontales entre 30 y 70
    for val in range(30, 71, 10):
        color = "#6EB0C0" if val == 30 or val == 70 else '#CCCCCC'
        lw = 2 if val == 30 or val == 70 else 1
        ax.axhline(y=val, color=color, linestyle='--', linewidth=lw, zorder=0)
    # Línea principal
    ax.plot(x, y, color="#122DA6", linewidth=2, marker='o', markersize=8, zorder=2)
    # Etiquetas de los puntos
    for i, (xi, yi) in enumerate(zip(x, y)):
        ax.text(xi, yi + 2, str(yi), ha='center', va='bottom', fontsize=10, fontweight='bold', color='grey', fontproperties=prop)
    ax.set_xticks(x)
    # Ajustar el primer label desplazándolo a la derecha
    ticklabels = []
    for i, label in enumerate(labels):
        if i == 0:
            ticklabels.append('\u200A' * 6 + label)  # Unicode thin space para desplazar
        else:
            ticklabels.append(label)
    ax.set_xticklabels(labels, fontproperties=prop, fontweight='bold', fontsize=12)
    ax.set_ylim([0, 100])
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    for s in ['top', 'right', 'left', 'bottom']:
        ax.spines[s].set_visible(False)
    #plt.tight_layout()
    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    plt.close()
    return buffer.read()

def grafico_linea_subdimension_pdf(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'
        prop = None

    # Dividir en 5 grupos de 6 valores
    n = 6
    grupos_labels = [labels[i:i+n] for i in range(0, len(labels), n)]
    grupos_values = [values[i:i+n] for i in range(0, len(values), n)]

    fig, axes = plt.subplots(1, 5, figsize=(12, 5), sharey=True)
    fig.subplots_adjust(top=0.85, bottom=0.25, left=0.07, right=0.98, wspace=0.15)
    fig.suptitle(title, fontsize=18, fontproperties=prop)

    for idx, ax in enumerate(axes):
        x = np.arange(len(grupos_labels[idx]))
        y = grupos_values[idx]
        # Líneas horizontales entre 30 y 70
        for val in range(30, 71, 10):
            color = "#6EB0C0" if val == 30 or val == 70 else "#4E4D4D" if val == 50 else '#CCCCCC'
            lw = 2 if val == 30 or val == 70 else 1
            ax.axhline(y=val, color=color, linestyle='--', linewidth=lw, zorder=0)
        # Línea principal
        ax.plot(x, y, color="#122DA6", linewidth=2, marker='o', markersize=7, zorder=2)
        # Etiquetas de los puntos
        for i, (xi, yi) in enumerate(zip(x, y)):
            ax.text(xi, yi + 2, str(yi), ha='center', va='bottom', fontsize=10, fontweight='bold', color='grey', fontproperties=prop)
        ax.set_xticks(x)
        ax.set_xticklabels(grupos_labels[idx], fontproperties=prop, fontweight='bold', fontsize=10, rotation=40, ha='right')
        ax.set_ylim([0, 100])
        if idx == 0:
            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
            ax.tick_params(axis='y', length=0)
        else:
            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels([str(i) for i in np.arange(0, 101, 10)], fontproperties=prop, fontsize=8)
            ax.tick_params(axis='y', length=0)
            #ax.set_yticks([])
            #ax.set_yticklabels([])
        ax.tick_params(axis='x', length=0)
        for s in ['top', 'right', 'bottom']:
            ax.spines[s].set_visible(False)
        if idx != 0:
            ax.spines['left'].set_visible(False)
        else:
            ax.spines['left'].set_visible(False)  # Opcional: si quieres ocultar también la línea del eje y

    #plt.show()
    buffer = BytesIO()
    fig.savefig(buffer, format='png', transparent=True)
    plt.close()
    buffer.seek(0)
    return buffer


def grafico_bar_pdf(labels, values, title=""):
    font_path = os.path.join(base_path, 'fonts','static', 'Montserrat-SemiBold.ttf')
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.family'] = 'sans-serif'  # Fallback
    
    x = labels
    y = values
    colores = ["#27A612","#C00000","#92D050","#7030A0", "#ED7D31", "#002060"]
    fig, ax = plt.subplots(figsize=(9, 4))
    fig.subplots_adjust(top=0.90, bottom=0.08, left=0.11, right=0.85)
    ax.set_title(title,  position=(0.5, 1.1), ha='center', fontproperties=prop)
    bars = ax.bar(x, y, color=colores)
    #ax.barh(x, width = y, color=colores)
    list_patch = []
    for i in range(len(labels)):
        patch = mpatches.Patch(color=colores[i], label=labels[i])
        list_patch.append(patch)
    #ax.legend(handles=list_patch, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=2)
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    # Add annotation to bars
    """for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5,str(round((i.get_width()))),
                 fontsize=10, fontweight='bold',color='grey')"""
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, str(height),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='grey', fontproperties=prop)
    #ax.set_ylim([0, max(y) + 10])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontproperties=prop, fontweight='bold', fontsize=10)
    #ax.set_yticks(np.arange(0, max(y)+11, 5))  # Mostrar ticks cada 5 unidades
    
    #ax.invert_yaxis()
    ax.set_ylim([0,40])
    
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    #plt.xticks([])
    #plt.yticks([])
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    
    buffer = BytesIO()
    fig.savefig(buffer, format='png', transparent=True)
    
    
    #plt.savefig(buffer, format='png',transparent=True)
    plt.close()
    buffer.seek(0)
    
    return buffer.read()


if __name__ == '__main__':
    df = carga_vocacional(2)
    



