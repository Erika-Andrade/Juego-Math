import sqlite3
from random import choice

class Juego:
    def __init__(self, usuario):
        self.usuario = usuario
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.nivel_actual = self.obtener_nivel_actual()
    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexión Juego cerrada")  # Para depuración

    def obtener_nivel_actual(self):
        self.cursor.execute("SELECT nivel_actual FROM usuarios WHERE usuario = ?", (self.usuario,))
        return self.cursor.fetchone()[0]

    def obtener_pregunta_aleatoria(self, nivel):
        self.cursor.execute("SELECT * FROM preguntas WHERE nivel = ?", (nivel,))
        preguntas = self.cursor.fetchall()
        return choice(preguntas) if preguntas else None

    def verificar_respuesta(self, id_pregunta, respuesta_usuario):
        self.cursor.execute("SELECT respuesta_correcta FROM preguntas WHERE id_pregunta = ?",
                            (id_pregunta,))
        return respuesta_usuario == self.cursor.fetchone()[0]

    def obtener_ayuda(self, id_pregunta):
        self.cursor.execute("SELECT ayuda FROM preguntas WHERE id_pregunta = ?", (id_pregunta,))
        return self.cursor.fetchone()[0]