"""Small example PDF generator using fpdf2.

Features demonstrated:
- Register a TTF font (Montserrat) if available, with unicode support
- Draw colored text boxes (filled rectangles with text)
- Insert a matplotlib chart rendered into an in-memory PNG
- Render a table with a colored header row and bold titles

Usage: python build_pdf.py  -> writes sample_report.pdf in the current folder

Requires: fpdf (fpdf2) and matplotlib installed in the environment.
"""
from fpdf import FPDF
import os
import pathlib
from io import BytesIO
import base64
from vocacional import grafico_linea_personalidad_pdf, grafico_linea_subdimension_pdf, grafico_bar_pdf, \
    carga_onet_df, carga_neo_pi_df, carga_rokeach_df
from datetime import datetime
try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
except Exception:
    plt = None

base_dir = pathlib.Path(os.getcwd()).resolve()


def _make_sample_plot():
    """Return PNG bytes of a small matplotlib chart (or None if matplotlib missing)."""
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(6, 3))
    labels = ['R', 'I', 'A', 'S', 'E', 'C']
    values = [18, 26, 14, 22, 16, 12]
    bars = ax.bar(labels, values, color=['#27A612', '#C00000', '#92D050', '#7030A0', '#ED7D31', '#002060'])
    ax.set_ylim(0, 40)
    ax.set_title('Perfil O*NET - Ejemplo')
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, str(h), ha='center', va='bottom')
    plt.tight_layout()
    bio = BytesIO()
    fig.savefig(bio, format='png', transparent=True)
    plt.close(fig)
    bio.seek(0)
    return bio.read()



