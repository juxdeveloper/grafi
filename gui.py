import tkinter as tk # GUI y sus elementos
from tkinter import messagebox # Para el mensaje de error de una entrada inválida
import matplotlib # Herramientas de grafiación
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import operations # operations.py --> Lógica de operaciones
import steps # steps.py --> Lógica de pasos
import re # Para parsear formatos y entradas, con regex

# Este es el módulo principal que controla la interfaz gráfica.
# Usamos tkinter para crear ventanas, botones y cuadros de texto.
# Hemos mejorado la interfaz para usar elementos nativos y solucionar problemas de layout.

# --- TEMAS DE COLOR ---
THEMES = {
    "dark": {
        "bg_window": "#1e1e1e",
        "bg_frame": "#2d2d2d",
        "fg_text": "#ffffff",
        "fg_title": "#bb86fc", # Morado claro
        "bg_entry": "#333333",
        "fg_entry": "#ffffff",
        "bg_button": "#bb86fc",
        "fg_button": "#000000",
        "bg_button_clear": "#cf6679",
        "fg_button_clear": "#000000",
        "graph_bg": "#1e1e1e",
        "graph_fg": "white",
        "graph_grid": "#444444",
        "math_color": "#ffffff",
        "btn_theme_bg": "#ffffff",
        "btn_theme_fg": "#000000",
        "btn_theme_text": "Modo: Oscuro"
    },
    "light": {
        "bg_window": "#f5f5f5",
        "bg_frame": "#ffffff",
        "fg_text": "#333333",
        "fg_title": "#4B0082", # Modo oscuro
        "bg_entry": "#ffffff",
        "fg_entry": "#000000",
        "bg_button": "#2196F3",
        "fg_button": "white",
        "bg_button_clear": "#F44336",
        "fg_button_clear": "white",
        "graph_bg": "#ffffff",
        "graph_fg": "black",
        "graph_grid": "#cccccc",
        "math_color": "#000000",
        "btn_theme_bg": "#000000",
        "btn_theme_fg": "#ffffff",
        "btn_theme_text": "Modo: Claro"
    }
}

# Estado global
current_mode = "dark" # Default

# Variables globales para los widgets
ventana = None
entrada_funcion = None
frame_resultados = None # Frame scrollable para los pasos
frame_grafico = None
canvas_scroll = None # Canvas para el scroll
canvas_grafico = None # Canvas de matplotlib
figura_grafico = None # Figura de matplotlib
panel_superior = None
panel_central = None
frame_izq_container = None
etiqueta_funcion = None
btn_analizar = None
btn_limpiar = None
btn_tema = None

def get_theme():
    return THEMES[current_mode]

def toggle_theme():
    global current_mode
    if current_mode == "dark":
        current_mode = "light"
    else:
        current_mode = "dark"
    
    aplicar_tema()

def aplicar_tema():
    theme = get_theme()
    
    # Ventana principal
    ventana.configure(bg=theme["bg_window"])
    
    # Panel superior
    panel_superior.configure(bg=theme["bg_window"])
    etiqueta_funcion.configure(bg=theme["bg_window"], fg=theme["fg_text"])
    entrada_funcion.configure(bg=theme["bg_entry"], fg=theme["fg_entry"], insertbackground=theme["fg_text"])
    
    # Botones
    btn_analizar.configure(bg=theme["bg_button"], fg=theme["fg_button"])
    btn_limpiar.configure(bg=theme["bg_button_clear"], fg=theme["fg_button_clear"])
    btn_tema.configure(bg=theme["btn_theme_bg"], fg=theme["btn_theme_fg"], text=theme["btn_theme_text"])
    
    # Panel central y contenedores
    panel_central.configure(bg=theme["bg_window"])
    frame_izq_container.configure(bg=theme["bg_frame"])
    frame_grafico.configure(bg=theme["bg_frame"])
    
    # Scroll
    canvas_scroll.configure(bg=theme["bg_frame"])
    frame_resultados.configure(bg=theme["bg_frame"])
    
    # Actualizar resultados si existen (reconstruyendo si es necesario o iterando)
    # Para simplificar y asegurar consistencia, si hay resultados, re-analizamos
    # Si no, solo limpiamos visualmente los widgets hijos
    for widget in frame_resultados.winfo_children():
        # Recursivamente actualizar colores sería ideal, pero reconstruir es más seguro
        pass
        
    # Re-ejecutar análisis si hay texto, para regenerar los labels con los colores correctos
    if entrada_funcion.get().strip() != "":
        analizar_funcion()
    else:
        # Si está vacío, asegurar que el frame esté limpio con el color correcto
        for widget in frame_resultados.winfo_children():
            widget.destroy()
            
    # Actualizar gráfico si existe
    if figura_grafico:
        # Regenerar gráfico con nuevos colores
        # Necesitamos los datos... Si ya se analizó, analizar_funcion lo hará.
        pass

