import operations

# Este módulo se encarga de generar el texto explicativo paso a paso.
# Usamos las funciones de operations.py para obtener los datos.

def explicar_derivadas(funcion):
    # Aquí construimos el texto del paso de derivación
    d1 = operations.calcular_derivada(funcion)
    d2 = operations.calcular_derivada(d1)
    
    texto = ""
    texto = texto + "Paso 1: Calcular la Primera Derivada f'(x)\n"
    texto = texto + "   f(x)  = " + str(funcion) + "\n"
    texto = texto + "   f'(x) = " + str(d1) + "\n\n"
    
    texto = texto + "Paso 2: Calcular la Segunda Derivada f''(x)\n"
    texto = texto + "   f''(x) = " + str(d2)
    return texto

def explicar_puntos_criticos(funcion, d1, d2):
    # Aquí explicamos cómo obtenemos y clasificamos los puntos
    criticos = operations.encontrar_puntos_criticos(d1)
    
    texto = "Paso 3: Igualar f'(x) a 0 para hallar puntos críticos\n"
    texto = texto + "   Ecuación: " + str(d1) + " = 0\n"
    
    if len(criticos) == 0:
        texto = texto + "   No se encontraron puntos críticos reales."
        return texto, [], [], [] # Retornamos listas vacías
        
    texto = texto + "   Puntos críticos encontrados (x): " + str(criticos) + "\n\n"
    
    texto = texto + "Paso 4: Criterio de la Segunda Derivada\n"
    
    lista_maximos = []
    lista_minimos = []
    lista_inflexion = [] # Puntos críticos que fallan el test de 2da derivada
    
    for punto in criticos:
        evaluacion = operations.evaluar_funcion(d2, punto)
        texto = texto + "   Evaluando x = " + str(punto) + " en f''(x):\n"
        texto = texto + "   f''(" + str(punto) + ") = " + str(evaluacion) + "\n"
        
        # Lógica sin ternarios
        if evaluacion > 0:
            texto = texto + "   Resultado: > 0, es un MÍNIMO RELATIVO\n"
            y_val = operations.evaluar_funcion(funcion, punto)
            lista_minimos.append((punto, y_val))
        else:
            if evaluacion < 0:
                texto = texto + "   Resultado: < 0, es un MÁXIMO RELATIVO\n"
                y_val = operations.evaluar_funcion(funcion, punto)
                lista_maximos.append((punto, y_val))
            else:
                texto = texto + "   Resultado: = 0, el criterio no decide (posible inflexión)\n"
                lista_inflexion.append(punto)
                
    return texto, lista_maximos, lista_minimos, lista_inflexion

def explicar_evaluacion(funcion, puntos_interes):
    # Genera texto mostrando la sustitución para graficar
    texto = "Paso Extra: Evaluar f(x) en puntos de interés para graficar\n"
    
    # Unimos listas si hay varias
    for p in puntos_interes:
        # Aseguramos que sea un número (puede venir como tupla a veces)
        valor_x = 0
        if type(p) is tuple:
            valor_x = p[0]
        else:
            valor_x = p
            
        valor_y = operations.evaluar_funcion(funcion, valor_x)
        texto = texto + "   f(" + str(valor_x) + ") = " + str(valor_y) + "\n"
        
    return texto

def obtener_texto_inflexion(d2):
    puntos = operations.resolver_puntos_inflexion(d2)
    texto = "   Igualando f''(x) = 0: " + str(puntos)
    return texto, puntos

