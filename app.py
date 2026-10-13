import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Configuración de la página
st.set_page_config(page_title="Sistema de Notas ACAD", page_icon="🎓", layout="wide")

st.title("🎓 Academia ACAD - Sistema de Consulta de Notas y Boletines")
st.markdown("Cargue el archivo Excel estandarizado para gestionar estudiantes, visualizar calificaciones y generar boletines en PDF.")

# Carga del archivo Excel
uploaded_file = st.sidebar.file_uploader("Cargar archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Leer las hojas
    try:
        df_estudiantes = pd.read_excel(uploaded_file, sheet_name="Estudiantes")
        df_notas = pd.read_excel(uploaded_file, sheet_name="Calificaciones")
        st.sidebar.success("¡Archivo cargado correctamente!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        st.stop()

    # Pestañas de la aplicación
    tab1, tab2 = st.tabs(["🔒 Portal de Estudiante (Consulta y Boletín)", "⚙️ Panel Administrativo"])

    with tab1:
        st.header("Consulta de Notas y Descarga de Boletines")
        
        # Selección de estudiante
        estudiantes_list = df_estudiantes['Nombres_y_Apellidos'].dropna().unique().tolist()
        estudiante_sel = st.selectbox("Seleccione el Estudiante:", estudiantes_list)

        if estudiante_sel:
            # Filtrar información
            est_info = df_estudiantes[df_estudiantes['Nombres_y_Apellidos'] == estudiante_sel].iloc[0]
            st.write(f"**Documento de Identidad:** {est_info.get('Documento_Identidad', 'N/A')} | **Estado:** {est_info.get('Estado', 'Activo')}")

            # Filtrar notas del estudiante
            notas_est = df_notas[df_notas['Nombre_Estudiante'] == estudiante_sel]

            if not notas_est.empty:
                st.subheader("Estado de Notas")
                periodo_sel = st.radio("Seleccione el Período:", [1, 2, 3, 4, "Todos los Períodos"], horizontal=True)

                if periodo_sel != "Todos los Períodos":
                    notas_mostrar = notas_est[notas_est['Periodo'] == periodo_sel]
                else:
                    notas_mostrar = notas_est

                cols_ver = ['Periodo', 'Nombre_Asignatura', 'Nota_1', 'Nota_2', 'Nota_3', 'Nota_4', 'Nota_Periodo', 'Nota_Final']
                cols_existentes = [c for c in cols_ver if c in notas_mostrar.columns]
                st.dataframe(notas_mostrar[cols_existentes], use_container_width=True)

                # Botón para generar Boletín PDF
                st.subheader("📄 Generar Boletín Escolar")
                if st.button("Crear Boletín en PDF"):
                    class PDF(FPDF):
                        def header(self):
                            self.set_font('Arial', 'B', 16)
                            self.cell(0, 10, 'ACADEMIA ACAD - BOLETÍN DE QUALIFICACIONES', 0, 1, 'C')
                            self.set_font('Arial', 'I', 10)
                            self.cell(0, 5, 'Informe Oficial de Rendimiento Académico', 0, 1, 'C')
                            self.ln(5)

                        def footer(self):
                            self.set_y(-15)
                            self.set_font('Arial', 'I', 8)
                            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

                    pdf = PDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 11)
                    
                    # Encabezado datos
                    pdf.cell(0, 8, f"Estudiante: {estudiante_sel}", 0, 1)
                    pdf.cell(0, 8, f"Documento: {est_info.get('Documento_Identidad', 'N/A')}", 0, 1)
                    pdf.ln(4)

                    # Tabla de Notas en PDF
                    pdf.set_fill_color(31, 78, 120)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font("Arial", 'B', 9)

                    # Columnas
                    pdf.cell(15, 8, "Per.", 1, 0, 'C', True)
                    pdf.cell(50, 8, "Asignatura", 1, 0, 'L', True)
                    pdf.cell(18, 8, "N1", 1, 0, 'C', True)
                    pdf.cell(18, 8, "N2", 1, 0, 'C', True)
                    pdf.cell(18, 8, "N3", 1, 0, 'C', True)
                    pdf.cell(18, 8, "N4", 1, 0, 'C', True)
                    pdf.cell(25, 8, "Nota Final", 1, 1, 'C', True)

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Arial", '', 9)

                    for idx, row in notas_est.iterrows():
                        pdf.cell(15, 7, str(row.get('Periodo', '')), 1, 0, 'C')
                        pdf.cell(50, 7, str(row.get('Nombre_Asignatura', '')), 1, 0, 'L')
                        pdf.cell(18, 7, str(row.get('Nota_1', '') if pd.notna(row.get('Nota_1')) else '-'), 1, 0, 'C')
                        pdf.cell(18, 7, str(row.get('Nota_2', '') if pd.notna(row.get('Nota_2')) else '-'), 1, 0, 'C')
                        pdf.cell(18, 7, str(row.get('Nota_3', '') if pd.notna(row.get('Nota_3')) else '-'), 1, 0, 'C')
                        pdf.cell(18, 7, str(row.get('Nota_4', '') if pd.notna(row.get('Nota_4')) else '-'), 1, 0, 'C')
                        pdf.cell(25, 7, str(row.get('Nota_Final', '') if pd.notna(row.get('Nota_Final')) else '-'), 1, 1, 'C')

                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    b64 = base64.b64encode(pdf_output).decode()
                    href = f'<a href="data:file/pdf;base64,{b64}" download="Boletin_{estudiante_sel.replace(" ", "_")}.pdf" style="background-color: #1F4E78; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">📥 Descargar Boletín PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron registros de notas para este estudiante.")

    with tab2:
        st.header("⚙️ Panel Administrativo")
        st.subheader("Estudiantes Registrados")
        st.dataframe(df_estudiantes, use_container_width=True)

        st.subheader("Registro Completo de Calificaciones")
        st.dataframe(df_notas, use_container_width=True)

else:
    st.info("👈 Por favor, carga el archivo Excel en la barra lateral izquierda para iniciar la aplicación.")
