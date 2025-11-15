import sympy
import numpy as np

# Aquí definimos las funciones matemáticas puras que usaremos en el programa.
# No dependemos de ninguna interfaz gráfica aquí, solo cálculos.

def convertir_texto_a_funcion(texto_funcion):
    # Aquí intentamos convertir el texto que ingresó el usuario a una expresión de SymPy.
    # Usamos try-except para que el programa no se rompa si el usuario escribe algo mal.
    try:
        x = sympy.symbols('x')
        # sympify convierte el string a expresión matemática
        funcion = sympy.sympify(texto_funcion)
        return funcion
    except:
        # Si falla, devolvemos None para indicar error
        return None

def calcular_derivada(funcion):
    # Aquí calculamos la derivada de la función con respecto a x.
    x = sympy.symbols('x')
    derivada = sympy.diff(funcion, x)
    return derivada

def encontrar_puntos_criticos(primera_derivada):
    # Aquí buscamos los valores de x donde la derivada es 0.
    x = sympy.symbols('x')
    try:
        # solve nos devuelve una lista de soluciones
        puntos = sympy.solve(primera_derivada, x)
        
        # Filtramos para quedarnos solo con números reales (no imaginarios)
        puntos_reales = []
        for p in puntos:
            if p.is_real:
                puntos_reales.append(p)
                
        return puntos_reales
    except:
        # Si no podemos resolver, devolvemos lista vacía
        return []

def evaluar_funcion(funcion, valor_x):
    # Aquí evaluamos la función en un punto específico x.
    x = sympy.symbols('x')
    try:
        resultado = funcion.subs(x, valor_x)
        return resultado
    except:
        return 0

def resolver_puntos_inflexion(segunda_derivada):
    # Aquí buscamos donde la segunda derivada se hace 0.
    x = sympy.symbols('x')
    try:
        puntos = sympy.solve(segunda_derivada, x)
        puntos_reales = []
        for p in puntos:
            if p.is_real:
                puntos_reales.append(p)
        return puntos_reales
    except:
        return []