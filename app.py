import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Sistema de Notas ACAD", page_icon="🎓", layout="wide")

# =========================================================================
# BARRA LATERAL: LOGOTIPO Y ENLACES INSTITUCIONALES (WEB Y REDES)
# =========================================================================
st.sidebar.header("🏫 Academia ACAD")

# Mostrar el logo en la barra lateral de la app web
logo_path = "logos-acad-5.png"
try:
    st.sidebar.image(logo_path, width=120)
except Exception:
    pass

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Canales Oficiales")
st.sidebar.markdown("[🌍 Visita nuestra Página Web](https://acadcol.com/)")
st.sidebar.markdown("[📘 Facebook oficial](https://www.facebook.com/AcadaCol)")
st.sidebar.markdown("[📸 Instagram oficial](https://www.instagram.com/acadcol/)")
st.sidebar.markdown("[📸 TikTok oficial](https://www.tiktok.com/@acadcol)")
st.sidebar.markdown("[💬 Canal de WhatsApp](https://api.whatsapp.com/send/?phone=573152402230)")
st.sidebar.markdown("---")

# =========================================================================
# CONFIGURACIÓN DE LOS GRUPOS (Múltiples Libros de Google Sheets)
# =========================================================================
GRUPOS_SHEETS = {
    "Grupo 1 (Ej. Grupo 01)": "Phttps://docs.google.com/spreadsheets/d/1xB6F4__Zxr9lSDJBtIY8QolzlwSfMsZF/edit?usp=sharing&ouid=116057535961518395264&rtpof=true&sd=true",
    "Grupo 2 (Ej. Grupo 02)": "https://docs.google.com/spreadsheets/d/1TrMi2yLmjGnEayaKdGwDqGjLl3wLbuMb/edit?usp=sharing&ouid=116057535961518395264&rtpof=true&sd=true",
    "Grupo 3 (Ej. Grado 10C)": "https://docs.google.com/spreadsheets/d/1uRZK8txP9TurJ3Z_0njPHdAYxtKqfcTm/edit?usp=sharing&ouid=116057535961518395264&rtpof=true&sd=true",
    "Grupo 4 (Ej. Grado 11D)": "PEGA_AQUI_EL_ENLACE_DEL_GRUPO_4"
}

st.sidebar.header("📚 Selección de Grupo")
grupo_seleccionado = st.sidebar.selectbox("Seleccione el grupo a consultar:", list(GRUPOS_SHEETS.keys()))
sheet_input_url = GRUPOS_SHEETS[grupo_seleccionado]

st.title("🎓 Academia ACAD - Consulta de Informes Académicos")
st.markdown("Sistema oficial de consulta de calificaciones y generación de informes institucionales.")

@st.cache_data(ttl=30) 
def cargar_datos_desde_drive(sheet_url):
    try:
        if "/d/" in sheet_url:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            url_estudiantes = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Estudiantes"
            url_calificaciones = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Calificaciones"
            
            df_est = pd.read_csv(url_estudiantes)
            df_not = pd.read_csv(url_calificaciones)
            return df_est, df_not
        else:
            return None, None
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets de este grupo: {e}")
        return None, None

if sheet_input_url and "PEGA_AQUI" not in sheet_input_url:
    df_estudiantes, df_notas = cargar_datos_desde_drive(sheet_input_url)
else:
    df_estudiantes, df_notas = None, None

