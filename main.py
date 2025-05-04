# Importar librerías, funciones...
import tkinter as tk
from tkinter import ttk, messagebox
from auth import Auth
from game import Juego
from functools import partial
import random
import time  # ← Necesario para el cronómetro

# COLORES
COLOR_FONDO = "#F8F9FA"
COLOR_PRIMARIO = "#6C63FF"
COLOR_BOTON_ACTIVO = "#4CAF50"
COLOR_BOTON_BLOQUEADO = "#E0E0E0"
COLOR_TEXTO_BOTON = "#FFFFFF"  # Blanco
COLOR_BOTON_INCORRECTO = "#FF6B6B"  # Rojo claro

# SIDEBAR
class Sidebar(tk.Frame):
    def __init__(self, parent, usuario, app):
        super().__init__(parent, bg=COLOR_PRIMARIO)
        self.parent = parent
        self.usuario = usuario
        self.auth = Auth()
        self.app = app

        # Cargar datos del usuario
        self.nivel_actual = self.auth.obtener_nivel_usuario(usuario)

        # Etiqueta bienvenidos
        tk.Label(self, text=f"¡Hola {usuario}!", font=("Arial", 14), bg=COLOR_PRIMARIO).pack(pady=15)
        # Separador horizontal
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=20, pady=5)
        # Etiqueta nivel actual
        tk.Label(self, text=f"Nivel Actual: {self.nivel_actual}", font=("Arial", 12), bg=COLOR_PRIMARIO).pack(pady=5)

        self.progress = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate", value=(self.nivel_actual / 10) * 100
        )
        self.progress.pack(pady=10)

        ttk.Button(self, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side='bottom', pady=20)

    # Método para actualizar barra lateral
    def actualizar(self):
        self.nivel_actual = self.auth.obtener_nivel_usuario(self.usuario)
        self.progress['value'] = (self.nivel_actual / 10) * 100
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and "Nivel Actual" in widget.cget("text"):
                widget.config(text=f"Nivel Actual: {self.nivel_actual}")

    # Método para cerrar sesión y volver al login
    def cerrar_sesion(self):
        self.auth.close()
        self.app.mostrar_login()


