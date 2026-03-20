# ... (Código anterior de la tabla y el gráfico)

# 3. Lógica de Visualización y Exportación
if not df_editado.empty:
    # --- Previsualización del Eje (Gráfico) ---
    fig, ax = plt.subplots(figsize=(10, 3))
    x_p = 0
    for _, f in df_editado.iterrows():
        # Dibujamos el perfil
        ax.plot([x_p, x_p + f["Longitud"]], [f["D_Inicial"]/2, f["D_Final"]/2], 'b')
        ax.plot([x_p, x_p + f["Longitud"]], [-f["D_Inicial"]/2, -f["D_Final"]/2], 'b')
        x_p += f["Longitud"]
    
    ax.set_aspect('equal')
    st.pyplot(fig) # Renderiza el gráfico

    # --- BLOQUE DEL BOTÓN (Asegúrate que esté alineado aquí) ---
    st.markdown("---") # Una línea divisoria estética
    st.subheader("📥 Exportar Diseño")
    
    try:
        # Generamos el contenido del DXF
        dxf_string = generar_dxf(df_editado)
        
        # Botón de descarga
        st.download_button(
            label="💾 Descargar Eje en formato DXF",
            data=dxf_string,
            file_name="eje_disenado.dxf",
            mime="application/dxf",
            use_container_width=True # Hace el botón más visible
        )
    except Exception as e:
        st.error(f"Error al generar el DXF: {e}")

else:
    st.info("💡 Agrega al menos una sección en la tabla superior para habilitar la descarga.")