class SamplePDF:
    def __init__(self, context,font_name='MontserratR'):
        self.pdf = FPDF(unit='mm', format='A4')
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.font_name = font_name
        self.context = context
        self.text_size_title = 18
        self.text_size_subtitle = 12
        self.text_size_normal = 10
        self.text_size_table = 9
        self.margin = 5
        self._register_fonts()

    def _register_fonts(self):
        """Try to register Montserrat from repository fonts; fall back to built-in fonts."""
        
        fonts_dir =os.path.join(os.getcwd(),'fonts', 'static') 
        # Common names used in this repo
        candidates = [
            os.path.join(fonts_dir, 'Montserrat-Regular.ttf'),
            os.path.join(fonts_dir , 'Montserrat-SemiBold.ttf'),
            os.path.join(fonts_dir , 'Montserrat-Medium.ttf'),
        ]
        registered = False
        for cand in candidates:
            if os.path.exists(cand):
                try:
                    # add regular (no style)
                    
                    # Register bold using same file if it's a semibold
                    if 'SemiBold' in cand or 'Bold' in cand:
                        self.pdf.add_font('MontserratR', 'B', str(cand), uni=True)
                        registered = True
                        self.font_name = 'MontserratR'
                    else:
                        self.pdf.add_font('MontserratR', '', str(cand), uni=True)
                        #self.pdf.add_font('MontserratR', 'B', str(cand), uni=True)
                        registered = True
                        self.font_name = 'MontserratR'
                    break
                except Exception as e:
                   
                    registered = False
        if not registered:
            # Use a built-in font as fallback
            self.font_name = 'Helvetica'

    def build(self, out_path='sample_report.pdf', to_buffer=False):
        pdf = self.pdf
        pdf.add_page()
         #ADD custom font
        try:
            fonts_dir =os.path.join(base_dir,'fonts', 'static','Montserrat-Bold.ttf')
            self.pdf.add_font('MontserratBold', '', str(fonts_dir), uni=True)
        except Exception:
            pass
        # Title
        pdf.set_font('MontserratBold', '', self.text_size_title)
        pdf.set_text_color(20, 20, 40)
        pdf.cell(0, 10, 'Informe Test Vocacional y Personalidad', ln=True, align='C')

       
        # Colored text box (filled rectangle with text)
        x = 0
        y = 30
        w = 220
        h = 5
        w_line = 220
        pdf.set_fill_color(86, 117, 206)  # light blue background
        pdf.rect(x, y, w, h, style='F')
        pdf.set_xy(x , y )
        pdf.set_font('MontserratBold', '', self.text_size_subtitle)
        pdf.set_text_color(226, 222, 223)
        pdf.multi_cell(w - 8, 6, 'A - Datos Generales', border=0)
        # Dibujar una linea debajo del recuadro
        y_line = pdf.get_y()+ 2
        pdf.set_fill_color(64, 64, 64)
        pdf.line(x, y_line, x + w, y_line)
        # Datos del participante - ejemplo: poner etiqueta en negrita y valor normal en la misma línea
        pdf.set_text_color(20, 20, 40)
        line_h = y_line + 2
        # Método 1: usar write() y cambiar la fuente entre llamadas (recomendado para flujo de texto)
        pdf.set_font('MontserratBold', '', self.text_size_normal)
        pdf.write(5, '\nNombre: ')
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.write(5, f'                       {self.context["info"]["nombre"][0]}\n')
        pdf.set_font('MontserratBold', '', self.text_size_normal)
        pdf.write(5, 'Edad: ')
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.write(5, f'                             {self.context["info"]["edad"][0]}\n')
        pdf.set_font('MontserratBold', '', self.text_size_normal)
        pdf.write(5, 'Fecha aplicación: ')
        pdf.set_font(self.font_name, '', self.text_size_normal)
        fecha = self.context["info"]["created"][0]
        #fecha.strftime("%d/%m/%Y")
        pdf.write(5, f'      {fecha.strftime("%d/%m/%Y")}\n')
        # Dibujar una linea debajo de los datos
        y_line2 = pdf.get_y() + 2
        pdf.set_fill_color(64, 64, 64)
        pdf.line(x, y_line2, x + w, y_line2)
        # Subtítulo para la siguiente sección
        y_title = pdf.get_y() + 4
        pdf.set_fill_color(86, 117, 206)  # light blue background
        pdf.rect(x, y_title, w, h, style='F')
        pdf.set_xy(x , y_title)
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(226, 222, 223)
        pdf.multi_cell(w - 8, 6, 'B - Resultados', border=0)
        # Alternativa (Método 2): usar dos celdas con anchos controlados para asegurar que queden en la misma línea
        # pdf.set_font('MontserratBold', '', 12)
        # pdf.cell(30, 8, 'Nombre:', border=0, ln=0)
        # pdf.set_font(self.font_name, '', 12)
        # pdf.cell(0, 8, 'Juan Pérez', border=0, ln=1)
        # Insert matplotlib graphic
        png = self.context['grafico_onet']#grafico_bar_pdf(self.label_onet, self.val_onet, "Perfil O*NET")
        if png:
            # place image below the box
            img_x = 20
            img_y = y_title + 4
            # fpdf2 accepts a BytesIO-like object via .image(stream=...)
            bio = BytesIO(png)
            bio.seek(0)
            try:
                pdf.image(bio, x=img_x, y=img_y, w=170)
            except Exception:
                # fallback: write to a temporary file
                tmp_path = os.path.join(base_dir,'temp_plot.png')  
                
                with open(tmp_path, 'wb') as f:
                    f.write(png)
                pdf.image(str(tmp_path), x=img_x, y=img_y, w=170)
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            # advance cursor below image
            pdf.ln(90)
        else:
            pdf.ln(20)
        # Subtítulo para la siguiente sección
        y_title2 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)  # light blue background
        pdf.rect(x, y_title2, w, h, style='F')
        pdf.set_xy(x , y_title2)
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w - 8, 6, 'Test O*NET',align="C", border=0)
        # Table with colored header and bold titles
        pdf.ln(0)
        pdf.set_font(self.font_name, '', 10)
        pdf.set_fill_color(50, 100, 160)  # header background
        pdf.set_text_color(255, 255, 255)
        col_widths = [50, 20, 40, 93]
        headers = ['', 'PD', 'Tipo de interés', 'Descripción']
        # draw header
        x_header = self.margin
        y_header = pdf.get_y() + 2
        pdf.set_xy(x_header, y_header)
        for i, htext in enumerate(headers):
            
            pdf.cell(col_widths[i], 6, htext, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # table rows with wrapping for the last column and vertical centering for other cells
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Primera opción', f'{self.context["df_onet_pd"]["PD_MAX_ONET_1"][0]}', f'{self.context["df_onet_pd"]["Max_Onet_1"][0]}', f'{self.context["df_onet_pd"]["Desc_Max_Onet_1"][0]}'],
            ['Segunda opción', f'{self.context["df_onet_pd"]["PD_MAX_ONET_2"][0]}', f'{self.context["df_onet_pd"]["Max_Onet_2"][0]}', f'{self.context["df_onet_pd"]["Desc_Max_Onet_2"][0]}'],
            ['Tercera opción', f'{self.context["df_onet_pd"]["PD_MAX_ONET_3"][0]}', f'{self.context["df_onet_pd"]["Max_Onet_3"][0]}', f'{self.context["df_onet_pd"]["Desc_Max_Onet_3"][0]}'],
            ['Zona de trabajo',f'{self.context["df_onet_pd"]["zona"][0]}','-',f'{self.context["df_onet_pd"]["Desc_Zona"][0]}']
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm

        def _wrap_text_to_lines(pdf_obj, text, max_width):
            """Simple word-wrap using pdf.get_string_width to compute lines."""
            if not text:
                return ['']
            words = str(text).split()
            lines = []
            cur = ''
            for w in words:
                test = (cur + ' ' + w).strip() if cur else w
                
                
                if pdf_obj.get_string_width(test) <= max_width:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    # word itself might be longer than max_width
                    if pdf_obj.get_string_width(w) > max_width:
                        # break the word by characters
                        part = ''
                        for ch in w:
                            if pdf_obj.get_string_width(part + ch) <= max_width:
                                part += ch
                            else:
                                if part:
                                    lines.append(part)
                                part = ch
                        if part:
                            cur = part
                        else:
                            cur = ''
                    else:
                        cur = w
            if cur:
                lines.append(cur)
            return lines

        def _rebalance_lines(pdf_obj, lines, max_width):
            """Try to avoid isolated single-word lines by moving last word from previous line
            to the current single-word line when both resulting lines still fit."""
            # operate on a copy
            out = lines[:]
            for i in range(1, len(out)):
                parts = out[i].split()
                if len(parts) == 1:
                    prev = out[i-1].split()
                    if len(prev) > 1:
                        # try moving last word from prev to current
                        candidate_prev = ' '.join(prev[:-1])
                        candidate_curr = prev[-1] + ' ' + out[i]
                        if pdf_obj.get_string_width(candidate_prev) <= (max_width) and pdf_obj.get_string_width(candidate_curr) <= (max_width):
                            out[i-1] = candidate_prev
                            out[i] = candidate_curr
            return out

        # before drawing, ensure there's enough vertical space; if not, add page and redraw header
        def _need_page_break(pdf_obj, needed_h):
            # pdf.h is page height, pdf.b_margin is bottom margin
            return pdf_obj.get_y() + needed_h > (pdf_obj.h - pdf_obj.b_margin)

        # helper to redraw header when starting a new page
        def _draw_table_header():
            pdf.set_xy(self.margin, pdf.get_y())
            pdf.set_font(self.font_name, '', 10)
            pdf.set_fill_color(50, 100, 160)
            pdf.set_text_color(255, 255, 255)
            for ii, htext in enumerate(headers):
                pdf.cell(col_widths[ii], 6, htext, border=1, ln=0, align='C', fill=True)
            pdf.ln()
            # restore expected font/color for subsequent row drawing
            try:
                pdf.set_font(self.font_name, '', 9)
            except Exception:
                # fallback to built-in font
                pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(10)
        # Add a new page for the next section
        ###############################################################
        pdf.add_page()
        #Ejemplos de carreras
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(3)
        
        #Carrera 1
        pdf.set_font(self.font_name, '', 10)
        pdf.cell(0, 10, f'Ejemplo de carreras de la Zona de trabajo {self.context["df_onet_pd"]["zona"][0]}, del tipo de interés {self.context["df_onet_pd"]["Max_Onet_1"][0]}', ln=True, align='C')
        pdf.ln(1)
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(5)
        carrera1 = self.context["df_onet_pd"]["Tipo_Trabajo_1"][0]
        pdf.set_xy(2 , pdf.get_y() +2 )
        pdf.set_font(self.font_name, '', 10)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 14, 6, carrera1,align="J", border=0)
        pdf.ln(5)
        #Carrera 2
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(3)
        pdf.set_font(self.font_name, '', 10)
        pdf.cell(0, 10, f'Ejemplo de carreras de la Zona de trabajo {self.context["df_onet_pd"]["zona"][0]}, del tipo de interés {self.context["df_onet_pd"]["Max_Onet_2"][0]}', ln=True, align='C')
        pdf.ln(1)
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(5)
        carrera2 = self.context["df_onet_pd"]["Tipo_Trabajo_2"][0]
        pdf.set_xy(2 , pdf.get_y() +2 )
        pdf.set_font(self.font_name, '', 10)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 14, 6, carrera2,align="J", border=0)
        pdf.ln(5)
        #Carrera 3
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(3)
        pdf.set_font(self.font_name, '', 10)
        pdf.cell(0, 10, f'Ejemplo de carreras de la Zona de trabajo {self.context["df_onet_pd"]["zona"][0]}, del tipo de interés {self.context["df_onet_pd"]["Max_Onet_3"][0]}', ln=True, align='C')
        pdf.ln(1)
        pdf.set_fill_color(64, 64, 64)
        pdf.line(0, pdf.get_y()+2, 0 + w_line, pdf.get_y()+2)
        pdf.ln(5)
        carrera3 = self.context["df_onet_pd"]["Tipo_Trabajo_3"][0]
        pdf.set_xy(2 , pdf.get_y() +2 )
        pdf.set_font(self.font_name, '', 10)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 14, 6, carrera3,align="J", border=0)
        pdf.ln(5)
        pdf.set_font(self.font_name, '', 10)
        pdf.cell(0, 5, 'Para una visualización más completa de las carreras, por favor, dirijase al siguiente link: https://bit.ly/aikumby', ln=True, align='C')
        pdf.ln(3)

        # Nueva pagina##########################################
        pdf.add_page()
        # Subtítulo para la siguiente sección
        #NEOPI-R
        #Dimensiones de la personalidad
        y_title2 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)  # light blue background
        pdf.rect(0, y_title2, w_line, 5, style='F')
        pdf.set_xy(0 , y_title2)
        pdf.set_font('MontserratBold', '', self.text_size_subtitle)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 8, 6, 'Test NEO-PI R',align="C", border=0)
        ## tabla NEO-PI-R
        pdf.set_font(self.font_name, '', 11)
        pdf.set_fill_color(50, 100, 160)  # header background
        pdf.set_text_color(255, 255, 255)
        col_widths = [50, 25, 30, 96]
        headers = ['Dimensiones', 'Pc', 'Nivel', 'Descripción']
        # draw header
        x_header = self.margin
        y_header = pdf.get_y() + 2
        pdf.set_xy(x_header, y_header)
        for i, htext in enumerate(headers):
            
            pdf.cell(col_widths[i], 5, htext, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # table rows with wrapping for the last column and vertical centering for other cells
        pdf.set_font(self.font_name, '', 11)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Neuroticismo', f'{self.context["df_neo_pi_pd"]["PC_NNEO"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_NNEO"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N"][0]}'],
            ['Extraversión', f'{self.context["df_neo_pi_pd"]["PC_ENEO"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_ENEO"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E"][0]}'],
            ['Apertura', f'{self.context["df_neo_pi_pd"]["PC_ONEO"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_ONEO"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O"][0]}'],
            ['Amabilidad', f'{self.context["df_neo_pi_pd"]["PC_ANEO"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_ANEO"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A"][0]}'],
            ['Responsabilidad', f'{self.context["df_neo_pi_pd"]["PC_CNEO"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_CNEO"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C"][0]}'],
            
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(2)
        #Fin tabla dimensiones NEO-PI-R
        ##Subdimensiones de la personalidad
        y_title2 = pdf.get_y() + 3
        ## tabla NEO-PI-R
        pdf.set_font(self.font_name, '', 9)
        pdf.set_fill_color(50, 100, 160)  # header background
        pdf.set_text_color(255, 255, 255)
        col_widths = [50, 25, 30, 96]
        headers = ['Subdimensiones', 'Pc', 'Nivel', 'Descripción']
        # draw header
        x_header = self.margin
        y_header = pdf.get_y() + 2
        pdf.set_xy(x_header, y_header)
        for i, htext in enumerate(headers):
            
            pdf.cell(col_widths[i], 5, htext, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # table rows with wrapping for the last column and vertical centering for other cells
        #sub dimension 1
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Ansiedad', f'{self.context["df_neo_pi_pd"]["PC_N1"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N1"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N1"][0]}'],
            ['Hostilidad', f'{self.context["df_neo_pi_pd"]["PC_N2"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N2"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N2"][0]}'],
            ['Depresión', f'{self.context["df_neo_pi_pd"]["PC_N3"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N3"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N3"][0]}'],
            ['Ansiedad Social', f'{self.context["df_neo_pi_pd"]["PC_N4"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N4"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N4"][0]}'],
            ['Impulsividad', f'{self.context["df_neo_pi_pd"]["PC_N5"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N5"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N5"][0]}'],
            ['Vulnerabilidad', f'{self.context["df_neo_pi_pd"]["PC_N6"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_N6"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_N6"][0]}'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(2)
        #sub dimension 2
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Cordialidad', f'{self.context["df_neo_pi_pd"]["PC_E1"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E1"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E1"][0]}'],
            ['Gregarismo', f'{self.context["df_neo_pi_pd"]["PC_E2"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E2"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E2"][0]}'],
            ['Asertividad', f'{self.context["df_neo_pi_pd"]["PC_E3"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E3"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E3"][0]}'],
            ['Actividad', f'{self.context["df_neo_pi_pd"]["PC_E4"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E4"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E4"][0]}'],
            ['Búsqueda de emociones', f'{self.context["df_neo_pi_pd"]["PC_E5"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E5"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E5"][0]}'],
            ['Emociones positivas', f'{self.context["df_neo_pi_pd"]["PC_E6"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_E6"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_E6"][0]}'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(2)
        #sub dimension 3
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Fantasía', f'{self.context["df_neo_pi_pd"]["PC_O1"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O1"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O1"][0]}'],
            ['Estética', f'{self.context["df_neo_pi_pd"]["PC_O2"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O2"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O2"][0]}'],
            ['Sentimientos', f'{self.context["df_neo_pi_pd"]["PC_O3"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O3"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O3"][0]}'],
            ['Acciones', f'{self.context["df_neo_pi_pd"]["PC_O4"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O4"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O4"][0]}'],
            ['Ideas', f'{self.context["df_neo_pi_pd"]["PC_O5"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O5"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O5"][0]}'],
            ['Valores', f'{self.context["df_neo_pi_pd"]["PC_O6"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_O6"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_O6"][0]}'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                

                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(2)
        #sub dimension 4
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Confianza', f'{self.context["df_neo_pi_pd"]["PC_A1"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A1"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A1"][0]}'],
            ['Franqueza',f'{self.context["df_neo_pi_pd"]["PC_A2"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A2"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A2"][0]}'],
            ['Altruismo', f'{self.context["df_neo_pi_pd"]["PC_A3"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A3"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A3"][0]}'],
            ['Actitud conciliadora', f'{self.context["df_neo_pi_pd"]["PC_A4"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A4"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A4"][0]}'],
            ['Modestia', f'{self.context["df_neo_pi_pd"]["PC_A5"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A5"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A5"][0]}'],
            ['Sensibilidad a los demás', f'{self.context["df_neo_pi_pd"]["PC_A6"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_A6"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_A6"][0]}'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(2)
        #sub dimension 5
        pdf.set_font(self.font_name, '', 9)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Competencia', f'{self.context["df_neo_pi_pd"]["PC_C1"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C1"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C1"][0]}'],
            ['Orden', f'{self.context["df_neo_pi_pd"]["PC_C2"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C2"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C2"][0]}'],
            ['Sentido del deber', f'{self.context["df_neo_pi_pd"]["PC_C3"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C3"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C3"][0]}'],
            ['Necesidad de logro', f'{self.context["df_neo_pi_pd"]["PC_C4"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C4"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C4"][0]}'],
            ['Autodisciplina', f'{self.context["df_neo_pi_pd"]["PC_C5"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C5"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C5"][0]}'],
            ['Deliberación', f'{self.context["df_neo_pi_pd"]["PC_C6"][0]}', f'{self.context["df_neo_pi_pd"]["Nivel_C6"][0]}', f'{self.context["df_neo_pi_pd"]["Desc_Nivel_C6"][0]}'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (245, 245, 245)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 9)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                elif i in (1, 2):
                    align = 'C'
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - 2 * padding, line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell(w - 2 * padding, line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(20)
        #Fin tabla subdimensiones NEO-PI-R
        #######################################################################
        pdf.add_page()
        ## Grafico dimensiones NEO-PI-R
        png_neo = self.context['graf_neo_dimen']#grafico_linea_personalidad_pdf(self.label_neo, self.val_neo, title='Perfil Dimensión global NEOPI-R')
        if png_neo:
            # place image below the box
            img_x = 5
            img_y = pdf.get_y() + 4
            # fpdf2 accepts a BytesIO-like object via .image(stream=...)
            bio_neo = BytesIO(png_neo)
            bio_neo.seek(0)
            try:
                pdf.image(bio_neo, x=img_x, y=img_y, w=190)
            except Exception:
                # fallback: write to a temporary file
                tmp_path = os.path.join(base_dir, 'temp_plot_neo.png')
                with open(tmp_path, 'wb') as f:
                    f.write(png_neo)
                pdf.image(str(tmp_path), x=img_x, y=img_y, w=190)
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            # advance cursor below image
            pdf.ln(120)
        else:
            pdf.ln(20)
        #Fin grafico dimensiones NEO-PI-R
        ## Grafico subdimensiones NEO-PI-R
        png_neo_sub = self.context['graf_neo_sub']#grafico_linea_subdimension_pdf(self.label_subdim, self.val_subdim, title='Perfil Subdimensiones NEOPI-R')
        if png_neo_sub:
            # place image below the box
            img_x = 2
            img_y = pdf.get_y() + 4
            # fpdf2 accepts a BytesIO-like object via .image(stream=...)
            bio_neo_sub = png_neo_sub
            #bio_neo_sub.seek(0)
            try:
                inicio_sub_carga = datetime.now()
                pdf.image(png_neo_sub, x=img_x, y=img_y, w=200, type='PNG')
            except Exception as e:
                # fallback: write to a temporary file
                tmp_path = os.path.join(base_dir, 'temp_plot_neo_sub.png')
                with open(tmp_path, 'wb') as f:
                    f.write(png_neo_sub.read())
                pdf.image(str(tmp_path), x=img_x, y=img_y, w=200)
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            # advance cursor below image
            pdf.ln(90)
        else:
            pdf.ln(20)
        #######################################################################
        pdf.add_page()
        # Lista valores Rokeach
        x_rok = 36
        w_rok = 132
        y_title3 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)
        pdf.rect(0, y_title3, w_line, 5, style='F')
        pdf.set_xy(0 , y_title3)
        pdf.set_font('MontserratBold', '', self.text_size_subtitle)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 8, 6, 'Inventario Valores Rokeach',align="C", border=0)
        pdf.ln(5)
        pdf.set_xy(0 , pdf.get_y() + 2 )
        pdf.set_font('MontserratBold', '', self.text_size_normal)
        pdf.multi_cell(w_line - 14, 6, 'Lista valores Terminales',align="C", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, 'Los valores terminales se orientan hacia estados deseables de existencia.',align="J", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, 'Sus valores terminales son:',align="J", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '1 - Mentalidad abierta (abierto a nuevas ideas)',align="J", border=0)
        pdf.ln(2)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '2 - Imaginativo (atrevido, creativo) ',align="J", border=0)
        pdf.ln(2)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '3 - Honesto (sincero, honrado)',align="J", border=0)
        pdf.ln(5)
        pdf.set_xy(0 , pdf.get_y() + 2 )
        pdf.set_font('MontserratBold', '', self.text_size_normal)
        pdf.multi_cell(w_line - 14, 6, 'Lista valores Instrumentales',align="C", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, 'Los valores instrumentales son preferencias sobre rasgos de comportamiento deseables para lograr una condición o valor de vida.',align="J", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, 'Sus valores instrumentales son:',align="J", border=0)
        pdf.ln(5)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '1 - Igualdad (fraternidad, igualdad de oportunidades para todos)',align="J", border=0)
        pdf.ln(2)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '2 - Sabiduría (una comprensión madura de la vida) ',align="J", border=0)
        pdf.ln(2)
        pdf.set_xy(x_rok , pdf.get_y() + 2 )
        pdf.set_font(self.font_name, '', self.text_size_normal)
        pdf.multi_cell(w_rok, 6, '3 - Armonía interna (ausencia de conflictos internos)',align="J", border=0)
        ########################################################################
        pdf.add_page()
        #Materiales
        x = 0
        y = 30
        w = 220
        h = 5
        w_line = 220
        pdf.set_fill_color(86, 117, 206)  # light blue background
        pdf.rect(x, y, w, h, style='F')
        pdf.set_xy(x , y )
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(226, 222, 223)
        pdf.multi_cell(w - 8, 6, 'C - Materiales', border=0)
        pdf.ln(1)
        #Primer test
        y_title3 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)
        pdf.rect(0, y_title3, w_line, 5, style='F')
        pdf.set_xy(0 , y_title3)
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 8, 6, 'Test NEO-PI R',align="C", border=0)
        pdf.ln(5)
        # Test O*NET
        col_widths = [46, 155]
        pdf.set_font(self.font_name, '', 11)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Objetivo', 'El test ofrece una medida abreviada de las cinco principales dimensiones de la personalidad y de algunos de las facetas o rasgos que definen cada dimensión.'],
            ['Características', 'Consta de 240 items con respuestas en escala likert'],
            ['Confiabilidad', 'Entre 0,86 y 0,92'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (255, 255, 255)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 11)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                    pdf.set_font('MontserratBold', '', 12)
                elif i in (1, 2):
                    align = 'J'
                    pdf.set_font(self.font_name, '', 11)
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - ((2 * padding)), line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell((w+2) - ((2 * padding)), line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(3)
        #Segundo test
        y_title3 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)
        pdf.rect(0, y_title3, w_line, 5, style='F')
        pdf.set_xy(0 , y_title3)
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 8, 6, 'Test O*NET',align="C", border=0)
        pdf.ln(5)
        # Test O*NET
        col_widths = [46, 155]
        pdf.set_font(self.font_name, '', 11)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Objetivo', 'El Perfil de intereses O*NET puede ayudarlo a saber cuáles son sus intereses y cómo se relacionan al mundo del empleo. Puede encontrar lo que le gusta hacer.'],
            ['Características', 'Consta de 60 items con respuestas en escala likert'],
            ['Confiabilidad', '0,8'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (255, 255, 255)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 11)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                    pdf.set_font('MontserratBold', '', 12)
                elif i in (1, 2):
                    align = 'J'
                    pdf.set_font(self.font_name, '', 11)
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - ((2 * padding)), line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell((w+2) - ((2 * padding)), line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(3)
        #Tercer test
        y_title3 = pdf.get_y() + 3
        pdf.set_fill_color(120, 186, 202)
        pdf.rect(0, y_title3, w_line, 5, style='F')
        pdf.set_xy(0 , y_title3)
        pdf.set_font('MontserratBold', '', 12)
        pdf.set_text_color(26, 22, 23)
        pdf.multi_cell(w_line - 8, 6, 'Inventario Valores Rokeach',align="C", border=0)
        pdf.ln(5)
        # Test O*NET
        col_widths = [46, 155]
        pdf.set_font(self.font_name, '', 11)
        pdf.set_text_color(0, 0, 0)
        rows = [
            ['Objetivo', 'Identificar el sistema de valores'],
            ['Características', 'Se compone de dos listas de 18 valores que la persona tiene que ordenar de acuerdo a su criterio, siendo el primero de mayor importancia y el último de menor importancia para la persona'],
            ['Confiabilidad', 'Entre 0,71 y 0,60'],
        ]
        fill = False
        padding = 2  # mm padding inside cells
        line_height = 5  # height per text line in mm
        for row in rows:
            # decide fill color for the entire row
            if fill:
                row_fill = (255, 255, 255)
            else:
                row_fill = (255, 255, 255)

            # calculate lines needed per column
            col_lines = []
            max_lines = 1
            for i, cell_text in enumerate(row):
                max_w = col_widths[i] - ((2 * padding)+8)
                pdf.set_font(self.font_name, '' if i != 0 else '', 11)
                lines = _wrap_text_to_lines(pdf, cell_text, max_w)
                # post-process to avoid single-word orphan lines
                if len(lines) > 1:
                    lines = _rebalance_lines(pdf, lines, max_w)
                col_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)

            row_h = line_height * max_lines

            

            # add a slightly larger buffer to avoid drawing shapes that clip the page
            page_break_buffer = pdf.font_size * 2 + 12
            if _need_page_break(pdf, row_h + page_break_buffer):
                pdf.add_page()
                _draw_table_header()

            # starting x,y for the row: use left margin to ensure rectangles align to page margin
            x_start = self.margin
            y_start = pdf.get_y()

            # draw each cell: filled rectangle + text (center vertically)
            for i in range(len(row)):
                w = col_widths[i]
                h = row_h
                x = x_start + sum(col_widths[:i])
                y = y_start

                # draw filled rect with border
                pdf.set_fill_color(*row_fill)
                # use DF to draw and fill rectangle
                try:
                    pdf.rect(x, y, w, h, style='DF')
                except Exception:
                    # fallback if style not supported: fill then draw border
                    pdf.rect(x, y, w, h, style='F')
                    pdf.rect(x, y, w, h)

                # now draw text
                lines = col_lines[i]
                # compute text start y to vertically center single-line cells
                # Custom alignment: lef for the first column, center for others two and justify for the last
                if i == 0:
                    align = 'L'
                    pdf.set_font('MontserratBold', '', 12)
                elif i in (1, 2):
                    align = 'J'
                    pdf.set_font(self.font_name, '', 11)
                else:
                    align = 'J'
                if len(lines) == 1:
                    text_y = y + (h - line_height) / 2
                    pdf.set_xy(x + padding, text_y)
                    pdf.multi_cell(w - ((2 * padding)), line_height, lines[0], border=0, align=align)
                else:
                    # multi-line: start at top plus small padding
                    pdf.set_xy(x + padding, y + (line_height * 0))
                    pdf.multi_cell((w+2) - ((2 * padding)), line_height, '\n'.join(lines), border=0, align=align)

            # move cursor to the beginning of next row
            pdf.set_xy(x_start, y_start + row_h)
            fill = not fill
        pdf.ln(3)
        
        if to_buffer:
            # Convertir el string a bytes antes de pasarlo a BytesIO
            pdf_content = pdf.output(dest='S').encode('latin1')
            buffer = BytesIO(pdf_content)
            buffer.seek(0)
            return buffer
        else:
            pdf.output(out_path)
            print(f'PDF guardado en: {out_path}')