class ContenidoJuego(tk.Frame):
    def __init__(self, parent, usuario, app):
        super().__init__(parent, bg=COLOR_FONDO)
        self.tiempo_transcurrido = 0  # Segundos transcurridos
        self.cronometro_id = None  # ID del contador (para cancelarlo)
        self.tiempo_inicio = None  # Momento de inicio
        self.parent = parent
        self.usuario = usuario
        self.app = app
        self.auth = Auth()  # Manejador de autenticación y progreso del usuario
        self.juego = Juego(usuario)
        self.nivel_actual = self.auth.obtener_nivel_usuario(usuario)
        self.preguntas_nivel = []
        self.indice_pregunta = 0
        self.widgets = {}
        self.vidas = 3
        # Variables para el cronómetro
        self.tiempo_transcurrido = 0  # Segundos transcurridos
        self.cronometro_id = None  # ID del contador (para cancelarlo)
        self.tiempo_inicio = None  # Momento de inicio
        # UI
        self.crear_interfaz()

    # Crea los elementos gráficos principales de la pantalla del juego.
    def crear_interfaz(self):
        # Barra superior con ayuda
        self.frame_superior = tk.Frame(self, bg=COLOR_PRIMARIO, height=60)
        self.frame_superior.pack(fill='x', pady=10)

        # Etiqueta del cronómetro
        self.widgets['lbl_tiempo'] = tk.Label(
            self.frame_superior,
            text="Tiempo: 00:00",
            bg=COLOR_PRIMARIO,
            fg="white",
            font=('Arial', 14)
        )
        self.widgets['lbl_tiempo'].pack(side='right', padx=20)

        self.widgets['btn_ayuda'] = tk.Button(
            self.frame_superior,
            text="💡 Ayuda",
            bg=COLOR_PRIMARIO,
            fg="white",
            command=self.mostrar_ayuda
        )
        self.widgets['btn_ayuda'].pack(side='left', padx=20)

        # Botón de menú en la barra superior
        self.widgets['btn_menu'] = tk.Button(
            self.frame_superior,
            text="🏠 Menú",
            bg=COLOR_PRIMARIO,
            fg="white",
            command=self.volver_menu
        )
        self.widgets['btn_menu'].pack(side='right', padx=20)
        # Barra de progreso
        self.widgets['lbl_progreso'] = tk.Label(
            self.frame_superior,
            text="",
            bg=COLOR_PRIMARIO,
            fg="white",
            font=('Arial', 14)
        )
        self.widgets['lbl_progreso'].pack(side='right', padx=20)

        self.widgets['lbl_vidas'] = tk.Label(
            self.frame_superior,
            text=f"Vidas: {self.vidas}",
            bg=COLOR_PRIMARIO,
            fg="white",
            font=('Arial', 14)
        )
        self.widgets['lbl_vidas'].pack(side='right', padx=20)

        # Contenedor principal
        self.contenedor = tk.Frame(self, bg=COLOR_FONDO)
        self.contenedor.pack(padx=20, pady=20, fill='both', expand=True)

        # Botones de niveles
        self.crear_niveles()

    def crear_niveles(self):
    # Muestra los botones de selección de nivel.
        self.frame_superior.pack_forget()
        for widget in self.contenedor.winfo_children():
            widget.destroy()  # Elimina los elementos previos de la pantalla

        # Crea los botones de nivel
        for nivel in range(1, 11):
            estado = 'activo' if nivel <= self.nivel_actual else 'bloqueado'
            color = COLOR_BOTON_ACTIVO if estado == 'activo' else COLOR_BOTON_BLOQUEADO

            if estado == 'activo':
                comando = lambda n=nivel: self.iniciar_nivel(n)
                texto = str(nivel)
            else:
                comando = lambda: messagebox.showinfo(
                    "Nivel bloqueado",
                    f"Debes completar el nivel {self.nivel_actual} para desbloquear este."
                )
                texto = "🔒"

            btn = tk.Button(
                self.contenedor,
                text=texto,
                bg=color,
                fg=COLOR_TEXTO_BOTON,
                font=('Arial', 16),
                width=8,
                height=2,
                command=comando
            )

            row = (nivel - 1) // 5
            col = (nivel - 1) % 5
            btn.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

    def iniciar_nivel(self, nivel):
        # Detener cualquier cronómetro previo
        self.detener_cronometro()  # Asegúrate de que no haya cronómetros corriendo

        # Reiniciar el tiempo y las vidas
        self.tiempo_transcurrido = 0  # Reiniciar el contador de tiempo
        self.widgets['lbl_tiempo'].config(text="Tiempo: 00:00")  # Resetear visualización
        self.vidas = 3
        self.widgets['lbl_vidas'].config(text=f"Vidas: {self.vidas}")

        # Configuración del nivel seleccionado
        self.nivel_actual_jugando = nivel
        self.preguntas_nivel = self.obtener_preguntas_nivel(nivel)  # Carga preguntas del nivel
        if len(self.preguntas_nivel) < 5:
            messagebox.showwarning("Atención", "Este nivel no tiene suficientes preguntas")
            return

        self.indice_pregunta = 0  # Se inicia desde la primera pregunta

        # Iniciar el cronómetro
        self.iniciar_cronometro()  # Llamada para iniciar el cronómetro

        # Mostrar la primera pregunta
        self.mostrar_pregunta()

    def iniciar_cronometro(self):
        """Inicia el contador de tiempo."""
        self.tiempo_inicio = time.time()  # Guarda el momento de inicio
        self.actualizar_cronometro()  # Comienza a actualizar

    def actualizar_cronometro(self):
        """Actualiza el cronómetro cada segundo."""
        self.tiempo_transcurrido = int(time.time() - self.tiempo_inicio)  # Calcula segundos
        minutos = self.tiempo_transcurrido // 60
        segundos = self.tiempo_transcurrido % 60
        self.widgets['lbl_tiempo'].config(text=f"Tiempo: {minutos:02d}:{segundos:02d}")
        self.cronometro_id = self.after(1000, self.actualizar_cronometro)  # Programa la próxima actualización

    def detener_cronometro(self):
        """Detiene el contador."""
        if self.cronometro_id:
            self.after_cancel(self.cronometro_id)  # Cancela la actualización programada
            self.cronometro_id = None

    def obtener_preguntas_nivel(self, nivel):
        self.juego.cursor.execute("SELECT * FROM preguntas WHERE nivel = ?", (nivel,))
        return self.juego.cursor.fetchall()

    def mostrar_pregunta(self):
        # Reiniciar contador de intentos para la nueva pregunta
        self.intentos_pregunta = 0
        
        # Limpiar contenedor
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.frame_superior.pack()
            
        # Obtener pregunta actual
        pregunta_actual = self.preguntas_nivel[self.indice_pregunta]
        self.pregunta_actual_id = pregunta_actual[0]
        
        # Obtener opciones y respuesta correcta ORIGINAL
        opciones_originales = [pregunta_actual[2], pregunta_actual[3], pregunta_actual[4]]
        self.respuesta_correcta_texto = opciones_originales[pregunta_actual[5]-1]  # Guardar texto correcto

        # Mezclar opciones
        opciones = list(opciones_originales)
        random.shuffle(opciones)
        
        # Encontrar NUEVO índice de la respuesta correcta
        self.respuesta_correcta_indice = opciones.index(self.respuesta_correcta_texto) + 1  

        # Mostrar progreso
        self.widgets['lbl_progreso'].config(text=f"Pregunta {self.indice_pregunta+1}/5")
        
        # Mostrar pregunta
        frame_pregunta = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_pregunta.pack(pady=20, fill='x')

        tk.Label(frame_pregunta, text=pregunta_actual[1], 
            font=('Arial', 16), bg=COLOR_FONDO,
            wraplength=600).pack(pady=10)
    
        # Botones de respuesta mezclados
        frame_respuestas = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_respuestas.pack(pady=10)

        for idx, texto_respuesta in enumerate(opciones):
            btn = tk.Button(frame_respuestas, text=texto_respuesta,
                    bg=COLOR_BOTON_ACTIVO, fg=COLOR_TEXTO_BOTON,
                    font=('Arial', 14), width=30, height=2,
                    command=partial(self.verificar_respuesta, idx+1 == self.respuesta_correcta_indice))
            btn.pack(pady=5, padx=20, fill='x')
        
        # Label para mensajes de ayuda/feedback
        self.lbl_feedback = tk.Label(self.contenedor, text="", 
                                font=('Arial', 12), bg=COLOR_FONDO, fg=COLOR_PRIMARIO)
        self.lbl_feedback.pack(pady=10)
        
        # Botón de control (se configurará en verificar_respuesta)
        self.btn_control = tk.Button(self.contenedor, text="Siguiente Pregunta",
                                bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                                command=self.siguiente_pregunta)
        self.btn_control.pack_forget()  # Ocultar inicialmente

    def verificar_respuesta(self, es_correcta):
        # Desactivar todos los botones de respuesta
        for btn in self.contenedor.winfo_children()[1].winfo_children():
            btn.config(state='disabled')
        
        # Incrementar contador de intentos
        self.intentos_pregunta += 1
        
        # Asegurarnos que el label de feedback existe
        if not hasattr(self, 'lbl_feedback') or not self.lbl_feedback.winfo_exists():
            self.lbl_feedback = tk.Label(self.contenedor, text="", 
                                    font=('Arial', 14), bg=COLOR_FONDO)
            self.lbl_feedback.pack(pady=10)
        
        if es_correcta:
            # Respuesta correcta - Mostrar feedback en pantalla
            mensajes_positivos = [
                "¡Respuesta correcta!",
                "¡Bien hecho!",
                "¡Excelente!",
                "¡Eres increíble!",
                "¡Perfecto!",
                "¡Lo tienes dominado!",
                "¡Así se hace!"
            ]
            mensaje = random.choice(mensajes_positivos)
            self.lbl_feedback.config(text=mensaje, fg="green")
            
            # Resaltar la respuesta correcta
            frame_respuestas = self.contenedor.winfo_children()[1]
            for i, btn in enumerate(frame_respuestas.winfo_children()):
                if i+1 == self.respuesta_correcta_indice:
                    btn.config(bg="#4CAF50", fg="white")  # Verde intenso
            
            self.indice_pregunta += 1
            self.btn_control.config(text="Siguiente Pregunta", command=self.siguiente_pregunta)
            self.btn_control.pack(pady=20)
        else:
            # Respuesta incorrecta
            self.vidas -= 1
            self.widgets['lbl_vidas'].config(text=f"Vidas: {self.vidas}")
            
            if self.vidas <= 0:
                self.mostrar_game_over()
                return
                
            if self.intentos_pregunta == 1:
                # Primer error - Mostrar ayuda en messagebox
                ayuda = self.preguntas_nivel[self.indice_pregunta][7]
                messagebox.showinfo("Ayuda", ayuda)
                
                # Configurar botón de reintento
                self.btn_control.config(text="Repetir Pregunta", 
                                    command=self.repetir_pregunta)
                self.btn_control.pack(pady=20)
                
                # Mostrar feedback en pantalla
                self.lbl_feedback.config(text="Inténtalo de nuevo", fg="orange")
            else:
                # Segundo error - Mostrar respuesta correcta
                messagebox.showinfo("Respuesta Correcta", 
                                f"La respuesta correcta era:\n\n{self.respuesta_correcta_texto}")
                
                frame_respuestas = self.contenedor.winfo_children()[1]
                for i, btn in enumerate(frame_respuestas.winfo_children()):
                    # Primero restablecemos todos los botones a su color original
                    btn.config(bg=COLOR_BOTON_ACTIVO, fg=COLOR_TEXTO_BOTON)
                    
                    # Luego aplicamos los colores especiales
                    if i+1 == self.respuesta_correcta_indice:
                        btn.config(bg="#4CAF50", fg="white")  # Verde para la correcta
                    elif btn['state'] == 'disabled' and btn['text'] != self.respuesta_correcta_texto:
                        # Solo colorear rojo el botón que el usuario seleccionó (que está deshabilitado)
                        btn.config(bg="#F44336", fg="white")
                self.indice_pregunta += 1
                self.btn_control.config(text="Siguiente Pregunta", 
                                    command=self.siguiente_pregunta)
                self.btn_control.pack(pady=20)
                self.lbl_feedback.config(text="Sigue intentándolo", fg="red")

    def repetir_pregunta(self):
        """Muestra la misma pregunta nuevamente pero sin mezclar las opciones"""
        # Mantenemos el mismo índice de pregunta
        # Solo necesitamos volver a mostrar la interfaz
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        
        pregunta_actual = self.preguntas_nivel[self.indice_pregunta]
        
        # Mostrar pregunta (sin mezclar opciones esta vez)
        frame_pregunta = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_pregunta.pack(pady=20, fill='x')

        tk.Label(frame_pregunta, text=pregunta_actual[1], 
                font=('Arial', 16), bg=COLOR_FONDO,
                wraplength=600).pack(pady=10)
        
        # Mostrar opciones en ORDEN ORIGINAL
        opciones = [pregunta_actual[2], pregunta_actual[3], pregunta_actual[4]]
        frame_respuestas = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_respuestas.pack(pady=10)

        for idx, texto_respuesta in enumerate(opciones):
            btn = tk.Button(frame_respuestas, text=texto_respuesta,
                        bg=COLOR_BOTON_ACTIVO, fg=COLOR_TEXTO_BOTON,
                        font=('Arial', 14), width=30, height=2,
                        command=partial(self.verificar_respuesta, 
                                        idx+1 == pregunta_actual[5]))  # Usar índice original
            btn.pack(pady=5, padx=20, fill='x')
        
        # Configurar botón de control
        self.btn_control = tk.Button(self.contenedor, text="Siguiente Pregunta",
                                bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                                command=self.siguiente_pregunta)
        self.btn_control.pack_forget()
    def mostrar_game_over(self):
        #Muestra la pantalla de Game Over.
        # Limpiar contenedor
        for widget in self.contenedor.winfo_children():
            widget.destroy()
            
        # Pantalla de Game Over
        tk.Label(self.contenedor, text="¡Has perdido!", 
                font=('Arial', 24), bg=COLOR_FONDO).pack(pady=20)
        tk.Label(self.contenedor, text="Te has equivocado 3 veces",
                font=('Arial', 16), bg=COLOR_FONDO).pack(pady=10)
                
        # Botones
        frame_botones = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_botones.pack(pady=20)
        tk.Button(frame_botones, text="Reiniciar Nivel", 
                 bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                 command=self.reiniciar_nivel).pack(side='left', padx=10)
        tk.Button(frame_botones, text="Volver al Menú", 
                 bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                 command=self.volver_menu).pack(side='right', padx=10)
        self.widgets['lbl_vidas'].config(text=f"Vidas: {self.vidas}")
    
    def reiniciar_nivel(self):
        #Reinicia el nivel actual
        self.detener_cronometro()  # ← Agregar esto al inicio
        self.tiempo_transcurrido = 0  # ← Reiniciar contador
        self.widgets['lbl_tiempo'].config(text="Tiempo: 00:00")  # ← Resetear visualización
        self.vidas = 3  # Resetear vidas
        self.widgets['lbl_vidas'].config(text=f"Vidas: {self.vidas}") 
        self.indice_pregunta = 0
        self.mostrar_pregunta()
    
    def volver_menu(self):
        #Regresa al menú de selección de niveles.
        self.detener_cronometro()
        self.vidas = 3  # Resetear vidas
        self.widgets['lbl_vidas'].config(text=f"Vidas: {self.vidas}")
        self.frame_superior.pack_forget()
        self.crear_niveles()

    def siguiente_pregunta(self):
        self.mostrar_pregunta()

    def finalizar_nivel(self):
        # Verificar si desbloquear siguiente nivel
        if self.nivel_actual_jugando == self.nivel_actual and self.nivel_actual < 10:
            self.auth.actualizar_nivel(self.usuario, self.nivel_actual + 1)
            self.nivel_actual += 1
            self.app.sidebar.actualizar()
        self.mostrar_pantalla_completado()

    def mostrar_pantalla_completado(self):
        # Ocultar elementos de juego
        self.frame_superior.pack_forget()  # Ocultar barra superior
        self.contenedor.destroy()  # Eliminar contenedor antiguo
        
        # Crear nuevo contenedor para la pantalla de finalización
        self.contenedor = tk.Frame(self, bg=COLOR_FONDO)
        self.contenedor.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Mensaje de finalización
        tk.Label(self.contenedor, text=f"¡Nivel {self.nivel_actual_jugando} Completado!",
                font=('Arial', 24), bg=COLOR_FONDO).pack(pady=40)
        
        # Botones de acción
        frame_botones = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        frame_botones.pack(pady=20)
        
        if self.nivel_actual_jugando < 10:
            tk.Button(frame_botones, text="Siguiente Nivel →",
                     bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                     font=('Arial', 14),
                     command=lambda: self.iniciar_nivel(self.nivel_actual_jugando + 1)
                     ).pack(side='left', padx=15)
                     
        tk.Button(frame_botones, text="← Volver al Menú",
                 bg=COLOR_PRIMARIO, fg=COLOR_TEXTO_BOTON,
                 font=('Arial', 14),
                 command=self.volver_menu
                 ).pack(side='right', padx=15)

    def mostrar_ayuda(self):
        if self.preguntas_nivel:
            pregunta_actual = self.preguntas_nivel[self.indice_pregunta]
            messagebox.showinfo("Ayuda", pregunta_actual[7])