if df_estudiantes is not None and df_notas is not None:

    st.sidebar.success(f"Conectado a: {grupo_seleccionado}")

    tab1, tab2 = st.tabs(["🔒 Portal de Consulta por Documento", "⚙️ Panel Administrativo (Secretaría)"])

    with tab1:
        st.header(f"Consulta de Informe - {grupo_seleccionado}")
        st.markdown("Digite el número de documento de identidad del estudiante para acceder a su expediente de notas.")

        doc_ingresado = st.text_input("Número de Documento de Identidad:", type="default")

        if doc_ingresado:
            df_estudiantes['Documento_Identidad'] = df_estudiantes['Documento_Identidad'].astype(str).str.strip()
            doc_buscado = doc_ingresado.strip()

            estudiante_encontrado = df_estudiantes[df_estudiantes['Documento_Identidad'] == doc_buscado]

            if not estudiante_encontrado.empty:
                est_info = estudiante_encontrado.iloc[0]
                estudiante_sel = est_info['Nombres_y_Apellidos']
                
                st.success(f"¡Estudiante encontrado: **{estudiante_sel}**!")
                st.write(f"**Documento:** {est_info.get('Documento_Identidad', 'N/A')} | **Estado:** {est_info.get('Estado', 'Activo')}")

                notas_est = df_notas[df_notas['Nombre_Estudiante'] == estudiante_sel]

                if not notas_est.empty:
                    st.subheader("Estado de Notas en Pantalla")
                    periodo_sel = st.radio("Seleccione el Período a consultar en pantalla:", [1, 2, 3, 4, "Todos los Períodos"], horizontal=True, key="p_pantalla")

                    if periodo_sel != "Todos los Períodos":
                        notas_mostrar = notas_est[notas_est['Periodo'] == periodo_sel]
                    else:
                        notas_mostrar = notas_est

                    cols_ver = ['Periodo', 'Nombre_Asignatura', 'Nota_1', 'Nota_2', 'Nota_3', 'Nota_4', 'Nota_Periodo', 'Nota_Final']
                    cols_existentes = [c for c in cols_ver if c in notas_mostrar.columns]
                    st.dataframe(notas_mostrar[cols_existentes], use_container_width=True)

                    st.subheader("📄 Generar Informe de Notas en PDF")
                    periodo_pdf = st.selectbox("Seleccione el período para el Informe PDF:", [1, 2, 3, 4, "Todos los Períodos"], key="p_pdf")
                    
                    # Observaciones seguras (sin edición libre del usuario)
                    observaciones_txt = "El estudiante demuestra un buen desempeño académico y compromiso institucional durante este período."
                    if 'Observaciones' in est_info and pd.notna(est_info['Observaciones']):
                        observaciones_txt = str(est_info['Observaciones'])
                    elif not notas_est.empty and 'Observaciones' in notas_est.columns:
                        obs_fila = notas_est[notas_est['Periodo'] == periodo_pdf]
                        if not obs_fila.empty and pd.notna(obs_fila.iloc[0].get('Observaciones')):
                            observaciones_txt = str(obs_fila.iloc[0]['Observaciones'])

                    st.info(f"**Observaciones institucionales para el informe:**\n\n_{observaciones_txt}_")

                    if st.button("Crear Informe de Notas en PDF"):
                        fecha_actual = datetime.now().strftime("%d/%m/%Y")

                        class PDF(FPDF):
                            def header(self):
                                try:
                                    self.image(logo_path, 10, 8, 30)
                                except Exception:
                                    pass
                                
                                self.set_font('Arial', 'B', 15)
                                self.cell(0, 8, 'ACADEMIA ACAD - INFORME DE CALIFICACIONES', 0, 1, 'C')
                                self.set_font('Arial', 'I', 10)
                                titulo_per = f"Período: {periodo_pdf}" if periodo_pdf != "Todos los Períodos" else "Informe Consolidado (Todos los Períodos)"
                                self.cell(0, 5, titulo_per, 0, 1, 'C')
                                self.set_font('Arial', '', 9)
                                self.cell(0, 5, f"Fecha de generación: {fecha_actual}", 0, 1, 'C')
                                self.ln(5)

                            def footer(self):
                                self.set_y(-15)
                                self.set_font('Arial', 'I', 8)
                                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

                        pdf = PDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 11)
                        
                        pdf.cell(0, 7, f"Estudiante: {estudiante_sel}", 0, 1)
                        pdf.cell(0, 7, f"Documento: {est_info.get('Documento_Identidad', 'N/A')}", 0, 1)
                        pdf.ln(3)

                        pdf.set_fill_color(31, 78, 120)
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font("Arial", 'B', 9)

                        pdf.cell(15, 8, "Per.", 1, 0, 'C', True)
                        pdf.cell(50, 8, "Asignatura", 1, 0, 'L', True)
                        pdf.cell(18, 8, "N1", 1, 0, 'C', True)
                        pdf.cell(18, 8, "N2", 1, 0, 'C', True)
                        pdf.cell(18, 8, "N3", 1, 0, 'C', True)
                        pdf.cell(18, 8, "N4", 1, 0, 'C', True)
                        pdf.cell(25, 8, "Nota Final", 1, 1, 'C', True)

                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Arial", '', 9)

                        if periodo_pdf != "Todos los Períodos":
                            notas_a_imprimir = notas_est[notas_est['Periodo'] == periodo_pdf]
                        else:
                            notas_a_imprimir = notas_est

                        for idx, row in notas_a_imprimir.iterrows():
                            pdf.cell(15, 7, str(row.get('Periodo', '')), 1, 0, 'C')
                            pdf.cell(50, 7, str(row.get('Nombre_Asignatura', '')), 1, 0, 'L')
                            pdf.cell(18, 7, str(row.get('Nota_1', '') if pd.notna(row.get('Nota_1')) else '-'), 1, 0, 'C')
                            pdf.cell(18, 7, str(row.get('Nota_2', '') if pd.notna(row.get('Nota_2')) else '-'), 1, 0, 'C')
                            pdf.cell(18, 7, str(row.get('Nota_3', '') if pd.notna(row.get('Nota_3')) else '-'), 1, 0, 'C')
                            pdf.cell(18, 7, str(row.get('Nota_4', '') if pd.notna(row.get('Nota_4')) else '-'), 1, 0, 'C')
                            pdf.cell(25, 7, str(row.get('Nota_Final', '') if pd.notna(row.get('Nota_Final')) else '-'), 1, 1, 'C')

                        pdf.ln(6)
                        pdf.set_font("Arial", 'B', 10)
                        pdf.cell(0, 6, "Observaciones Institucionales:", 0, 1)
                        pdf.set_font("Arial", '', 9)
                        pdf.multi_cell(0, 5, observaciones_txt)

                        pdf_output = pdf.output(dest='S').encode('latin-1')
                        b64 = base64.b64encode(pdf_output).decode()
                        nombre_archivo = f"Informe_{estudiante_sel.replace(' ', '_')}_Periodo_{periodo_pdf}.pdf"
                        href = f'<a href="data:file/pdf;base64,{b64}" download="{nombre_archivo}" style="background-color: #1F4E78; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">📥 Descargar Informe en PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                else:
                    st.warning("No se encontraron registros de notas para este estudiante en este grupo.")
            else:
                st.error("❌ El número de documento ingresado no se encuentra registrado en este grupo. Verifique e intente nuevamente.")

    with tab2:
        st.header(f"⚙️ Panel Administrativo - {grupo_seleccionado}")
        st.markdown("Área protegida para la administración del grupo seleccionado.")

        password_ingresada = st.text_input("Ingrese la Contraseña de Administración:", type="password", key="pwd_admin")
        CLAVE_ADMIN = "Acad2019*" 

        if password_ingresada:
            if password_ingresada == CLAVE_ADMIN:
                st.success("¡Acceso autorizado!")
                st.subheader("Estudiantes Registrados en este Grupo")
                st.dataframe(df_estudiantes, use_container_width=True)
                
                st.subheader("Calificaciones del Grupo")
                st.dataframe(df_notas, use_container_width=True)
            else:
                st.error("❌ Contraseña incorrecta. Acceso denegado.")
        else:
            st.info("🔒 Por favor, ingrese la contraseña institucional para visualizar los registros de este grupo.")

else:
    st.error("⚠️ Por favor, asegúrese de reemplazar los enlaces de prueba en el diccionario `GRUPOS_SHEETS` por los enlaces reales de sus Google Sheets.")
