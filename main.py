import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import ezdxf
import io
import json
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Ejes Pro", layout="wide")

# --- FUNCIONES DE LÓGICA ---

def cargar_datos_url():
    """Recupera datos de la URL para permitir el trabajo colaborativo."""
    query_params = st.query_params
    if "data" in query_params:
        try:
            js_data = urllib.parse.unquote(query_params["data"])
            return pd.DataFrame(json.loads(js_data))
        except:
            pass
    # Valores iniciales por defecto
    return pd.DataFrame([
        {"Tag": "Seccion_1", "Longitud": 50.0, "D_Inicial": 20.0, "D_Final": 20.0},
        {"Tag": "Seccion_2", "Longitud": 30.0, "D_Inicial": 20.0, "D_Final": 40.0},
    ])

def generar_dxf(df):
    """Genera el archivo DXF compatible con AutoCAD (Versión R2010)."""
    # Crear documento nuevo
    doc = ezdxf.new('R2010')
    
    # Configurar tipo de línea para el eje central
    if 'CENTER' not in doc.linetypes:
        doc.linetypes.new('CENTER', dxfattribs={
            'description': 'Centro ____ _ ____',
            'pattern': [2.0, 1.25, 0.25, 1.25]
        })
    
    msp = doc.modelspace()
    x_pos = 0.0
    
    for _, fila in df.iterrows():
        try:
            L = float(fila["Longitud"])
            d1 = float(fila["D_Inicial"])
            d2 = float(fila["D_Final"])
            tag = str(fila["Tag"])
        except (ValueError, TypeError):
            continue # Ignorar filas con datos no numéricos
            
        x_fin = x_pos + L
        
        # 1. Dibujar Perfil Superior e Inferior
        msp.add_line((x_pos, d1/2), (x_fin, d2/2))
        msp.add_line((x_pos, -d1/2), (x_fin, -d2/2))
        
        # 2. Línea vertical de inicio de sección
        msp.add_line((x_pos, d1/2), (x_pos, -d1/2))
        
        # 3. Añadir Texto (Tag) centrado en la sección
        if tag:
            txt = msp.add_text(tag, dxfattribs={'height': 2.5})
            # Alineación centrada para que AutoCAD no lo ignore
            txt.set_placement((x_pos + L/2, 0), align=ezdxf.enums.TextEntityAlignment.CENTER)
        
        x_pos = x_fin
    
    # 4. Línea vertical de cierre final
    if not df.empty:
        u_d2 = float(df.iloc[-1]["D_Final"])
        msp.add_line((x_pos, u_d2/2), (x_pos, -u_d2/2))
    
    # 5. Eje de simetría (Línea de centro)
    msp.add_line((0, 0), (x_pos, 0), dxfattribs={'linetype': 'CENTER', 'color': 8})

    # --- EXPORTACIÓN ROBUSTA ---
    # Usar BytesIO evita errores de codificación de texto (UTF-8 vs ANSI)
    buffer = io.BytesIO()
    doc.write(buffer) 
    return buffer.getvalue()

# --- INTERFAZ DE USUARIO ---

st.title("⚙️ Generador Paramétrico de Ejes (DXF)")
st.info("Diseña, comparte mediante enlace y exporta directamente a AutoCAD o SolidWorks.")

# Paso 1: Editor de datos
datos_ini = cargar_datos_url()
df_editado = st.data_editor(datos_ini, num_rows="dynamic", use_container_width=True)

if not df_editado.empty:
    # Paso 2: Generar Link de Compartir (Base 64/URL Encoding)
    json_str = df_editado.to_json(orient="records")
    link_data = urllib.parse.quote(json_str)
    # Reemplazar con la URL real al desplegar
    url_actual = f"https://tu-app.streamlit.app/?data={link_data}"

    col_grafico, col_acciones = st.columns([2, 1])

    with col_grafico:
        st.subheader("Vista Previa del Perfil")
        fig, ax = plt.subplots(figsize=(10, 3))
        curr_x = 0
        for _, f in df_editado.iterrows():
            # Dibujo de líneas azules para el contorno
            ax.plot([curr_x, curr_x + f["Longitud"]], [f["D_Inicial"]/2, f["D_Final"]/2], color='#1f77b4', lw=2)
            ax.plot([curr_x, curr_x + f["Longitud"]], [-f["D_Inicial"]/2, -f["D_Final"]/2], color='#1f77b4', lw=2)
            # Líneas de división grises
            ax.vlines(curr_x, -f["D_Inicial"]/2, f["D_Inicial"]/2, colors='gray', linestyles=':', alpha=0.5)
            curr_x += f["Longitud"]
        
        ax.axhline(0, color='black', linestyle='-.', lw=0.8) # Eje central
        ax.set_aspect('equal')
        ax.grid(True, which='both', linestyle='--', alpha=0.2)
        st.pyplot(fig)

    with col_acciones:
        st.subheader("Exportar y Compartir")
        
        # Botón de Descarga DXF
        try:
            dxf_final = generar_dxf(df_editado)
            st.download_button(
                label="💾 Descargar para AutoCAD (.DXF)",
                data=dxf_final,
                file_name="eje_mecanico.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Fallo en generación: {e}")

        st.markdown("---")
        # Campo para copiar el link
        st.text_input("🔗 Enlace colaborativo:", url_actual)
        st.caption("Cualquier persona con este link podrá continuar editando este diseño.")

else:
    st.warning("Añade filas a la tabla para generar el diseño.")
