import streamlit as st
import pickle
import sqlite3
from app_usuarios import GestorUsuarios

# -------------------------
# INICIALIZAR GESTOR
# -------------------------

gestor = GestorUsuarios()

# -------------------------
# CARGAR MODELO
# -------------------------

with open("model.pkl","rb") as f:
    model = pickle.load(f)

# -------------------------
# CREAR TABLA PREDICCIONES
# -------------------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT,
input_value REAL,
prediction REAL,
fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# -------------------------
# INTERFAZ
# -------------------------

st.title("🤖 Demo ML App")

menu = st.sidebar.selectbox(
    "Menú",
    ["Login","Registro","Predicción"]
)

# -------------------------
# REGISTRO
# -------------------------

if menu == "Registro":

    st.header("Crear usuario")

    nombre = st.text_input("Nombre")
    email = st.text_input("Email")
    edad = st.number_input("Edad",0,120)
    ciudad = st.text_input("Ciudad")

    if st.button("Registrar"):

        ok = gestor.agregar_usuario(
            nombre,
            email,
            edad if edad > 0 else None,
            ciudad if ciudad else None
        )

        if ok:
            st.success("Usuario creado")
        else:
            st.error("No se pudo crear usuario")

# -------------------------
# LOGIN
# -------------------------

elif menu == "Login":

    st.header("Login")

    email = st.text_input("Email")

    if st.button("Ingresar"):

        gestor.cursor.execute(
            "SELECT * FROM users WHERE email = ? AND activo = 1",
            (email,)
        )

        user = gestor.cursor.fetchone()

        if user:

            st.session_state["user"] = email
            st.success("Login correcto")

        else:

            st.error("Usuario no encontrado")

# -------------------------
# PREDICCIÓN
# -------------------------

elif menu == "Predicción":

    if "user" not in st.session_state:

        st.warning("Debes iniciar sesión")

    else:

        st.header("Predicción con modelo")

        value = st.number_input("Ingresa un número")

        if st.button("Predecir"):

            prediction = model.predict([[value]])[0]

            st.write("Resultado:", prediction)

            cursor.execute(
                """
                INSERT INTO predictions
                (email,input_value,prediction)
                VALUES (?,?,?)
                """,
                (st.session_state["user"],value,prediction)
            )

            conn.commit()

            st.success("Predicción guardada")
