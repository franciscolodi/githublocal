# C:\PythonP\GITHUB\app_usuarios.py
import sqlite3
import os
from datetime import datetime
import getpass  # Para contraseñas (en terminal)

class GestorUsuarios:
    def __init__(self, db_name="database.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.conectar()
        self.crear_tabla()
    
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"✅ Conectado a {self.db_name}")
        except sqlite3.Error as e:
            print(f"❌ Error de conexión: {e}")
    
    def crear_tabla(self):
        """Crea la tabla users si no existe"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    edad INTEGER,
                    ciudad TEXT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            self.conn.commit()
            print("✅ Tabla 'users' verificada/creada")
        except sqlite3.Error as e:
            print(f"❌ Error creando tabla: {e}")
    
    def agregar_usuario(self, nombre, email, edad=None, ciudad=None):
        """Agrega un nuevo usuario"""
        try:
            self.cursor.execute('''
                INSERT INTO users (nombre, email, edad, ciudad)
                VALUES (?, ?, ?, ?)
            ''', (nombre, email, edad, ciudad))
            self.conn.commit()
            print(f"✅ Usuario '{nombre}' agregado correctamente")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ El email '{email}' ya existe")
            return False
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
            return False
    
    def listar_usuarios(self, solo_activos=True):
        """Lista todos los usuarios"""
        try:
            if solo_activos:
                query = "SELECT * FROM users WHERE activo = 1 ORDER BY id"
            else:
                query = "SELECT * FROM users ORDER BY id"
            
            self.cursor.execute(query)
            usuarios = self.cursor.fetchall()
            
            if not usuarios:
                print("📭 No hay usuarios registrados")
                return
            
            print("\n" + "="*80)
            print(f"{'ID':<4} {'NOMBRE':<20} {'EMAIL':<25} {'EDAD':<6} {'CIUDAD':<15} {'FECHA REGISTRO':<20}")
            print("="*80)
            
            for user in usuarios:
                fecha = user[5][:10] if user[5] else "N/A"
                print(f"{user[0]:<4} {user[1]:<20} {user[2]:<25} {str(user[3] or ''):<6} {user[4] or '':<15} {fecha:<20}")
            print("="*80)
            print(f"Total: {len(usuarios)} usuarios")
            
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
    
    def buscar_usuario(self, criterio, valor):
        """Busca usuarios por diferentes criterios"""
        try:
            campos = {
                'id': 'id = ?',
                'nombre': 'nombre LIKE ?',
                'email': 'email LIKE ?',
                'ciudad': 'ciudad LIKE ?'
            }
            
            if criterio not in campos:
                print("❌ Criterio no válido")
                return
            
            query = f"SELECT * FROM users WHERE {campos[criterio]} AND activo = 1"
            
            if criterio == 'id':
                param = valor
            else:
                param = f'%{valor}%'
            
            self.cursor.execute(query, (param,))
            resultados = self.cursor.fetchall()
            
            if resultados:
                print(f"\n🔍 Resultados para {criterio} = '{valor}':")
                for user in resultados:
                    print(f"  ID: {user[0]}, Nombre: {user[1]}, Email: {user[2]}")
            else:
                print(f"📭 No se encontraron usuarios con {criterio} = '{valor}'")
                
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
    
    def actualizar_usuario(self, user_id, campo, valor):
        """Actualiza un campo específico de un usuario"""
        campos_permitidos = ['nombre', 'email', 'edad', 'ciudad']
        
        if campo not in campos_permitidos:
            print(f"❌ Campo no permitido. Usa: {campos_permitidos}")
            return False
        
        try:
            query = f"UPDATE users SET {campo} = ? WHERE id = ?"
            self.cursor.execute(query, (valor, user_id))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✅ Usuario ID {user_id} actualizado: {campo} = {valor}")
                return True
            else:
                print(f"❌ No se encontró usuario con ID {user_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
            return False
    
    def eliminar_usuario(self, user_id, permanente=False):
        """Elimina o desactiva un usuario"""
        try:
            if permanente:
                # Eliminación física
                self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                mensaje = f"🗑️ Usuario ID {user_id} eliminado permanentemente"
            else:
                # Eliminación lógica (desactivar)
                self.cursor.execute("UPDATE users SET activo = 0 WHERE id = ?", (user_id,))
                mensaje = f"⏸️ Usuario ID {user_id} desactivado"
            
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✅ {mensaje}")
                return True
            else:
                print(f"❌ No se encontró usuario con ID {user_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
            return False
    
    def estadisticas(self):
        """Muestra estadísticas de los usuarios"""
        try:
            # Total usuarios
            self.cursor.execute("SELECT COUNT(*) FROM users")
            total = self.cursor.fetchone()[0]
            
            # Usuarios activos
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
            activos = self.cursor.fetchone()[0]
            
            # Edad promedio
            self.cursor.execute("SELECT AVG(edad) FROM users WHERE edad IS NOT NULL")
            edad_prom = self.cursor.fetchone()[0]
            
            # Usuarios por ciudad
            self.cursor.execute('''
                SELECT ciudad, COUNT(*) as count 
                FROM users 
                WHERE ciudad IS NOT NULL 
                GROUP BY ciudad 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            ciudades = self.cursor.fetchall()
            
            print("\n" + "="*40)
            print("📊 ESTADÍSTICAS DE USUARIOS")
            print("="*40)
            print(f"Total usuarios: {total}")
            print(f"Usuarios activos: {activos}")
            print(f"Usuarios inactivos: {total - activos}")
            if edad_prom:
                print(f"Edad promedio: {edad_prom:.1f} años")
            
            if ciudades:
                print("\n🏙️ Top 5 ciudades:")
                for ciudad, count in ciudades:
                    print(f"  {ciudad}: {count} usuario(s)")
            print("="*40)
            
        except sqlite3.Error as e:
            print(f"❌ Error: {e}")
    
    def exportar_csv(self, filename="usuarios_export.csv"):
        """Exporta usuarios a archivo CSV"""
        try:
            import csv
            
            self.cursor.execute("SELECT * FROM users")
            usuarios = self.cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Escribir encabezados
                writer.writerow(['ID', 'Nombre', 'Email', 'Edad', 'Ciudad', 'Fecha Registro', 'Activo'])
                # Escribir datos
                writer.writerows(usuarios)
            
            print(f"✅ Datos exportados a {filename}")
            
        except Exception as e:
            print(f"❌ Error exportando: {e}")
    
    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            print("🔒 Conexión cerrada")

def menu_principal():
    """Interfaz de menú para el usuario"""
    gestor = GestorUsuarios()
    
    while True:
        print("\n" + "="*50)
        print("📱 SISTEMA DE GESTIÓN DE USUARIOS")
        print("="*50)
        print("1. ➕ Agregar usuario")
        print("2. 📋 Listar usuarios")
        print("3. 🔍 Buscar usuario")
        print("4. ✏️ Actualizar usuario")
        print("5. 🗑️ Eliminar/Desactivar usuario")
        print("6. 📊 Ver estadísticas")
        print("7. 📤 Exportar a CSV")
        print("8. ❌ Salir")
        print("="*50)
        
        opcion = input("Selecciona una opción (1-8): ").strip()
        
        if opcion == '1':
            print("\n--- NUEVO USUARIO ---")
            nombre = input("Nombre: ").strip()
            email = input("Email: ").strip()
            
            edad = input("Edad (opcional): ").strip()
            edad = int(edad) if edad.isdigit() else None
            
            ciudad = input("Ciudad (opcional): ").strip() or None
            
            gestor.agregar_usuario(nombre, email, edad, ciudad)
        
        elif opcion == '2':
            print("\n--- LISTA DE USUARIOS ---")
            ver_inactivos = input("¿Ver también inactivos? (s/n): ").lower() == 's'
            gestor.listar_usuarios(solo_activos=not ver_inactivos)
        
        elif opcion == '3':
            print("\n--- BUSCAR USUARIO ---")
            print("Criterios: id, nombre, email, ciudad")
            criterio = input("Criterio: ").strip().lower()
            valor = input("Valor a buscar: ").strip()
            gestor.buscar_usuario(criterio, valor)
        
        elif opcion == '4':
            print("\n--- ACTUALIZAR USUARIO ---")
            try:
                user_id = int(input("ID del usuario: "))
                print("Campos: nombre, email, edad, ciudad")
                campo = input("Campo a actualizar: ").strip().lower()
                valor = input("Nuevo valor: ").strip()
                gestor.actualizar_usuario(user_id, campo, valor)
            except ValueError:
                print("❌ ID inválido")
        
        elif opcion == '5':
            print("\n--- ELIMINAR/DESACTIVAR USUARIO ---")
            try:
                user_id = int(input("ID del usuario: "))
                print("1. Desactivar (mantener datos)")
                print("2. Eliminar permanentemente")
                sub_opcion = input("Selecciona (1-2): ").strip()
                
                if sub_opcion == '1':
                    gestor.eliminar_usuario(user_id, permanente=False)
                elif sub_opcion == '2':
                    confirm = input("⚠️ ¿Estás seguro? (escribe 'SI' para confirmar): ")
                    if confirm == 'SI':
                        gestor.eliminar_usuario(user_id, permanente=True)
                    else:
                        print("Operación cancelada")
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ ID inválido")
        
        elif opcion == '6':
            gestor.estadisticas()
        
        elif opcion == '7':
            filename = input("Nombre del archivo (default: usuarios_export.csv): ").strip()
            if not filename:
                filename = "usuarios_export.csv"
            gestor.exportar_csv(filename)
        
        elif opcion == '8':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")
    
    gestor.cerrar()

if __name__ == "__main__":
    # Cambiar al directorio si es necesario
    if os.path.exists(r"C:\PythonP\GITHUB"):
        os.chdir(r"C:\PythonP\GITHUB")
    
    menu_principal()
