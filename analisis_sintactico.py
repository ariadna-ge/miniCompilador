#De infija a posfija
precedencia = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '(': 0
}

def infija_a_postfija(tokens):
    salida = []
    pila = []
    for token in tokens:
        if token.isalnum() or token.startswith("'") or token.startswith('"'):  # variables o constantes
            salida.append(token)
        elif token == '(':
            pila.append(token)
        elif token == ')':
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            if pila:
                pila.pop() 
        elif token in precedencia:
            while pila and precedencia.get(pila[-1], 0) >= precedencia[token]:
                salida.append(pila.pop())
            pila.append(token)
        else:
            salida.append(token)  

    while pila:
        salida.append(pila.pop())
    return salida

def infija_a_prefija(tokens):
    tokens = tokens[::-1]
    for i in range(len(tokens)):
        if tokens[i] == '(':
            tokens[i] = ')'
        elif tokens[i] == ')':
            tokens[i] = '('
    postfija = infija_a_postfija(tokens)
    return postfija[::-1]

def extraer_instrucciones_begin_end(tokens): #Extrae todas las instrucciones individuales entre begin y end
    if not tokens or tokens[0].lower() != 'begin':
        return []
    
    instrucciones = []
    instruccion_actual = []
    i = 1  # Empezar después de 'begin'
    nivel_begin = 1
    
    while i < len(tokens) and nivel_begin > 0:
        token = tokens[i]
        
        if token.lower() == 'begin':
            nivel_begin += 1
            instruccion_actual.append(token)
        elif token.lower() == 'end':
            nivel_begin -= 1
            if nivel_begin == 0:
                # Encontramos el 'end' que cierra nuestro 'begin'
                if instruccion_actual:
                    instrucciones.append(instruccion_actual[:])  # Copia de la instrucción actual
                break
            else:
                instruccion_actual.append(token)
        elif token == ';':
            # Fin de una instrucción
            if instruccion_actual:
                instruccion_actual.append(token)  # Incluir el punto y coma
                instrucciones.append(instruccion_actual[:])  # Copia de la instrucción
                instruccion_actual = []
        else:
            instruccion_actual.append(token)
        i += 1
    
    # Si quedó una instrucción sin punto y coma al final
    if instruccion_actual:
        instrucciones.append(instruccion_actual)
    return instrucciones

#Divide tokens en instrucciones
def dividir_en_instrucciones(tokens): 
    instrucciones = []
    instruccion_actual = []
    i = 0
    
    while i < len(tokens):
        token = tokens[i]
        if token.lower() == 'for':
            j = i
            while j < len(tokens) and tokens[j].lower() != 'do':
                j += 1
            if j < len(tokens):  # Encontramos 'do'
                if j + 1 < len(tokens) and tokens[j + 1].lower() == 'begin': # Verificar si después viene 'begin'
                    nivel_begin = 0
                    k = j + 1
                    while k < len(tokens):
                        if tokens[k].lower() == 'begin':
                            nivel_begin += 1
                        elif tokens[k].lower() == 'end':
                            nivel_begin -= 1
                            if nivel_begin == 0:
                                break
                        k += 1
                    if k < len(tokens):
                        instruccion_for = tokens[i:k+1]  # Incluimps el 'end'
                        instrucciones.append(instruccion_for)
                        i = k + 1
                        continue
                else:
                    # FOR con una sola instrucción
                    k = j + 1
                    while k < len(tokens) and tokens[k] != ';':
                        k += 1
                    if k < len(tokens):
                        k += 1  # Incluimos el ';'
                    instruccion_for = tokens[i:k]
                    instrucciones.append(instruccion_for)
                    i = k
                    continue
        instruccion_actual.append(token)
        
        if token == ';': # Si encontramos ';', es fin de instrucción
            instrucciones.append(instruccion_actual)
            instruccion_actual = []
        
        elif token.lower() in ['begin', 'end'] and len(instruccion_actual) == 1:
            instrucciones.append(instruccion_actual)
            instruccion_actual = []   
        i += 1
    
    if instruccion_actual:
        instrucciones.append(instruccion_actual)
    
    for idx, instr in enumerate(instrucciones):
        print(f"Instrucción {idx+1}: {instr}")  # Debug
    return instrucciones