def obtener_intervalos_crecimiento(d1, maximos, minimos):
    # Explicación de intervalos de crecimiento
    # Recibimos d1 para evaluar signos
    puntos = []
    for m in maximos: puntos.append(float(m[0]))
    for m in minimos: puntos.append(float(m[0]))
    puntos.sort()
    
    texto = ""
    
    # Caso sin puntos críticos
    if len(puntos) == 0:
        val_prueba = 0
        signo = operations.evaluar_funcion(d1, val_prueba)
        if signo == 0: signo = operations.evaluar_funcion(d1, 1) # Intento de desempate
        
        if signo > 0:
            texto = "Dominio (-∞, ∞): f'(0) > 0   CRECIENTE ↑"
        elif signo < 0:
            texto = "Dominio (-∞, ∞): f'(0) < 0   DECRECIENTE ↓"
        else:
            texto = "La función es constante."
        return texto

    # Caso con puntos críticos
    # Intervalo inicial (-inf, x0)
    val_prueba = puntos[0] - 1
    signo = operations.evaluar_funcion(d1, val_prueba)
    estado = "CRECIENTE ↑" if signo > 0 else "DECRECIENTE ↓"
    texto = texto + f"Intervalo (-∞, {puntos[0]}): f'({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}\n"
    
    # Intervalos intermedios
    for i in range(len(puntos) - 1):
        x_start = puntos[i]
        x_end = puntos[i+1]
        val_prueba = (x_start + x_end) / 2
        signo = operations.evaluar_funcion(d1, val_prueba)
        estado = "CRECIENTE ↑" if signo > 0 else "DECRECIENTE ↓"
        texto = texto + f"Intervalo ({x_start}, {x_end}): f'({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}\n"
        
    # Intervalo final (xn, inf)
    val_prueba = puntos[-1] + 1
    signo = operations.evaluar_funcion(d1, val_prueba)
    estado = "CRECIENTE ↑" if signo > 0 else "DECRECIENTE ↓"
    texto = texto + f"Intervalo ({puntos[-1]}, ∞): f'({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}"
    
    return texto

def obtener_intervalos_concavidad(d2, puntos_inflexion):
    # Explicación de intervalos de concavidad
    # Recibimos d2 para evaluar signos
    puntos = []
    for p in puntos_inflexion: puntos.append(float(p))
    puntos.sort()
    
    texto = ""
    
    # Caso sin puntos de inflexión
    if len(puntos) == 0:
        val_prueba = 0
        signo = operations.evaluar_funcion(d2, val_prueba)
        if signo == 0: signo = operations.evaluar_funcion(d2, 1)
        
        if signo > 0:
            texto = "Dominio (-∞, ∞): f''(0) > 0   CÓNCAVA ARRIBA ∪"
        elif signo < 0:
            texto = "Dominio (-∞, ∞): f''(0) < 0   CÓNCAVA ABAJO ∩"
        else:
            texto = "No hay concavidad definida (posible recta)."
        return texto
        
    # Caso con puntos de inflexión
    # Intervalo inicial (-inf, x0)
    val_prueba = puntos[0] - 1
    signo = operations.evaluar_funcion(d2, val_prueba)
    estado = "CÓNCAVA ARRIBA ∪" if signo > 0 else "CÓNCAVA ABAJO ∩"
    texto = texto + f"Intervalo (-∞, {puntos[0]}): f''({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}\n"
    
    # Intervalos intermedios
    for i in range(len(puntos) - 1):
        x_start = puntos[i]
        x_end = puntos[i+1]
        val_prueba = (x_start + x_end) / 2
        signo = operations.evaluar_funcion(d2, val_prueba)
        estado = "CÓNCAVA ARRIBA ∪" if signo > 0 else "CÓNCAVA ABAJO ∩"
        texto = texto + f"Intervalo ({x_start}, {x_end}): f''({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}\n"
        
    # Intervalo final (xn, inf)
    val_prueba = puntos[-1] + 1
    signo = operations.evaluar_funcion(d2, val_prueba)
    estado = "CÓNCAVA ARRIBA ∪" if signo > 0 else "CÓNCAVA ABAJO ∩"
    texto = texto + f"Intervalo ({puntos[-1]}, ∞): f''({val_prueba:.1f}) {' > 0' if signo > 0 else '< 0'}   {estado}"
    
    return texto