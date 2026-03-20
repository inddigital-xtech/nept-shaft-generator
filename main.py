import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import ezdxf
import io
import json
import urllib.parse

st.set_page_config(page_title="Eje Compartible", layout="wide")

# 1. Función para leer datos de la URL
def cargar_datos_url():
    query_params = st.query_params
    if "data" in query_params:
        try:
            # Decodificar el JSON de la URL
            js_data = urllib.parse.unquote(query_params["data"])
            return pd.DataFrame(json.loads(js_data))
        except:
            pass
    return pd.DataFrame([
        {"Tag": "S1", "Longitud": 50.0, "D_Inicial": 20.0, "D_Final": 20.0},
        {"Tag": "S2", "Longitud": 30.0, "D_Inicial": 20.0, "D_Final": 40.0},
    ])

st.title("⚙️ Diseñador de Ejes Colaborativo")

# 2. Cargar datos (prioriza la URL si existe)
datos_actuales = cargar_datos_url()

# 3. Tabla Editable
df_editado = st.data_editor(datos_actuales, num_rows="dynamic", use_container_width=True)

# 4. Generar Enlace para Compartir
if not df_editado.empty:
    # Convertir tabla a JSON y luego a formato URL
    json_data = df_editado.to_json(orient="records")
    encoded_data = urllib.parse.quote(json_data)
    
    # Construir la URL (Streamlit detecta la base automáticamente)
    url_base = "https://tu-app.streamlit.app" # Reemplazar con tu URL real al desplegar
    share_link = f"{url_base}/?data={encoded_data}"
    
    st.info("🔗 **Enlace para compartir:**")
    st.code(share_link)
    st.write("Copia este enlace y envíaselo a otra persona para que vea y edite este diseño.")

# 5. Visualización del Eje
if not df_editado.empty:
    fig, ax = plt.subplots(figsize=(10, 3))
    x_p = 0
    for _, f in df_editado.iterrows():
        ax.plot([x_p, x_p + f["Longitud"]], [f["D_Inicial"]/2, f["D_Final"]/2], 'b', lw=2)
        ax.plot([x_p, x_p + f["Longitud"]], [-f["D_Inicial"]/2, -f["D_Final"]/2], 'b', lw=2)
        ax.vlines(x_p, -f["D_Inicial"]/2, f["D_Inicial"]/2, colors='gray', linestyles='--', alpha=0.5)
        x_p += f["Longitud"]
    
    ax.set_aspect('equal')
    ax.axhline(0, color='black', linestyle='-.', lw=0.5)
    st.pyplot(fig)

    # --- Función DXF ---
    # (Aquí iría la función de exportación DXF del paso anterior)
