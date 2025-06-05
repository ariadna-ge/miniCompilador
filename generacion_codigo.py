from estructuras_datos import Variable, tabla_var, memoria_spill, seccion_data
from analisis_semantico import asignar_registro_temporal, get_registro_var, get_tipo_var, get_valor
from analisis_lexico import es_operador, es_constante, es_id, es_cadena
from analisis_semantico import existe_var

#Generamos el código intermedio y ensamblador RISC-V desde notación postfija
def codigoInterEnsambla(posfija, tabla_var): 
    codigo_intermedio = []
    codigo_ensamblador = []
    pila = []
    cont = 1
    mapeo_temporales = {}  # Para checar qué registro tiene cada temporal
    num_operadores = sum(1 for t in posfija if es_operador(t) and t != ':=')
    operador_actual = 0
    
    for token in posfija:
        if es_operador(token) and token != ':=':  # es operador aritmético
            if len(pila) < 2:
                print(f"Error: expresión mal formada")
                return [], []
            
            op2 = pila.pop()
            op1 = pila.pop()
            
            # generamos código intermedio
            temp_var = f"t{cont}"
            codigo_intermedio.append(f"{temp_var} = {op1} {token} {op2}")
            
            # Obtenemos los registros o sus valores
            reg1 = None
            reg2 = None
            es_inmediato1 = False
            es_inmediato2 = False
            
            # procesamos op1
            if op1 in mapeo_temporales:
                reg1 = mapeo_temporales[op1]
            elif es_constante(str(op1)):
                es_inmediato1 = True
                reg1 = op1
            elif es_id(op1):
                reg1 = get_registro_var(tabla_var, op1)
                if not reg1:
                    print(f"Error: variable '{op1}' no encontrada")
                    return [], []
            else:
                reg1 = op1  
            # procesamos op2
            if op2 in mapeo_temporales:
                reg2 = mapeo_temporales[op2]
            elif es_constante(str(op2)):
                es_inmediato2 = True
                reg2 = op2
            elif es_id(op2):
                reg2 = get_registro_var(tabla_var, op2)
                if not reg2:
                    print(f"Error: variable '{op2}' no encontrada")
                    return [], []
            else:
                reg2 = op2
            # checar el tipo de resultado
            tipo_resultado = "integer"  
            if es_id(op1):
                tipo1 = get_tipo_var(tabla_var, op1)
                if tipo1 == "real":
                    tipo_resultado = "real"
            if es_id(op2):
                tipo2 = get_tipo_var(tabla_var, op2)
                if tipo2 == "real":
                    tipo_resultado = "real"

            # Asignamos el registro temporal para el resultado
            destino = asignar_registro_temporal(tipo_resultado)
            mapeo_temporales[temp_var] = destino

            # Agregamos a la tabla 
            if operador_actual < num_operadores - 1:
                if not existe_var(tabla_var, temp_var):
                    # calculamos el valor del temporal
                    val1 = get_valor(tabla_var, op1) if es_id(op1) else float(op1)
                    val2 = get_valor(tabla_var, op2) if es_id(op2) else float(op2)

                    if token == '+':
                        valor_resultado = val1 + val2
                    elif token == '-':
                        valor_resultado = val1 - val2
                    elif token == '*':
                        valor_resultado = val1 * val2
                    elif token == '/':
                        valor_resultado = val1 / val2 if val2 != 0 else None
                    else:
                        valor_resultado = None

                    var_temporal = Variable(temp_var, tipo_resultado, valor_resultado, destino)
                    tabla_var.append(var_temporal)

            # Generamos código ensamblador RISC-V
            if tipo_resultado == "real":
                # Operaciones de punto flotante
                if token == '+':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li.s {destino}, {float(reg1) + float(reg2)}  # {destino} = {reg1} + {reg2}")
                    elif es_inmediato1:
                        codigo_ensamblador.append(f"li.s ft31, {reg1}")
                        codigo_ensamblador.append(f"fadd.s {destino}, ft31, {reg2}  # {destino} = {reg1} + {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li.s ft31, {reg2}")
                        codigo_ensamblador.append(f"fadd.s {destino}, {reg1}, ft31  # {destino} = {reg1} + {reg2}")
                    else:
                        codigo_ensamblador.append(f"fadd.s {destino}, {reg1}, {reg2}  # {destino} = {reg1} + {reg2}")
                
                elif token == '-':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li.s {destino}, {float(reg1) - float(reg2)}  # {destino} = {reg1} - {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li.s ft31, {reg2}")
                        codigo_ensamblador.append(f"fsub.s {destino}, {reg1}, ft31  # {destino} = {reg1} - {reg2}")
                    else:
                        codigo_ensamblador.append(f"fsub.s {destino}, {reg1}, {reg2}  # {destino} = {reg1} - {reg2}")
                
                elif token == '*':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li.s {destino}, {float(reg1) * float(reg2)}  # {destino} = {reg1} * {reg2}")
                    elif es_inmediato1:
                        codigo_ensamblador.append(f"li.s ft31, {reg1}")
                        codigo_ensamblador.append(f"fmul.s {destino}, ft31, {reg2}  # {destino} = {reg1} * {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li.s ft31, {reg2}")
                        codigo_ensamblador.append(f"fmul.s {destino}, {reg1}, ft31  # {destino} = {reg1} * {reg2}")
                    else:
                        codigo_ensamblador.append(f"fmul.s {destino}, {reg1}, {reg2}  # {destino} = {reg1} * {reg2}")
                
                elif token == '/':
                    if es_inmediato1 and es_inmediato2:
                        if float(reg2) != 0:
                            codigo_ensamblador.append(f"li.s {destino}, {float(reg1) / float(reg2)}  # {destino} = {reg1} / {reg2}")
                        else:
                            print("Error: división por cero")
                            return [], []
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li.s ft31, {reg2}")
                        codigo_ensamblador.append(f"fdiv.s {destino}, {reg1}, ft31  # {destino} = {reg1} / {reg2}")
                    else:
                        codigo_ensamblador.append(f"fdiv.s {destino}, {reg1}, {reg2}  # {destino} = {reg1} / {reg2}")
            
            else:  # integer
                # Operaciones enteras
                if token == '+':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li {destino}, {int(reg1) + int(reg2)}  # {destino} = {reg1} + {reg2}")
                    elif es_inmediato1:
                        codigo_ensamblador.append(f"addi {destino}, {reg2}, {reg1}  # {destino} = {reg2} + {reg1}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"addi {destino}, {reg1}, {reg2}  # {destino} = {reg1} + {reg2}")
                    else:
                        codigo_ensamblador.append(f"add {destino}, {reg1}, {reg2}  # {destino} = {reg1} + {reg2}")
                
                elif token == '-':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li {destino}, {int(reg1) - int(reg2)}  # {destino} = {reg1} - {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"addi {destino}, {reg1}, -{reg2}  # {destino} = {reg1} - {reg2}")
                    else:
                        codigo_ensamblador.append(f"sub {destino}, {reg1}, {reg2}  # {destino} = {reg1} - {reg2}")
                
                elif token == '*':
                    if es_inmediato1 and es_inmediato2:
                        codigo_ensamblador.append(f"li {destino}, {int(reg1) * int(reg2)}  # {destino} = {reg1} * {reg2}")
                    elif es_inmediato1:
                        codigo_ensamblador.append(f"li t6, {reg1}")
                        codigo_ensamblador.append(f"mul {destino}, t6, {reg2}  # {destino} = {reg1} * {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li t6, {reg2}")
                        codigo_ensamblador.append(f"mul {destino}, {reg1}, t6  # {destino} = {reg1} * {reg2}")
                    else:
                        codigo_ensamblador.append(f"mul {destino}, {reg1}, {reg2}  # {destino} = {reg1} * {reg2}")
                
                elif token == '/':
                    if es_inmediato1 and es_inmediato2:
                        if int(reg2) != 0:
                            codigo_ensamblador.append(f"li {destino}, {int(reg1) // int(reg2)}  # {destino} = {reg1} / {reg2}")
                        else:
                            print("Error: división por cero")
                            return [], []
                    elif es_inmediato1:
                        codigo_ensamblador.append(f"li t6, {reg1}")
                        codigo_ensamblador.append(f"div {destino}, t6, {reg2}  # {destino} = {reg1} / {reg2}")
                    elif es_inmediato2:
                        codigo_ensamblador.append(f"li t6, {reg2}")
                        codigo_ensamblador.append(f"div {destino}, {reg1}, t6  # {destino} = {reg1} / {reg2}")
                    else:
                        codigo_ensamblador.append(f"div {destino}, {reg1}, {reg2}  # {destino} = {reg1} / {reg2}")
            
            # Agregar el temporal a la pila y su registro 
            pila.append(temp_var)
            operador_actual += 1
            cont += 1
            
        else:  # es un operando
            pila.append(token)
    return codigo_intermedio, codigo_ensamblador

#Generamos código RISC-V para la instrucción read
def generar_codigo_read(variable, tabla_var): 
    codigo = []
    tipo = get_tipo_var(tabla_var, variable)
    registro = get_registro_var(tabla_var, variable)
    
    if not tipo or not registro:
        print(f"Error: variable '{variable}' no encontrada")
        return []
    
    if tipo == "integer":
        codigo.append("li a7, 5        # Syscall para Read(integer)")
        codigo.append("ecall           # Ejecutar syscall")
        codigo.append(f"mv {registro}, a0  # Mover valor leído a {variable}")
    
    elif tipo == "real":
        codigo.append("li a7, 6        # Syscall para Read(real)")
        codigo.append("ecall           # Ejecutar syscall")
        codigo.append(f"fmv.s {registro}, fa0  # Mover valor leído a {variable}")
    
    elif tipo == "char":
        codigo.append("li a7, 12       # Syscall para Read(carácter)")
        codigo.append("ecall           # Ejecutar syscall")
        codigo.append(f"mv {registro}, a0  # Mover carácter leído a {variable}")
    
    elif tipo == "string":
        codigo.append(f"la a0, buffer_{variable}  # Cargar dirección del buffer")
        codigo.append("li a1, 256      # Longitud máxima")
        codigo.append("li a7, 8        # Syscall para Read('texto')")
        codigo.append("ecall           # Ejecutar syscall")
    return codigo

#Generamos código RISC-V para write
def generar_codigo_write_mejorado(argumentos, tabla_var):
    global seccion_data
    codigo = []
    
    for i, arg in enumerate(argumentos):
        if es_cadena(arg):
            cadena = arg[1:-1]  
            label = f"str_{len(seccion_data)}"
            seccion_data.append(f'{label}: .asciiz "{cadena}"')
            
            codigo.append(f"la a0, {label}  # Cargar dirección de la cadena")
            codigo.append("li a7, 4        # Syscall para Write('texto')")
            codigo.append("ecall           # Ejecutar syscall")
        
        elif es_id(arg):
            tipo = get_tipo_var(tabla_var, arg)
            registro = get_registro_var(tabla_var, arg)
            
            if not tipo or not registro:
                print(f"Error: variable '{arg}' no encontrada")
                continue
            
            if tipo == "integer":
                codigo.append(f"mv a0, {registro}  # Cargar valor de {arg}")
                codigo.append("li a7, 1        # Syscall para Write(integer)")
                codigo.append("ecall           # Ejecutar syscall")
            
            elif tipo == "real":
                codigo.append(f"fmv.s fa0, {registro}  # Cargar valor de {arg}")
                codigo.append("li a7, 2        # Syscall para Write(real)")
                codigo.append("ecall           # Ejecutar syscall")
            
            elif tipo == "char":
                codigo.append(f"mv a0, {registro}  # Cargar valor de {arg}")
                codigo.append("li a7, 11       # Syscall para Write(carácter)")
                codigo.append("ecall           # Ejecutar syscall")
            
            elif tipo == "string":
                codigo.append(f"la a0, buffer_{arg}  # Cargar dirección de {arg}")
                codigo.append("li a7, 4        # Syscall para Write('texto')")
                codigo.append("ecall           # Ejecutar syscall")  
    return codigo

#Generamos código RISC-V para writeln
def generar_codigo_writeln_mejorado(argumentos, tabla_var):
    codigo = generar_codigo_write_mejorado(argumentos, tabla_var)
    
    # Agregar salto de línea
    codigo.append("li a0, 10       # ASCII para newline")
    codigo.append("li a7, 11       # Syscall para WriteLn(carácter)")
    codigo.append("ecall           # Ejecutar syscall")
    return codigo

def mostrar_codigo_con_correspondencia(codigo_intermedio_total, codigo_ensamblador_total):
    i_int = 0
    i_asm = 0
    
    while i_int < len(codigo_intermedio_total) or i_asm < len(codigo_ensamblador_total):
        # Mostramos el comentario de la instrucción
        if i_asm < len(codigo_ensamblador_total) and codigo_ensamblador_total[i_asm].startswith("#"):
            print(f"\n{codigo_ensamblador_total[i_asm]}")
            i_asm += 1
        
        # Mostramos el código intermedio
        if i_int < len(codigo_intermedio_total) and not codigo_intermedio_total[i_int].startswith("#"):
            if codigo_intermedio_total[i_int]:
                print(f"Código intermedio: {codigo_intermedio_total[i_int]}")
            i_int += 1
        elif i_int < len(codigo_intermedio_total):
            i_int += 1
        
        # Mostramos su traducción a RISC-V
        print("Traducción RISC-V:")
        while i_asm < len(codigo_ensamblador_total) and not codigo_ensamblador_total[i_asm].startswith("#") and codigo_ensamblador_total[i_asm]:
            print(f"  {codigo_ensamblador_total[i_asm]}")
            i_asm += 1
        # Saltamos las líneas vacías
        while i_asm < len(codigo_ensamblador_total) and codigo_ensamblador_total[i_asm] == "":
            i_asm += 1