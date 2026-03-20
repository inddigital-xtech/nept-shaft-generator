import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import ezdxf
import io

# 1. Configuración y Título
st.set_page_config(page_title="Generador de Ejes DXF", layout="wide")
st.title("⚙️ Generador de Ejes con Exportación DXF")

# 2. Función para generar el archivo DXF (Debe estar arriba para que Python la conozca)
def generar_dxf(df):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    x_pos = 0
    for _, fila in df.iterrows():
        L = float(fila["Longitud"])
        d1 = float(fila["D_Inicial"])
        d2 = float(fila["D_Final"])
        x_fin = x_pos + L
        # Dibujar líneas del perfil
        msp.add_line((x_pos, d1/2), (x_fin, d2/2))
        msp.add_line((x_pos, -d1/2), (x_fin, -d2/2))
        msp.add_line((x_pos, d1/2), (x_pos, -d1/2)) # Vertical inicial
        x_pos = x_fin
    msp.add_line((x_pos, d2/2), (x_pos, -d2/2)) # Vertical final
    msp.add_line((0, 0), (x_pos, 0), dxfattribs={'linetype': 'CENTER'}) # Eje central
    
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

# 3. Datos iniciales y TABLA (Aquí se define df_editado)
datos_ini = pd.DataFrame([
    {"Tag": "S1", "Longitud": 50.0, "D_Inicial": 20.0, "D_Final": 20.0},
    {"Tag": "S2", "Longitud": 30.0, "D_Inicial": 20.0, "D_Final": 40.0}
])

st.subheader("1. Ingresa las secciones del eje")
# MUY IMPORTANTE: Aquí asignamos el resultado a la variable df_editado
df_editado = st.data_editor(datos_ini, num_rows="dynamic", use_container_width=True)

# 4. Gráfico y Botón (Ahora df_editado ya existe)
if not df_editado.empty:
    st.subheader("2. Previsualización y Descarga")
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

    # Botón de Descarga
    dxf_string = generar_dxf(df_editado)
    st.download_button(
        label="💾 Descargar archivo DXF",
        data=dxf_string,
        file_name="eje_disenado.dxf",
        mime="application/dxf"
    )