def crear_seccion_paso(padre, titulo, contenido_lista):
    # Función auxiliar para crear un marco con título y contenido estructurado
    theme = get_theme()
    
    # Estilos
    font_titulo = ("Arial", 11, "bold")
    color_titulo = theme["fg_title"]
    
    font_texto = ("Arial", 10)
    color_texto = theme["fg_text"]
    
    font_math = ("Times New Roman", 12, "bold")
    color_math = theme["math_color"]
    
    frame_paso = tk.LabelFrame(padre, text=titulo, font=font_titulo, padx=15, pady=10, bg=theme["bg_frame"], fg=color_titulo)
    frame_paso.pack(fill=tk.X, expand=True, padx=10, pady=10)
    
    if isinstance(contenido_lista, str):
        lineas = contenido_lista.split('\n')
    else:
        lineas = contenido_lista
        
    for linea in lineas:
        if linea.strip() != "":
            # --- CASO 1: Intervalos con colores ---
            es_intervalo_coloreado = False
            palabras_estado = ["CRECIENTE", "DECRECIENTE", "CÓNCAVA ARRIBA", "CÓNCAVA ABAJO"]
            
            for estado in palabras_estado:
                if estado in linea:
                    es_intervalo_coloreado = True
                    break
            
            if es_intervalo_coloreado and ("Intervalo" in linea or "Dominio" in linea):
                 frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                 frame_linea.pack(fill=tk.X, pady=1)
                 
                 match = re.search(r"(CRECIENTE.*|DECRECIENTE.*|CÓNCAVA ARRIBA.*|CÓNCAVA ABAJO.*)$", linea)
                 
                 if match:
                     parte_estado = match.group(1)
                     parte_izq = linea[:match.start()].strip()
                     
                     # Procesamos la parte izquierda
                     if parte_izq.startswith("Intervalo") and ":" in parte_izq:
                         try:
                             p1, resto = parte_izq.split("(", 1)
                             intervalo_str, p3 = resto.split(")", 1)
                             
                             tk.Label(frame_linea, text=p1 + "(", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                             tk.Label(frame_linea, text=intervalo_str, font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                             
                             if ":" in p3:
                                 sep, formula = p3.split(":", 1)
                                 tk.Label(frame_linea, text=")" + sep + ": ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                                 tk.Label(frame_linea, text=formula.strip(), font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                             else:
                                 tk.Label(frame_linea, text=")" + p3, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                         except:
                             tk.Label(frame_linea, text=parte_izq, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                     else:
                         # Caso Dominio
                         if "Dominio" in parte_izq and ":" in parte_izq:
                             try:
                                 p1, resto = parte_izq.split("(", 1)
                                 intervalo_str, p3 = resto.split(")", 1)
                                 
                                 tk.Label(frame_linea, text=p1 + "(", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                                 tk.Label(frame_linea, text=intervalo_str, font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                                 
                                 if ":" in p3:
                                     sep, formula = p3.split(":", 1)
                                     tk.Label(frame_linea, text=")" + sep + ": ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                                     tk.Label(frame_linea, text=formula.strip(), font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                                 else:
                                     tk.Label(frame_linea, text=")" + p3, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                             except:
                                 tk.Label(frame_linea, text=parte_izq, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                         else:
                             tk.Label(frame_linea, text=parte_izq, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                     
                     tk.Label(frame_linea, text="   ", font=font_texto, bg=theme["bg_frame"]).pack(side=tk.LEFT)
                     
                     color_estado = color_texto
                     # Colores específicos para estados (Red/Blue se mantienen igual o ajustados?)
                     # En dark mode, Blue oscuro no se ve bien. Usaremos un azul más claro (Cyan/LightBlue) si es dark mode?
                     # El usuario pidió "azul" y "rojo".
                     # Ajustemos ligeramente para dark mode si es necesario, pero "blue" y "red" standard suelen ser legibles.
                     # Para asegurar legibilidad en dark mode:
                     c_red = "red"
                     c_blue = "blue"
                     if current_mode == "dark":
                         c_red = "#ff5555" # Rojo más claro
                         c_blue = "#5555ff" # Azul más claro
                     
                     if "DECRECIENTE" in parte_estado:
                         color_estado = c_blue
                     elif "CRECIENTE" in parte_estado:
                         color_estado = c_red
                     elif "CÓNCAVA ARRIBA" in parte_estado:
                         color_estado = c_red
                     elif "CÓNCAVA ABAJO" in parte_estado:
                         color_estado = c_blue
                         
                     tk.Label(frame_linea, text=parte_estado, font=font_texto, bg=theme["bg_frame"], fg=color_estado).pack(side=tk.LEFT)
                 else:
                     tk.Label(frame_paso, text=linea, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(anchor="w")

            # --- CASO 2: Puntos Críticos ---
            elif "Ecuación:" in linea:
                frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                frame_linea.pack(fill=tk.X, pady=1)
                tk.Label(frame_linea, text="Ecuación: ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                tk.Label(frame_linea, text=linea.replace("Ecuación: ", ""), font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
            
            elif "Puntos críticos encontrados" in linea:
                frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                frame_linea.pack(fill=tk.X, pady=1)
                if ":" in linea:
                    texto_izq, lista_nums = linea.split(":", 1)
                    tk.Label(frame_linea, text=texto_izq + ": ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                    tk.Label(frame_linea, text=lista_nums.strip(), font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                else:
                    tk.Label(frame_linea, text=linea, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)

            elif "Evaluando x =" in linea:
                frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                frame_linea.pack(fill=tk.X, pady=1)
                match = re.search(r"x = ([\d\.\-]+)", linea)
                val_x = match.group(1) if match else "?"
                tk.Label(frame_linea, text="Evaluando ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                tk.Label(frame_linea, text=f"x = {val_x}", font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                tk.Label(frame_linea, text=" en ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                tk.Label(frame_linea, text="f''(x)", font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                tk.Label(frame_linea, text=":", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)

            elif "Resultado:" in linea:
                frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                frame_linea.pack(fill=tk.X, pady=1)
                tk.Label(frame_linea, text="Resultado: ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                if "< 0" in linea:
                    tk.Label(frame_linea, text="< 0", font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                    resto = linea.split("< 0")[1]
                elif "> 0" in linea:
                    tk.Label(frame_linea, text="> 0", font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                    resto = linea.split("> 0")[1]
                elif "= 0" in linea:
                    tk.Label(frame_linea, text="= 0", font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)
                    resto = linea.split("= 0")[1]
                else:
                    resto = linea.replace("Resultado: ", "")
                tk.Label(frame_linea, text=resto, font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)

            # --- CASO 3: Puntos de Inflexión ---
            elif "Igualando f''(x) = 0:" in linea:
                frame_linea = tk.Frame(frame_paso, bg=theme["bg_frame"])
                frame_linea.pack(fill=tk.X, pady=1)
                tk.Label(frame_linea, text="Igualando ", font=font_texto, bg=theme["bg_frame"], fg=color_texto).pack(side=tk.LEFT)
                tk.Label(frame_linea, text=linea.replace("Igualando ", ""), font=font_math, bg=theme["bg_frame"], fg=color_math).pack(side=tk.LEFT)

            # --- CASO DEFAULT ---
            else:
                estilo_actual = font_texto
                fg_color = color_texto
                es_texto_explicativo = False
                palabras_clave_texto = ["Paso", "Puntos críticos encontrados"]
                for palabra in palabras_clave_texto:
                    if linea.strip().startswith(palabra):
                        es_texto_explicativo = True
                        break
                if not es_texto_explicativo:
                    if "=" in linea or "f'(" in linea or "f''(" in linea:
                        estilo_actual = font_math
                        fg_color = color_math
                
                label = tk.Label(frame_paso, text=linea, justify=tk.LEFT, font=estilo_actual, bg=theme["bg_frame"], fg=fg_color, anchor="w", wraplength=400)
                label.pack(fill=tk.X, anchor="w", pady=1)
                def update_wrap(event, l=label):
                    l.config(wraplength=event.width - 20)
                frame_paso.bind("<Configure>", update_wrap)

def analizar_funcion():
    texto_ingresado = entrada_funcion.get()
    
    # Limpiamos
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    
    funcion = operations.convertir_texto_a_funcion(texto_ingresado)
    if funcion is None:
        messagebox.showerror("Error", "La función ingresada no es válida.")
        return

    # Cálculos
    txt_deriv = steps.explicar_derivadas(funcion)
    crear_seccion_paso(frame_resultados, "1. Cálculo de Derivadas", txt_deriv)
    
    d1 = operations.calcular_derivada(funcion)
    d2 = operations.calcular_derivada(d1)
    txt_criticos, maximos, minimos, inflexion = steps.explicar_puntos_criticos(funcion, d1, d2)
    crear_seccion_paso(frame_resultados, "2. Puntos Críticos y Clasificación", txt_criticos)
    
    txt_inflexion, pts_inflexion = steps.obtener_texto_inflexion(d2)
    crear_seccion_paso(frame_resultados, "3. Puntos de Inflexión", txt_inflexion)
    
    txt_crecimiento = steps.obtener_intervalos_crecimiento(d1, maximos, minimos)
    crear_seccion_paso(frame_resultados, "4. Intervalos de Crecimiento/Decrecimiento", txt_crecimiento)
    
    txt_concavidad = steps.obtener_intervalos_concavidad(d2, pts_inflexion)
    crear_seccion_paso(frame_resultados, "5. Intervalos de Concavidad", txt_concavidad)
    
    frame_resultados.update_idletasks()
    canvas_scroll.config(scrollregion=canvas_scroll.bbox("all"))
    
    graficar_en_ventana(funcion, maximos, minimos, pts_inflexion)

def graficar_en_ventana(funcion, maximos, minimos, inflexion):
    global canvas_grafico, figura_grafico
    theme = get_theme()
    
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    
    # Configuración de colores de matplotlib
    plt.rcParams['figure.facecolor'] = theme["graph_bg"]
    plt.rcParams['axes.facecolor'] = theme["graph_bg"]
    plt.rcParams['axes.edgecolor'] = theme["graph_fg"]
    plt.rcParams['axes.labelcolor'] = theme["graph_fg"]
    plt.rcParams['xtick.color'] = theme["graph_fg"]
    plt.rcParams['ytick.color'] = theme["graph_fg"]
    plt.rcParams['text.color'] = theme["graph_fg"]
    plt.rcParams['grid.color'] = theme["graph_grid"]
    
    figura_grafico = plt.figure(figsize=(5, 4), dpi=100)
    ax = figura_grafico.add_subplot(111)
    
    rango_x = [-10, 10]
    puntos_x = []
    for m in maximos: puntos_x.append(float(m[0]))
    for m in minimos: puntos_x.append(float(m[0]))
    for p in inflexion: puntos_x.append(float(p))
    
    if len(puntos_x) > 0:
        rango_x[0] = min(puntos_x) - 2
        rango_x[1] = max(puntos_x) + 2
        
    import numpy as np
    x_vals = np.linspace(rango_x[0], rango_x[1], 400)
    y_vals = []
    
    for val in x_vals:
        y = operations.evaluar_funcion(funcion, val)
        y_vals.append(float(y))
        
    ax.plot(x_vals, y_vals, label='f(x)', linewidth=2)
    
    for m in maximos:
        ax.plot(float(m[0]), float(m[1]), 'ro', markersize=8)
        ax.text(float(m[0]), float(m[1]), 'Max', fontsize=9, color='red', verticalalignment='bottom')
        
    for m in minimos:
        ax.plot(float(m[0]), float(m[1]), 'bo', markersize=8)
        ax.text(float(m[0]), float(m[1]), 'Min', fontsize=9, color='blue', verticalalignment='top')
        
    for p in inflexion:
        y = operations.evaluar_funcion(funcion, p)
        ax.plot(float(p), float(y), 'go', markersize=8)
        ax.text(float(p), float(y), 'Inf', fontsize=9, color='green', verticalalignment='bottom')
        
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.axhline(0, color=theme["graph_fg"], linewidth=1)
    ax.axvline(0, color=theme["graph_fg"], linewidth=1)
    
    # Leyenda con texto correcto
    leg = ax.legend(facecolor=theme["graph_bg"], edgecolor=theme["graph_fg"])
    for text in leg.get_texts():
        text.set_color(theme["graph_fg"])
    
    figura_grafico.tight_layout()
    
    canvas_grafico = FigureCanvasTkAgg(figura_grafico, master=frame_grafico)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def limpiar_todo():
    entrada_funcion.delete(0, tk.END)
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    canvas_scroll.config(scrollregion=canvas_scroll.bbox("all"))

def validar_entrada(char):
    # Solo permite caracteres válidos para expresiones matemáticas
    # Números, operadores, paréntesis, x, y letras para funciones (sin, cos, etc.)
    permitidos = "0123456789+-*/^(). xyzsincotaelgqpr"
    return char.lower() in permitidos

def iniciar_gui():
    global ventana, entrada_funcion, frame_resultados, frame_grafico, canvas_scroll
    global panel_superior, panel_central, frame_izq_container, etiqueta_funcion, btn_analizar, btn_limpiar, btn_tema
    
    ventana = tk.Tk()
    ventana.title("grafi")
    
    # Configuración de tamaño y posición
    ancho_ventana = 1000
    alto_ventana = 700
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    x_c = int((screen_width/2) - (ancho_ventana/2))
    y_c = int((screen_height/2) - (alto_ventana/2))
    
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x_c}+{y_c}")
    ventana.minsize(800, 600)
    
    # Función para recursos en PyInstaller
    import sys
    import os
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    try:
        img_path = resource_path("logo.png")
        img_logo = tk.PhotoImage(file=img_path)
        ventana.iconphoto(False, img_logo)
    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")
    
    # Validación de entrada
    vcmd = (ventana.register(validar_entrada), '%S')
    
    # Panel superior
    panel_superior = tk.Frame(ventana, pady=20, padx=20)
    panel_superior.pack(side=tk.TOP, fill=tk.X)
    
    etiqueta_funcion = tk.Label(panel_superior, text="Función f(x):", font=("Arial", 14, "bold"))
    etiqueta_funcion.pack(side=tk.LEFT, padx=(0, 10))
    
    entrada_funcion = tk.Entry(panel_superior, width=35, font=("Arial", 12), bd=2, relief=tk.FLAT,
                               validate="key", validatecommand=vcmd)
    entrada_funcion.pack(side=tk.LEFT, padx=10)
    # Analizar al presionar Enter
    entrada_funcion.bind('<Return>', lambda event: analizar_funcion())
    
    btn_analizar = tk.Button(panel_superior, text="ANALIZAR", command=analizar_funcion, 
                             font=("Arial", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
    btn_analizar.pack(side=tk.LEFT, padx=10)
    
    btn_limpiar = tk.Button(panel_superior, text="LIMPIAR", command=limpiar_todo, 
                            font=("Arial", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
    btn_limpiar.pack(side=tk.LEFT, padx=10)
    
    # Botón de Tema (Derecha)
    btn_tema = tk.Button(panel_superior, text="Modo: Oscuro", command=toggle_theme,
                         font=("Arial", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, cursor="hand2")
    btn_tema.pack(side=tk.RIGHT, padx=10)
    
    # Panel central
    panel_central = tk.PanedWindow(ventana, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.RAISED)
    panel_central.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Lado Izquierdo
    frame_izq_container = tk.Frame(panel_central, bd=1, relief=tk.SOLID)
    panel_central.add(frame_izq_container, width=450, minsize=300)
    
    canvas_scroll = tk.Canvas(frame_izq_container, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_izq_container, orient="vertical", command=canvas_scroll.yview)
    frame_resultados = tk.Frame(canvas_scroll)
    
    frame_resultados_id = canvas_scroll.create_window((0, 0), window=frame_resultados, anchor="nw")
    
    def on_canvas_configure(event):
        canvas_scroll.itemconfig(frame_resultados_id, width=event.width)
    
    canvas_scroll.bind("<Configure>", on_canvas_configure)
    frame_resultados.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    
    canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Lado Derecho
    frame_grafico = tk.Frame(panel_central, bd=1, relief=tk.SOLID)
    panel_central.add(frame_grafico, minsize=300)
    
    # Aplicar tema inicial (Dark)
    aplicar_tema()
    
    ventana.mainloop()

if __name__ == "__main__":
    iniciar_gui()
