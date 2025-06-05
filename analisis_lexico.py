import re

def es_simbolo_especial(caracter):
    return caracter in "+-*;,.:!#=%&/(){}[]<>=="

def es_separador(caracter):
    return caracter in " \n\t"

def es_id(cadena):
    if not cadena:
        return False
    return cadena[0] in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def es_tipo(cadena):
    tipos = ["integer", "real", "string", "boolean", "char", "text"]
    return cadena.lower() in tipos

def es_palabra_reservada(cadena):
    reservadas = ['and', 'array', 'begin', 'case', 'const', 'div', 'do', 'downto', 'else', 'end', 'file', 'for', 'function',
                  'goto', 'if', 'in', 'label', 'mod', 'nil', 'not', 'of', 'or', 'packed','procedure', 'program', 'record',
                  'repeat', 'set', 'then', 'to', 'type', 'until', 'var', 'while', 'with', 'uses']
    return cadena.lower() in reservadas

def es_procedimiento(cadena):
    procedimientos = ['write', 'writeln', 'read', 'readln', 'assign', 'rewrite', 'reset', 'append', 'close', 'dispose', 'new', 'getmem',
                       'freemem', 'fillchar', 'move', 'sizeof', 'addr', 'ptr', 'str', 'val', 'ord', 'chr', 'succ', 'pred', 'upcase',
                       'locase', 'length', 'copy', 'concat', 'delete', 'insert', 'pos', 'randomize', 'random', 'delay', 'halt', 'exit']
    return cadena.lower() in procedimientos

def es_operador(cadena):
    operadores = [':=', '+', '-', '*', '/', '=', '<', '>']
    return cadena in operadores

def es_constante(cadena):
    if not cadena:
        return False
    return cadena[0].isdigit()

def es_cadena(cadena): # checha comillas simples y dobles
    return (cadena.startswith("'") and cadena.endswith("'")) or \
           (cadena.startswith('"') and cadena.endswith('"'))

def get_etiqueta(token):
    if es_operador(token):
        return 'Operador'
    elif es_simbolo_especial(token):
        return 'Simbolo especial'
    elif es_palabra_reservada(token):
        return 'Palabra reservada'
    elif es_procedimiento(token):
        return 'Procedimiento estandar'
    elif es_tipo(token):
        return 'Tipo'
    elif es_cadena(token):
        return 'Cadena'
    elif es_constante(token):
        return 'Constante'
    elif es_id(token):
        return 'ID'
    else:
        return 'Desconocido'

# Eliminar comentarios tipo (* ... *)
def tokenizar(texto): 
    estado = 'Z'
    texto_sin_comentarios = ''
    i = 0
    while i < len(texto):
        letra = texto[i]
        if estado == 'Z':
            if letra == '(':
                # mirar hacia adelante para ver si es el inicio de un comentario
                if i + 1 < len(texto) and texto[i + 1] == '*':
                    estado = 'B'  # entrar en estado de comentario tipo (* *)
                    i += 1        # Consume el '*'
                else:
                    texto_sin_comentarios += letra  # Es un paréntesis normal
            else:
                texto_sin_comentarios += letra
        elif estado == 'B':
            if letra == '*':
                estado = 'C'  # posible cierre de comentario
            # si no, seguir en estado B
        elif estado == 'C':
            if letra == ')':
                estado = 'Z'  # fin del comentario
            else:
                estado = 'B'  # no era cierre, volver a estado de comentario
        i += 1

    print("----- Quita comentarios ----")
    print(texto_sin_comentarios)
    print("-----------------------")
    #separar "begin" y "end" si están seguidos de código
    texto_sin_comentarios = re.sub(r'\bbegin\b', 'begin', texto_sin_comentarios)
    texto_sin_comentarios = re.sub(r'\bend\b', 'end', texto_sin_comentarios)

    # Marca error cuando falta un ";"
    lineas = texto_sin_comentarios.split('\n')
    excepciones = ['program', 'uses', 'begin', 'end', 'var', 'const', 'type', 'procedure', 'function', 'if', 'then', 'else', 'while', 'do', 'for', 'to', 'repeat', 'until']
    errores_encontrados = False
    num_linea = 1

    for i, linea in enumerate(lineas):
        l = linea.strip()
        if l == '': # saltamos líneas vacías
            num_linea += 1
            continue
         
        if l.endswith(';'): # saltamos líneas que terminan con ';'
            num_linea += 1
            continue  
        
        if l.lower() in ['begin', 'end', 'end.']: # saltamos líneas con 'begin', 'end' o 'end.'
            num_linea += 1
            continue

        palabras = l.split() # Checamos si la línea empieza con una palabra clave que no mecesita ;
        if palabras:  
            primera_palabra = palabras[0].lower()
            # Si es una línea de declaración (program, uses, var, etc.)
            if primera_palabra in excepciones:
                if primera_palabra == 'var':
                    if len(palabras) > 1:# var x1 real necesita ;
                        print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                        errores_encontrados = True
                    else:
                        num_linea += 1
                        continue
                
                elif primera_palabra == 'program' and len(palabras) > 1: #program necesita ;
                    print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                    errores_encontrados = True
                
                elif primera_palabra == 'uses' and len(palabras) > 1:# uses necesita ;
                    print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                    errores_encontrados = True
                
                elif len(palabras) == 1: # no necesita ;
                    num_linea += 1
                    continue
                else:
                    num_linea += 1
                    continue
            else:
                # Si no es palabra clave, verificar si es una instrucción que necesita ;
                if ':=' in l:
                    print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                    errores_encontrados = True
                elif any(proc in l.lower() for proc in ['write', 'writeln', 'read', 'readln']):
                    if '(' in l and ')' in l:
                        print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                        errores_encontrados = True
                elif ':' in l and not ':=' in l:
                    print(f'Error: Falta un ";" al final de la línea {num_linea} -> {l}')
                    errores_encontrados = True
        num_linea += 1

    if not errores_encontrados:
        print('El programa es correcto, no faltan ";"')

    # Tokenización 
    separadores = [' ', '\t', '\n']
    especiales = '[](),;:+-*/=<>@^{}$'
    tokens = []
    i = 0
    while i < len(texto_sin_comentarios):
        letra = texto_sin_comentarios[i]
        if letra in separadores:
            i += 1
            continue
        # Cadenas entre comillas
        elif letra == "'" or letra == '"':
            comilla_tipo = letra
            cadena = letra
            i += 1
            comilla_cerrada = False
            while i < len(texto_sin_comentarios):
                cadena += texto_sin_comentarios[i]
                if texto_sin_comentarios[i] == comilla_tipo:
                    comilla_cerrada = True
                    break
                i += 1
            
            if not comilla_cerrada:
                print(f"Error: Comilla no cerrada en la cadena '{cadena}'")
            tokens.append(cadena)
            i += 1 
        # Operador :=
        elif texto_sin_comentarios[i:i+2] == ':=':
            tokens.append(':=')
            i += 2
        elif letra in especiales:
            tokens.append(letra)
            i += 1
        else:
            token = ''
            if texto_sin_comentarios[i].isdigit(): # detectar los números con punto decimal
                while i < len(texto_sin_comentarios) and (texto_sin_comentarios[i].isdigit() or texto_sin_comentarios[i] == '.'):
                    token += texto_sin_comentarios[i]
                    i += 1
                tokens.append(token)
            else:
                while i < len(texto_sin_comentarios) and texto_sin_comentarios[i] not in especiales and texto_sin_comentarios[i] not in separadores:
                    token += texto_sin_comentarios[i]
                    i += 1
                tokens.append(token)
    return tokens