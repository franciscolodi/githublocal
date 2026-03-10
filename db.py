from app_usuarios import GestorUsuarios

class DBManager:

    def __init__(self):
        self.gestor = GestorUsuarios()

    # -----------------------
    # CREAR USUARIO
    # -----------------------

    def crear_usuario(self, nombre, email, edad=None, ciudad=None):
        return self.gestor.agregar_usuario(nombre, email, edad, ciudad)

    # -----------------------
    # LISTAR USUARIOS
    # -----------------------

    def obtener_usuarios(self, solo_activos=True):

        if solo_activos:
            query = "SELECT * FROM users WHERE activo = 1"
        else:
            query = "SELECT * FROM users"

        self.gestor.cursor.execute(query)
        return self.gestor.cursor.fetchall()

    # -----------------------
    # BUSCAR USUARIO
    # -----------------------

    def buscar_usuario(self, criterio, valor):

        query = f"""
        SELECT * FROM users
        WHERE {criterio} LIKE ?
        AND activo = 1
        """

        self.gestor.cursor.execute(query, (f"%{valor}%",))
        return self.gestor.cursor.fetchall()

    # -----------------------
    # ELIMINAR USUARIO
    # -----------------------

    def desactivar_usuario(self, user_id):
        return self.gestor.eliminar_usuario(user_id, permanente=False)

    # -----------------------
    # ESTADÍSTICAS
    # -----------------------

    def estadisticas(self):

        c = self.gestor.cursor

        c.execute("SELECT COUNT(*) FROM users")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
        activos = c.fetchone()[0]

        c.execute("SELECT AVG(edad) FROM users WHERE edad IS NOT NULL")
        edad_prom = c.fetchone()[0]

        return {
            "total": total,
            "activos": activos,
            "edad_prom": edad_prom
        }

    # -----------------------

    def cerrar(self):
        self.gestor.cerrar()
