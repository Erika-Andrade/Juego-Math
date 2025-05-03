import sqlite3
from tkinter import messagebox

class Auth:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexión Auth cerrada")

    def registrar_usuario(self, usuario, contrasenia):
        if len(usuario) < 4 or len(contrasenia) < 6:
            messagebox.showerror("Error", "Usuario mínimo 4 caracteres\nContraseña mínimo 6 caracteres")
            return False
            
        try:
            self.cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?)",
                                (usuario, contrasenia, 1))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El usuario ya existe")
            return False

    def verificar_credenciales(self, usuario, contrasenia):
        self.cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        usuario_db = self.cursor.fetchone()
        
        if not usuario_db:
            messagebox.showerror("Error", "Usuario no encontrado")
            return False
            
        if usuario_db[1] != contrasenia:
            messagebox.showerror("Error", "Contraseña incorrecta")
            return False
            
        return True

    def obtener_nivel_usuario(self, usuario):
        self.cursor.execute("SELECT nivel_actual FROM usuarios WHERE usuario = ?", (usuario,))
        return self.cursor.fetchone()[0]

    def actualizar_nivel(self, usuario, nuevo_nivel):
        self.cursor.execute("UPDATE usuarios SET nivel_actual = ? WHERE usuario = ?",
                            (nuevo_nivel, usuario))
        self.conn.commit()