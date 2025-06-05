from estructuras_datos import registros_real, registros_int, registros_char, registros_string, memoria_spill, tabla_var, Variable
from analisis_lexico import es_id, es_constante

def asignar_registro(tipo):
    if tipo == "real":  # float en Pascal
        return registros_real.pop(0) if registros_real else f"SPILL_mem_{len(memoria_spill)}"
    elif tipo == "integer":  # int en Pascal
        return registros_int.pop(0) if registros_int else f"SPILL_mem_{len(memoria_spill)}"
    elif tipo == "char":
        return registros_char.pop(0) if registros_char else f"SPILL_mem_{len(memoria_spill)}"
    elif tipo == "string":
        return registros_string.pop(0) if registros_string else f"SPILL_mem_{len(memoria_spill)}"
    else:
        print(f"Error: tipo de variable no reconocido ('{tipo}').")
        return None

#Agregar la nueva variable a la tabla
def agregar_var(tabla_var, nombre, tipo):
    if existe_var(tabla_var, nombre):
        print(f'Error: la Variable "{nombre}" ya ha sido declarada')
        return False
    else:
        registro = asignar_registro(tipo)
        var = Variable(nombre, tipo, None, registro) 
        tabla_var.append(var)
        if "SPILL" in registro:
            memoria_spill.append(var)

#checa si la variable existe en la tabla
def existe_var(tabla_var, nombre):
    for v in tabla_var:
        if v.nombre == nombre:
            return True
    return False

#si existe la variable en la tabla, asigna el valor al campo "valor"
def set_var(tabla_var, nombre, valor):
    if existe_var(tabla_var, nombre):
        for v in tabla_var:
            if v.nombre == nombre:
                valor_anterior = v.valor
                v.valor = valor
                return True
    else:
        return False
    
# recupera el valor de la variable por medio de su nombre
def get_valor(tabla_var, varNombre):
    for v in tabla_var:
        if (v.nombre == varNombre):
            return v.valor
    return None

# obtiene el registro que se le asigno a una variable
def get_registro_var(tabla_var, nombre):
    for v in tabla_var:
        if v.nombre == nombre:
            return v.registro
    return None

def get_tipo_var(tabla_var, nombre): #obtener el tipo de la variable
    for v in tabla_var:
        if v.nombre == nombre:
            return v.tipo
    return None

def asignar_registro_temporal(tipo): #Asigna un registro temporal
    global registros_real, registros_int
    if tipo == "real":
        if registros_real:
            return registros_real.pop(0)
        else:
            return f"SPILL_temp_{len(memoria_spill)}"
    else: 
        if registros_int:
            return registros_int.pop(0)
        else:
            return f"SPILL_temp_{len(memoria_spill)}"

def liberar_registro_temporal(registro, tipo): 
    global registros_real, registros_int
    if "SPILL" not in registro:
        if tipo == "real" and registro.startswith("ft"):
            registros_real.append(registro)
        elif registro in ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"]:
            registros_int.append(registro)

# imprime el contenido de la tabla
def imprime_tabla_var(tabla_var):
    print()
    print(' Tabla de variables')
    print('nombre\t\ttipo\t\tregistro asignado\tvalor')
    for v in tabla_var:
        print(f'{v.nombre}\t\t{v.tipo}\t\t{v.registro}\t\t{v.valor}')
    return None

def evaluar_expresion(expresion, tabla_var): #procesa una expresión aritmética
    try:
        expr_evaluada = []
        for token in expresion:
            if es_id(token):
                valor = get_valor(tabla_var, token)
                if valor is not None:
                    expr_evaluada.append(str(valor))
                else:
                    print(f"Error: Variable '{token}' no tiene valor asignado")
                    return None
            else:
                expr_evaluada.append(token)
        
        expr_str = ' '.join(expr_evaluada)
        resultado = eval(expr_str)
        
        return resultado
    except Exception as e:
        print(f"Error al evaluar expresión: {e}")
        print(f"  Expresión problemática: {expresion}")
        print(f"  Expresión evaluada: {expr_evaluada if 'expr_evaluada' in locals() else 'No disponible'}")
        return None