import sqlite3

def crear_tablas():
    """
    Crea las tablas en la base de datos si no existen.
    """
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Crear la tabla 'niveles'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS niveles (
            id_nivel INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_nivel TEXT NOT NULL
        )
        ''')
        
        # Crear la tabla 'usuarios'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            contrasenia TEXT NOT NULL,
            nivel_actual INTEGER DEFAULT 1,
            FOREIGN KEY (nivel_actual) REFERENCES niveles(id_nivel)
        )
        ''')
        
        # Crear la tabla 'preguntas'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preguntas (
            id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT NOT NULL,
            respuesta1 TEXT NOT NULL,
            respuesta2 TEXT NOT NULL,
            respuesta3 TEXT NOT NULL,
            respuesta_correcta INTEGER NOT NULL,
            nivel INTEGER,
            ayuda TEXT,
            FOREIGN KEY (nivel) REFERENCES niveles(id_nivel)
        )
        ''')
        
        conn.commit()

def insertar_niveles():
    """
    Inserta datos iniciales en la tabla 'niveles'.
    """
    niveles = [
        ("Nivel 1",),  # id_nivel = 1
        ("Nivel 2",),  # id_nivel = 2
        ("Nivel 3",)   # id_nivel = 3
    ]
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO niveles (nombre_nivel) VALUES (?)', niveles)
        conn.commit()

def insertar_preguntas():
    """
    Inserta datos iniciales en la tabla 'preguntas'.
    """
    preguntas = [
        # Preguntas para el Nivel 1
        ("¿Cuánto es 2 + 2?", "3", "4", "5", 2, 1, "Suma los números."),
        ("¿Cuánto es 3 * 3?", "6", "9", "12", 2, 1, "Multiplica los números."),
        ("¿Cuánto es 10 - 5?", "2", "5", "10", 2, 1, "Resta los números."),
        
        # Preguntas para el Nivel 2
        ("¿Cuánto es 15 / 3?", "3", "5", "10", 2, 2, "Divide los números."),
        ("¿Cuánto es 8 + 7?", "10", "15", "20", 2, 2, "Suma los números."),
        ("¿Cuánto es 4 * 5?", "15", "20", "25", 2, 2, "Multiplica los números."),
        
        # Preguntas para el Nivel 3
        ("¿Cuánto es 20 - 8?", "10", "12", "15", 2, 3, "Resta los números."),
        ("¿Cuánto es 9 * 3?", "18", "27", "36", 2, 3, "Multiplica los números."),
        ("¿Cuánto es 50 / 5?", "5", "10", "15", 2, 3, "Divide los números.")
    ]
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT INTO preguntas (pregunta, respuesta1, respuesta2, respuesta3, respuesta_correcta, nivel, ayuda)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', preguntas)
        conn.commit()

if __name__ == "__main__":
    # Crear las tablas y insertar datos iniciales
    crear_tablas()
    insertar_niveles()
    insertar_preguntas()
    print("Base de datos creada y datos iniciales insertados correctamente.")