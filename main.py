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
    """Recupera datos de la URL."""
    query_params = st.query_params
    if "data" in query_params:
        try:
            js_data = urllib.parse.unquote(query_params["data"])
            return pd.DataFrame(json.loads(js_data))
        except:
            pass
    return pd.DataFrame([
        {"Tag": "Seccion_1", "Longitud": 50.0, "D_Inicial": 20.0, "D_Final": 20.0},
        {"Tag": "Seccion_2", "Longitud": 30.0, "D_Inicial": 20.0, "D_Final": 40.0},
    ])

def generar_dxf(df):
    """Genera el archivo DXF corrigiendo el error de bytes/str."""
    # Crear documento R2010 (muy compatible)
    doc = ezdxf.new('R2010')
    
    # Tipo de línea para el centro
    if 'CENTER' not in doc.linetypes:
        doc.linetypes.new('CENTER', dxfattribs={'description': 'Eje', 'pattern': [2.0, -1.0, 0.5, -1.0]})
    
    msp = doc.modelspace()
    x_pos = 0.0
    
    for _, fila in df.iterrows():
        try:
            L = float(fila["Longitud"])
            d1 = float(fila["D_Inicial"])
            d2 = float(fila["D_Final"])
            tag = str(fila["Tag"])
        except:
            continue
            
        x_fin = x_pos + L
        
        # Geometría del eje
        msp.add_line((x_pos, d1/2), (x_fin, d2/2))
        msp.add_line((x_pos, -d1/2), (x_fin, -d2/2))
        msp.add_line((x_pos, d1/2), (x_pos, -d1/2))
        
        if tag:
            t = msp.add_text(tag, dxfattribs={'height': 2.5})
            t.set_placement((x_pos + L/2, 0), align=ezdxf.enums.TextEntityAlignment.CENTER)
        
        x_pos = x_fin
    
    # Cierre final
    if not df.empty:
        u_d2 = float(df.iloc[-1]["D_Final"])
        msp.add_line((x_pos, u_d2/2), (x_pos, -u_d2/2))
    
    # Eje central (color gris = 8)
    msp.add_line((0, 0), (x_pos, 0), dxfattribs={'linetype': 'CENTER', 'color': 8})

    # --- SOLUCIÓN AL ERROR DE BYTES/STR ---
    # 1. Escribimos a un StringWriter (Texto)
    out_text = io.StringIO()
    doc.write(out_text)
    # 2. Convertimos ese texto a Bytes para Streamlit
    return out_text.getvalue().encode('utf-8')

# --- INTERFAZ ---

st.title("⚙️ Generador de Ejes (Versión Final)")

# 1. Editor
datos_ini = cargar_datos_url()
df_editado = st.data_editor(datos_ini, num_rows="dynamic", use_container_width=True)

if not df_editado.empty:
    # Generar Link
    json_str = df_editado.to_json(orient="records")
    link_data = urllib.parse.quote(json_str)
    url_actual = f"https://tu-app.streamlit.app/?data={link_data}"

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Vista Previa")
        fig, ax = plt.subplots(figsize=(10, 3))
        curr_x = 0
        for _, f in df_editado.iterrows():
            ax.plot([curr_x, curr_x + f["Longitud"]], [f["D_Inicial"]/2, f["D_Final"]/2], color='#1f77b4', lw=2)
            ax.plot([curr_x, curr_x + f["Longitud"]], [-f["D_Inicial"]/2, -f["D_Final"]/2], color='#1f77b4', lw=2)
            ax.vlines(curr_x, -f["D_Inicial"]/2, f["D_Inicial"]/2, colors='gray', linestyles=':', alpha=0.5)
            curr_x += f["Longitud"]
        
        ax.axhline(0, color='black', linestyle='-.', lw=0.8)
        ax.set_aspect('equal')
        st.pyplot(fig)

    with c2:
        st.subheader("Exportar")
        try:
            # Ahora la función devuelve bytes reales
            dxf_final = generar_dxf(df_editado)
            st.download_button(
                label="💾 Descargar DXF para AutoCAD",
                data=dxf_final,
                file_name="eje_disenado.dxf",
                mime="application/dxf",
                use_container_width=True
            )
            st.success("Archivo listo para descargar")
        except Exception as e:
            st.error(f"Error técnico: {e}")

        st.text_input("🔗 Enlace para compartir:", url_actual)