if __name__ == '__main__':
    lab_onet = ['R','I','A','S','E','C']
    val_onets = [45, 30, 60, 20, 10, 5]
    lab_neo = ['Neuroticismo','Extraversión','Apertura','Amabilidad','Responsabilidad']
    val_neo = [99, 22, 14, 22, 14]
    label = ['Ansiedad','Hostilidad','Depresión','Ansiedad Social','Impulsividad','Vulnerabilidad','Cordialidad','Gregarismo','Asertividad','Actividad','Busqueda de emociones','Emociones positivas','Fantasía','Estética','Sentimientos','Acciones','Ideas','Valores','Confianza','Franqueza','Altruismo','Actitud conciliadora','Modestia','Sensibilidad a los demás','Competencia','Orden','Sentido del deber','Necesidad de logro','Autodisciplina','Deliberación']
    valores = [55,65,45,70,60,50,40,30,80,90,60,70,50,40,30,55,65,45,70,60,50,40,30,80,90,60,70,50,40,30]
    id = 2193642
    info, df_onet_pd, df_zona, lista_onet = carga_onet_df(id)
    info["nombre"] = info["Nombre"]
    info["created"] = info["Fecha_aplicación"]
    info["edad"] = info["Edad"]
    info = info.to_dict(orient='list')
    df_onet_pd = df_onet_pd.to_dict(orient='list')
    df_neo_pi_pd, lista_neo_pi = carga_neo_pi_df(id)
    df_rokeach_pd= carga_rokeach_df(id)
    df_rokeach_pd = df_rokeach_pd.to_dict(orient='list')
    grafico_onet = grafico_bar_pdf(lab_onet, lista_onet, "Perfil O*NET")
    grafico_neopi = grafico_linea_personalidad_pdf(lab_neo, lista_neo_pi[30:] , "Perfil dimension global NEOPI-R")
    grafico_sub_neo_pi = grafico_linea_subdimension_pdf(label,lista_neo_pi[:30], "Perfil subdimensiones NEOPI-R")
    df_zona = df_zona.to_dict()
    df_neo_pi_pd = df_neo_pi_pd.to_dict(orient='list')
    
    print(df_onet_pd["zona"][0])
    print(df_zona[0])
    contexto = {
        'info': info,
        'df_onet_pd': df_onet_pd,
        'df_neo_pi_pd': df_neo_pi_pd,
        'df_rokeach_pd': df_rokeach_pd,
        'lista_onet': lista_onet,
        'lista_neo_pi': lista_neo_pi,
        'valores': valores,
        'grafico_onet': grafico_onet,
        'graf_neo_dimen': grafico_neopi,
        'graf_neo_sub': grafico_sub_neo_pi,
    }
    # Crear el PDF
    s = SamplePDF(contexto)
    print(f'Usando fuente: {s.font_name}')
    s.build('sample_report.pdf')
