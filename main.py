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
    """Carga datos desde los parámetros de la URL si existen."""
    query_params = st.query_params
    if "data" in query_params:
        try:
            js_data = urllib.parse.unquote(query_params["data"])
            return pd.DataFrame(json.loads(js_data))
        except:
            pass
    # Datos por defecto si no hay URL
    return pd.DataFrame([
        {"Tag": "S1", "Longitud": 50.0, "D_Inicial": 20.0, "D_Final": 20.0},
        {"Tag": "S2", "Longitud": 30.0, "D_Inicial": 20.0, "D_Final": 40.0},
        {"Tag": "S3", "Longitud": 80.0, "D_Inicial": 40.0, "D_Final": 40.0}
    ])

def generar_dxf(df):
    """Genera el contenido del archivo DXF."""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    x_pos = 0.0
    for _, fila in df.iterrows():
        # Asegurar tipos numéricos
        L = float(fila["Longitud"])
        d1 = float(fila["D_Inicial"])
        d2 = float(fila["D_Final"])
        tag = str(fila["Tag"])
        x_fin = x_pos + L
        
        # Perfil (Superior e Inferior)
        msp.add_line((x_pos, d1/2), (x_fin, d2/2))
        msp.add_line((x_pos, -d1/2), (x_fin, -d2/2))
        
        # Línea vertical de sección
        msp.add_line((x_pos, d1/2), (x_pos, -d1/2))
        
        # Texto del Tag en el centro de la sección
        msp.add_text(tag, dxfattribs={'height': 2.0}).set_placement((x_pos + L/2, 0))
        
        x_pos = x_fin
    
    # Línea de cierre final
    ultimo_d2 = float(df.iloc[-1]["D_Final"])
    msp.add_line((x_pos, ultimo_d2/2), (x_pos, -ultimo_d2/2))
    
    # Eje de centro
    msp.add_line((0, 0), (x_pos, 0), dxfattribs={'linetype': 'CENTER'})

    # Exportar a un flujo de texto y luego convertir a bytes
    s_io = io.StringIO()
    doc.write(s_io)
    return s_io.getvalue().encode('utf-8')

# --- INTERFAZ DE USUARIO ---

st.title("⚙️ Generador Paramétrico de Ejes")
st.write("Edita la tabla, comparte el link o descarga el archivo para AutoCAD/SolidWorks.")

# 1. Cargar/Editar Datos
datos_iniciales = cargar_datos_url()
df_editado = st.data_editor(datos_iniciales, num_rows="dynamic", use_container_width=True)

if not df_editado.empty:
    # 2. Generar Enlace para Compartir
    json_data = df_editado.to_json(orient="records")
    encoded_data = urllib.parse.quote(json_data)
    # Nota: En despliegue real, cambia localhost por tu URL de streamlit.app
    share_link = f"https://tu-app.streamlit.app/?data={encoded_data}"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Vista Previa")
        fig, ax = plt.subplots(figsize=(10, 4))
        x_p = 0
        for _, f in df_editado.iterrows():
            # Dibujo de perfil
            ax.plot([x_p, x_p + f["Longitud"]], [f["D_Inicial"]/2, f["D_Final"]/2], 'b', lw=2)
            ax.plot([x_p, x_p + f["Longitud"]], [-f["D_Inicial"]/2, -f["D_Final"]/2], 'b', lw=2)
            # Líneas guía
            ax.vlines(x_p, -f["D_Inicial"]/2, f["D_Inicial"]/2, colors='gray', linestyles='--', alpha=0.4)
            # Tags
            ax.text(x_p + f["Longitud"]/2, 0, str(f["Tag"]), ha='center', va='center', fontsize=8, fontweight='bold')
            x_p += f["Longitud"]
            
        ax.axhline(0, color='black', linestyle='-.', lw=0.5)
        ax.set_aspect('equal')
        ax.grid(True, linestyle=':', alpha=0.3)
        st.pyplot(fig)

    with col2:
        st.subheader("Acciones")
        
        # Botón DXF
        try:
            dxf_data = generar_dxf(df_editado)
            st.download_button(
                label="💾 Descargar DXF",
                data=dxf_data,
                file_name="eje_disenado.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al generar DXF: {e}")

        # Enlace Compartir
        st.text_input("Enlace para compartir diseño:", share_link)
        st.caption("Copia y envía este link para que otros editen este mismo eje.")

else:
    st.warning("La tabla está vacía. Añade secciones para comenzar.")