class App:
     # Configuración de la ventana principal
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aventura Educativa")
        self.root.geometry("900x600")
        self.root.configure(bg=COLOR_FONDO)
        self.centrar_ventana() 
        self.root.resizable(True, True)  # Permitir redimensionar
        self.root.bind("<Configure>", self.actualizar_diseño)
        self.centrar_ventana()  
        self.root.resizable(True, True) 
        self.root.bind("<Configure>", self.actualizar_diseño)  # Para responsive

        #Manejo de autenticación
        self.auth = Auth()
        self.usuario_actual = None
         # Mostrar pantalla de inicio de sesión
        self.centrar_ventana()
        self.mostrar_login()
        
 # Centra la ventana en la pantalla
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"+{x}+{y}")

    def actualizar_diseño(self, event=None):
         # Ajusta el diseño para que sea responsive
        if not hasattr(self, 'contenido'):
            return  
        if not self.contenido.winfo_exists():
            return  # Verifica si el contenedor aún existe
        for widget in self.contenido.contenedor.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(wraplength=self.contenido.contenedor.winfo_width()-40)



    def mostrar_login(self):
         # Muestra la interfaz de inicio de sesión
        self.limpiar_ventana()
        
        # Frame principal con padding
        login_frame = ttk.Frame(self.root, padding="30")
        login_frame.pack(fill='both', expand=True)
        
        # Crear un frame interno para centrar contenido
        content_frame = ttk.Frame(login_frame)
        content_frame.pack(pady=20)  # Añade espacio vertical
        
        # Configurar columnas para centrado
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(2, weight=1)
        
        # Elementos del formulario
        ttk.Label(content_frame, text="Iniciar Sesión", font=('Arial', 16, 'bold')).grid(row=0, column=1, pady=20)
        
        ttk.Label(content_frame, text="Usuario:").grid(row=1, column=1, sticky='e', padx=10)
        self.entry_user = ttk.Entry(content_frame, width=25)
        self.entry_user.grid(row=1, column=2, pady=5, padx=10)
        
        ttk.Label(content_frame, text="Contraseña:").grid(row=2, column=1, sticky='e', padx=10)
        self.entry_pass = ttk.Entry(content_frame, show="*", width=25)
        self.entry_pass.grid(row=2, column=2, pady=5, padx=10)
        
        self.btn_login = ttk.Button(content_frame, text="Iniciar Sesión", command=self.login)
        self.btn_login.grid(row=3, column=1, columnspan=2, pady=20)
        
        self.btn_registro = ttk.Button(content_frame, text="Registrarse", command=self.mostrar_registro)
        self.btn_registro.grid(row=4, column=1, columnspan=2)

    def mostrar_registro(self):
         # Muestra la interfaz de registro de usuario
        self.limpiar_ventana()
        
        registro_frame = ttk.Frame(self.root, padding="30")
        registro_frame.pack(fill='both', expand=True)
        
        ttk.Label(registro_frame, text="Registro", font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(registro_frame, text="Nuevo Usuario:").grid(row=1, column=0, pady=5, sticky='e')
        self.entry_new_user = ttk.Entry(registro_frame, width=25)
        self.entry_new_user.grid(row=1, column=1, pady=5)
        
        ttk.Label(registro_frame, text="Nueva Contraseña:").grid(row=2, column=0, pady=5, sticky='e')
        self.entry_new_pass = ttk.Entry(registro_frame, show="*", width=25)
        self.entry_new_pass.grid(row=2, column=1, pady=5)
        
        ttk.Button(registro_frame, text="Crear Cuenta", command=self.registrar).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(registro_frame, text="Volver", command=self.mostrar_login).grid(row=4, column=0, columnspan=2)

    def limpiar_ventana(self):
        # Elimina todos los widgets de la ventana para actualizar la interfaz
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
         # Manejo de inicio de sesión
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not user or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        if self.auth.verificar_credenciales(user, password):
            self.usuario_actual = user
            self.iniciar_juego()

    def registrar(self):
         # Manejo de registro de usuarios
        new_user = self.entry_new_user.get().strip()
        new_pass = self.entry_new_pass.get().strip()
        
        if not new_user or not new_pass:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        if self.auth.registrar_usuario(new_user, new_pass):
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            self.mostrar_login()
        

    def iniciar_juego(self):
        # Inicia el juego y muestra la interfaz de usuario
        self.limpiar_ventana()
        
        contenedor = tk.Frame(self.root)
        contenedor.pack(fill=tk.BOTH, expand=True)
        contenedor.grid_columnconfigure(0, weight=1)
        
        # Pasamos 'self' (la instancia de App) al ContenidoJuego
        self.sidebar = Sidebar(contenedor, self.usuario_actual, self)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        
        self.contenido = ContenidoJuego(contenedor, self.usuario_actual, self)  # ← Nuevo parámetro
        self.contenido.grid(row=0, column=1, sticky="nsew")
        
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)

    def iniciar_cronometro(self):
        """Inicia el contador de tiempo."""
        self.tiempo_inicio = time.time()  # Guarda el momento de inicio
        self.actualizar_cronometro()      # Comienza a actualizar

    def actualizar_cronometro(self):
        """Actualiza el cronómetro cada segundo."""
        self.tiempo_transcurrido = int(time.time() - self.tiempo_inicio)  # Calcula segundos
        minutos = self.tiempo_transcurrido // 60
        segundos = self.tiempo_transcurrido % 60
        self.widgets['lbl_tiempo'].config(text=f"Tiempo: {minutos:02d}:{segundos:02d}")
        self.cronometro_id = self.after(1000, self.actualizar_cronometro)  # Programa la próxima actualización

    def detener_cronometro(self):
        """Detiene el contador."""
        if self.cronometro_id:
            self.after_cancel(self.cronometro_id)  # Cancela la actualización programada
            self.cronometro_id = None

if __name__ == "__main__":
    app = App()
    app.root.mainloop()


