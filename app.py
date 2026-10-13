import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Configuración de la página
st.set_page_config(page_title="Sistema de Notas ACAD", page_icon="🎓", layout="wide")

st.title("🎓 Academia ACAD - Sistema de Consulta de Notas e Informes")
st.markdown("Sistema conectado con Google Sheets para la gestión de notas y generación de informes personalizados.")

# Campo en la barra lateral para ingresar la URL de Google Sheets
st.sidebar.header("⚙️ Configuración de Datos")
sheet_input_url = st.sidebar.text_input("Enlace de Google Sheets:", value="https://docs.google.com/spreadsheets/d/TU_ID_DE_LA_HOJA/edit?usp=sharing")

# Opcional: Subir un logotipo institucional para el PDF
logo_file = st.sidebar.file_uploader("Subir Logotipo de la Academia (Opcional, formato PNG/JPG)", type=["png", "jpg", "jpeg"])

@st.cache_data(ttl=60)
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
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None, None

if sheet_input_url and "TU_ID" not in sheet_input_url:
    df_estudiantes, df_notas = cargar_datos_desde_drive(sheet_input_url)
else:
    df_estudiantes, df_notas = None, None

if df_estudiantes is not None and df_notas is not None:
    st.sidebar.success("¡Conectado a Google Drive con éxito!")

    tab1, tab2 = st.tabs(["🔒 Portal de Secretaría / Estudiante (Informes)", "⚙️ Panel Administrativo"])

    with tab1:
        st.header("Consulta de Notas y Generación de Informes")
        
        estudiantes_list = df_estudiantes['Nombres_y_Apellidos'].dropna().unique().tolist()
        estudiante_sel = st.selectbox("Seleccione el Estudiante:", estudiantes_list)

        if estudiante_sel:
            est_info = df_estudiantes[df_estudiantes['Nombres_y_Apellidos'] == estudiante_sel].iloc[0]
            st.write(f"**Documento de Identidad:** {est_info.get('Documento_Identidad', 'N/A')} | **Estado:** {est_info.get('Estado', 'Activo')}")

            notas_est = df_notas[df_notas['Nombre_Estudiante'] == estudiante_sel]

            if not notas_est.empty:
                st.subheader("Estado de Notas en Pantalla")
                periodo_sel = st.radio("Seleccione el Período a consultar en pantalla:", [1, 2, 3, 4, "Todos los Períodos"], horizontal=True)

                if periodo_sel != "Todos los Períodos":
                    notas_mostrar = notas_est[notas_est['Periodo'] == periodo_sel]
                else:
                    notas_mostrar = notas_est

                cols_ver = ['Periodo', 'Nombre_Asignatura', 'Nota_1', 'Nota_2', 'Nota_3', 'Nota_4', 'Nota_Periodo', 'Nota_Final']
                cols_existentes = [c for c in cols_ver if c in notas_mostrar.columns]
                st.dataframe(notas_mostrar[cols_existentes], use_container_width=True)

                st.subheader("📄 Generar Informe de Notas en PDF")
                periodo_pdf = st.selectbox("Seleccione el período para el Informe PDF:", [1, 2, 3, 4, "Todos los Períodos"])
                
                # Espacio para ingresar observaciones personalizadas
                observaciones_txt = st.text_area("Observaciones o Comportamiento del Estudiante para el Informe:", 
                                                 value="El estudiante demuestra un buen desempeño académico y compromiso institucional durante este período.")

                if st.button("Crear Informe de Notas en PDF"):
                    
                    # Guardar temporalmente el logo si se subió
                    logo_path = None
                    if logo_file is not None:
                        logo_path = "temp_logo.png"
                        with open(logo_path, "wb") as f:
                            f.write(logo_file.getbuffer())

                    class PDF(FPDF):
                        def header(self):
                            if logo_path:
                                try:
                                    self.image(logo_path, 10, 8, 22)
                                except:
                                    pass
                            self.set_font('Arial', 'B', 15)
                            self.cell(0, 8, 'ACADEMIA ACAD - INFORME DE CALIFICACIONES', 0, 1, 'C')
                            self.set_font('Arial', 'I', 10)
                            titulo_per = f"Período: {periodo_pdf}" if periodo_pdf != "Todos los Períodos" else "Informe Consolidado (Todos los Períodos)"
                            self.cell(0, 5, titulo_per, 0, 1, 'C')
                            self.ln(8)

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

                    # Tabla de calificaciones
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

                    # Sección de Observaciones en el PDF
                    pdf.ln(6)
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 6, "Observaciones Institucionales:", 0, 1)
                    pdf.set_font("Arial", '', 9)
                    pdf.multi_cell(0, 5, observaciones_txt)

                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    b64 = base64.b64encode(pdf_output).decode()
                    nombre_archivo = f"Informe_Notas_{estudiante_sel.replace(' ', '_')}_Periodo_{periodo_pdf}.pdf"
                    href = f'<a href="data:file/pdf;base64,{b64}" download="{nombre_archivo}" style="background-color: #1F4E78; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">📥 Descargar Informe en PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron registros de notas para este estudiante.")

    with tab2:
        st.header("⚙️ Panel Administrativo")
        st.subheader("Estudiantes Registrados")
        st.dataframe(df_estudiantes, use_container_width=True)
        st.subheader("Calificaciones")
        st.dataframe(df_notas, use_container_width=True)

else:
    st.info("👈 Por favor, pega el enlace de tu Google Sheet en la barra lateral izquierda para conectar el sistema.")
