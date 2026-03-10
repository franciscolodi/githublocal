import streamlit as st
from app_usuarios import GestorUsuarios

# inicializar gestor
gestor = GestorUsuarios()

st.title("📱 Sistema de Gestión de Usuarios")

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Agregar usuario",
        "Listar usuarios",
        "Buscar usuario",
        "Estadísticas"
    ]
)

# -------------------------
# AGREGAR USUARIO
# -------------------------

if menu == "Agregar usuario":

    st.header("➕ Nuevo usuario")

    nombre = st.text_input("Nombre")
    email = st.text_input("Email")
    edad = st.number_input("Edad", min_value=0, max_value=120)
    ciudad = st.text_input("Ciudad")

    if st.button("Guardar usuario"):

        ok = gestor.agregar_usuario(
            nombre,
            email,
            edad if edad > 0 else None,
            ciudad if ciudad else None
        )

        if ok:
            st.success("Usuario agregado correctamente")
        else:
            st.error("No se pudo agregar el usuario")

# -------------------------
# LISTAR USUARIOS
# -------------------------

elif menu == "Listar usuarios":

    st.header("📋 Lista de usuarios")

    gestor.cursor.execute("SELECT * FROM users WHERE activo = 1")

    usuarios = gestor.cursor.fetchall()

    if usuarios:

        import pandas as pd

        df = pd.DataFrame(
            usuarios,
            columns=[
                "ID",
                "Nombre",
                "Email",
                "Edad",
                "Ciudad",
                "Fecha registro",
                "Activo"
            ]
        )

        st.dataframe(df)

    else:
        st.info("No hay usuarios")

# -------------------------
# BUSCAR USUARIO
# -------------------------

elif menu == "Buscar usuario":

    st.header("🔍 Buscar usuario")

    criterio = st.selectbox(
        "Buscar por",
        ["nombre", "email", "ciudad"]
    )

    valor = st.text_input("Valor")

    if st.button("Buscar"):

        query = f"""
        SELECT * FROM users
        WHERE {criterio} LIKE ?
        AND activo = 1
        """

        gestor.cursor.execute(query, (f"%{valor}%",))

        resultados = gestor.cursor.fetchall()

        if resultados:

            import pandas as pd

            df = pd.DataFrame(
                resultados,
                columns=[
                    "ID",
                    "Nombre",
                    "Email",
                    "Edad",
                    "Ciudad",
                    "Fecha registro",
                    "Activo"
                ]
            )

            st.dataframe(df)

        else:
            st.warning("No se encontraron resultados")

# -------------------------
# ESTADÍSTICAS
# -------------------------

elif menu == "Estadísticas":

    st.header("📊 Estadísticas")

    gestor.cursor.execute("SELECT COUNT(*) FROM users")
    total = gestor.cursor.fetchone()[0]

    gestor.cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
    activos = gestor.cursor.fetchone()[0]

    gestor.cursor.execute("SELECT AVG(edad) FROM users WHERE edad IS NOT NULL")
    edad_prom = gestor.cursor.fetchone()[0]

    st.metric("Total usuarios", total)
    st.metric("Usuarios activos", activos)

    if edad_prom:
        st.metric("Edad promedio", round(edad_prom,1))
