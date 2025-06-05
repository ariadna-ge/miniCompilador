import math
from estructuras_datos import tabla_var, codigo_intermedio_total, codigo_ensamblador_total, seccion_data, estado_for
from analisis_lexico import es_id, es_tipo, es_constante, es_cadena
from analisis_semantico import agregar_var, existe_var, set_var, get_valor, get_registro_var, get_tipo_var, evaluar_expresion
from analisis_sintactico import extraer_instrucciones_begin_end, infija_a_postfija
from generacion_codigo import codigoInterEnsambla, generar_codigo_read, generar_codigo_write_mejorado, generar_codigo_writeln_mejorado

def procesar_instruccion(tokens, tabla_var): #Manejo del for y de todas las funcionalidades del compilador
    global codigo_intermedio_total, codigo_ensamblador_total, seccion_data, estado_for

    if not tokens:
        return True
    
    if tokens[0].lower() == "begin":    # Manejo de begin 
        if len(tokens) == 1:
            # Solo 'begin'
            if estado_for.get('esperando_begin', False):
                estado_for['esperando_begin'] = False
                estado_for['dentro_bloque'] = True
                estado_for['nivel_begin'] = 1
                return True
            else:
                return True  
        else:
            resto_tokens = tokens[1:]
            # Si hay un FOR, marcar que entramos al bloque
            if estado_for.get('esperando_begin', False):
                estado_for['esperando_begin'] = False
                estado_for['dentro_bloque'] = True
                estado_for['nivel_begin'] = 1
            return procesar_instruccion(resto_tokens, tabla_var)

    # declaración de variable
    elif len(tokens) >= 4 and tokens[0].lower() == 'var' and es_id(tokens[1]) and es_tipo(tokens[2]):
        if agregar_var(tabla_var, tokens[1], tokens[2]):
            print(f'Variable {tokens[1]} declarada como {tokens[2]}')
        return True
    
    # Caso read(variable)
    elif tokens[0].lower() == 'read':
        if len(tokens) >= 4 and tokens[1] == '(' and es_id(tokens[2]) and tokens[3] == ')':
            variable = tokens[2]

            codigo_asm = generar_codigo_read(variable, tabla_var) # Generamos código RISC-V para read y lo acumulamos
            if codigo_asm:
                codigo_ensamblador_total.append(f"# read({variable})")
                codigo_ensamblador_total.extend(codigo_asm)
                codigo_ensamblador_total.append("") 
            
            leido = input(f'Input para variable {tokens[2]}: ')
            # Convertimos el valor según el tipo de la variable
            for var in tabla_var:
                if var.nombre == tokens[2]:
                    if var.tipo == 'real':
                        try:
                            leido = float(leido)
                        except ValueError:
                            print(f"Error: '{leido}' no es un número real válido")
                            return True
                    elif var.tipo == 'integer':
                        try:
                            leido = int(leido)
                        except ValueError:
                            print(f"Error: '{leido}' no es un número entero válido")
                            return True
                    break
            
            set_var(tabla_var, tokens[2], leido)
            print(f'Variable {tokens[2]} asignada con valor "{leido}"')
        else:
            print("Error en sintaxis de read. Debe ser read(<var>)")
        return True
    
    elif (len(tokens) >= 6 and tokens[0].lower() == 'for' and es_id(tokens[1]) and tokens[2] == ':=' and 'to' in tokens and 'do' in tokens):
        try:
            idx_to = tokens.index('to')
            idx_do = tokens.index('do')
        except ValueError:
            print("Error: FOR mal formado")
            return True
    
        var_loop = tokens[1]
        valor_inicio = tokens[3]
        valor_final = tokens[idx_to + 1]
    
        if not existe_var(tabla_var, var_loop):
            agregar_var(tabla_var, var_loop, 'integer')
    
        if es_constante(valor_inicio):
            set_var(tabla_var, var_loop, int(valor_inicio))
    
        reg_loop = get_registro_var(tabla_var, var_loop)

        etiqueta_inicio = f"loop_start_{len(codigo_ensamblador_total)}"
        etiqueta_fin = f"loop_end_{len(codigo_ensamblador_total)}"
    
        codigo_ensamblador_total.append(f"# for {var_loop} := {valor_inicio} to {valor_final} do")
        codigo_ensamblador_total.append(f"li {reg_loop}, {valor_inicio}  # {var_loop} := {valor_inicio}")
        codigo_ensamblador_total.append(f"{etiqueta_inicio}:")
    
        if es_constante(valor_final): 
            codigo_ensamblador_total.append(f"li t7, {valor_final}")
            codigo_ensamblador_total.append(f"bgt {reg_loop}, t7, {etiqueta_fin}  # if {var_loop} > {valor_final} goto end")
        elif existe_var(tabla_var, valor_final):
            reg_final = get_registro_var(tabla_var, valor_final)
            codigo_ensamblador_total.append(f"bgt {reg_loop}, {reg_final}, {etiqueta_fin}  # if {var_loop} > {valor_final} goto end")
    
        # Procesamos el cuerpo del bucle
        if idx_do + 1 < len(tokens):
            resto_tokens = tokens[idx_do + 1:]
        
            if resto_tokens[0].lower() == 'begin':# Extraemos las instrucciones del bloque begin/end
                instrucciones_extraidas = extraer_instrucciones_begin_end(resto_tokens)
            
                # Generar código RicV para cada instrucc. del cuerpo
                for instruccion in instrucciones_extraidas:
                    if instruccion and instruccion[0].lower() not in ['begin', 'end']:
                        if instruccion[0].lower() in ['write', 'writeln']:# Procesamos writeln dentro del FOR
                            es_writeln = instruccion[0].lower() == 'writeln'
                        
                            if instruccion[-1] == ';':
                                tokens_sin_punto_coma = instruccion[:-1]
                            else:
                                tokens_sin_punto_coma = instruccion

                            if len(tokens_sin_punto_coma) >= 3 and tokens_sin_punto_coma[1] == '(' and tokens_sin_punto_coma[-1] == ')':
                                args_tokens = tokens_sin_punto_coma[2:-1]
                                args = []
                                temp = []
                                for t in args_tokens:
                                    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                                        args.append(t)
                                    elif t == ',':
                                        if temp:
                                            args.append(' '.join(temp).strip())
                                            temp = []
                                    else:
                                        temp.append(t)
                                if temp:
                                    args.append(' '.join(temp).strip())

                                #creamos código RiscV para write y writeln
                                codigo_ensamblador_total.append(f"# {tokens[0].lower()}({', '.join(args)}) (dentro del FOR)")

                                if es_writeln:
                                    codigo_asm = generar_codigo_writeln_mejorado(args, tabla_var)
                                else:
                                    codigo_asm = generar_codigo_write_mejorado(args, tabla_var)
                            
                                if codigo_asm:
                                    codigo_ensamblador_total.extend(codigo_asm)
                    
                        # Procesar asignaciones dentro del FOR
                        elif len(instruccion) >= 4 and es_id(instruccion[0]) and instruccion[1] == ':=':
                            var_nombre = instruccion[0]
                            expresion = []
                        
                            for t in instruccion[2:]:
                                if t == ';':
                                    break
                                expresion.append(t)
                        
                            if expresion:
                                postfija = infija_a_postfija(expresion)
                                codigo_int, codigo_asm = codigoInterEnsambla(postfija, tabla_var)
                            
                                if codigo_asm:
                                    codigo_ensamblador_total.append(f"# {var_nombre} := {' '.join(expresion)} (dentro del FOR)")
                                    codigo_ensamblador_total.extend(codigo_asm)
                                
                                    reg_var = get_registro_var(tabla_var, var_nombre)
                                    tipo_var = get_tipo_var(tabla_var, var_nombre)
                                
                                    if reg_var and codigo_asm:
                                        ultimo_destino = None
                                        for linea in reversed(codigo_asm):
                                            partes = linea.split()
                                            if partes and partes[0] in ['add', 'sub', 'mul', 'div', 'addi', 'li', 
                                                                     'fadd.s', 'fsub.s', 'fmul.s', 'fdiv.s', 'li.s']:
                                                ultimo_destino = partes[1].rstrip(',')
                                                break
                                    
                                        if ultimo_destino and ultimo_destino != reg_var:
                                            if tipo_var == "real":
                                                codigo_ensamblador_total.append(f"fmv.s {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
                                            else:
                                                codigo_ensamblador_total.append(f"mv {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
            
                # Se ejecuta la simulación 
                if es_constante(valor_inicio) and (es_constante(valor_final) or existe_var(tabla_var, valor_final)):
                    inicio_val = int(valor_inicio)
                    if es_constante(valor_final):
                        final_val = int(valor_final)
                    else:
                        final_val = get_valor(tabla_var, valor_final)
                        if final_val is None:
                            print(f"Error: variable {valor_final} no tiene valor")
                            return True
                        final_val = int(final_val)
                
                    print(f"\nSimulando for {var_loop} desde {inicio_val} hasta {final_val}:")
                    for i in range(inicio_val, final_val + 1):
                        set_var(tabla_var, var_loop, i)
                    
                        for instruccion in instrucciones_extraidas:
                            if instruccion and instruccion[0].lower() not in ['begin', 'end']:
                                procesar_instruccion_sin_for(instruccion, tabla_var)
            
            else:
                # Una sola instrucción sin begin/end
                if resto_tokens[0].lower() in ['write', 'writeln']:
                    es_writeln = resto_tokens[0].lower() == 'writeln'
                
                    if resto_tokens[-1] == ';':
                        tokens_sin_punto_coma = resto_tokens[:-1]
                    else:
                        tokens_sin_punto_coma = resto_tokens

                    if len(tokens_sin_punto_coma) >= 3 and tokens_sin_punto_coma[1] == '(' and tokens_sin_punto_coma[-1] == ')':
                        args_tokens = tokens_sin_punto_coma[2:-1]
                        args = []
                        temp = []
                        for t in args_tokens:
                            if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                                args.append(t)
                            elif t == ',':
                                if temp:
                                    args.append(' '.join(temp).strip())
                                    temp = []
                            else:
                                temp.append(t)
                        if temp:
                            args.append(' '.join(temp).strip())

                        if es_writeln:
                            codigo_asm = generar_codigo_writeln_mejorado(args, tabla_var)
                        else:
                            codigo_asm = generar_codigo_write_mejorado(args, tabla_var)
                    
                        if codigo_asm:
                            codigo_ensamblador_total.extend(codigo_asm)
            
                #instrucción simple
                if es_constante(valor_inicio) and (es_constante(valor_final) or existe_var(tabla_var, valor_final)):
                    inicio_val = int(valor_inicio)
                    if es_constante(valor_final):
                        final_val = int(valor_final)
                    else:
                        final_val = get_valor(tabla_var, valor_final)
                        if final_val is None:
                            print(f"Error: variable {valor_final} no tiene valor")
                            return True
                        final_val = int(final_val)
                
                    print(f"\nSimulando for {var_loop} desde {inicio_val} hasta {final_val}:")
                    for i in range(inicio_val, final_val + 1):
                       set_var(tabla_var, var_loop, i)
                       print(f"  Iteración {i}: {var_loop} = {i}")
                       procesar_instruccion_sin_for(resto_tokens, tabla_var)
        # fin del bucle
        codigo_ensamblador_total.append(f"addi {reg_loop}, {reg_loop}, 1  # {var_loop}++")
        codigo_ensamblador_total.append(f"j {etiqueta_inicio}  # jump to loop start")
        codigo_ensamblador_total.append(f"{etiqueta_fin}:")
        codigo_ensamblador_total.append("")
        return True

    # si estamos dentro de un bloque FOR, acumulamos instrucciones sin ejecutarlas
    elif (estado_for.get('dentro_bloque', False) and 
          not tokens[0].lower() in ['begin', 'end']):
        estado_for['instrucciones_cuerpo'].append(tokens)
        
        if len(tokens) >= 4 and es_id(tokens[0]) and tokens[1] == ':=':# Generamos código ensamblador
            var_nombre = tokens[0]
            expresion = []
            
            for t in tokens[2:]:
                if t == ';':
                    break
                expresion.append(t)
            
            if expresion:
                postfija = infija_a_postfija(expresion)
                codigo_int, codigo_asm = codigoInterEnsambla(postfija, tabla_var)
                
                if codigo_int:
                    codigo_intermedio_total.extend(codigo_int)
                
                if codigo_asm:
                    codigo_ensamblador_total.append(f"# {var_nombre} := {' '.join(expresion)} (dentro del FOR)")
                    codigo_ensamblador_total.extend(codigo_asm)
                    
                    reg_var = get_registro_var(tabla_var, var_nombre)
                    tipo_var = get_tipo_var(tabla_var, var_nombre)

                    if reg_var and codigo_asm:
                        ultimo_destino = None
                        for linea in reversed(codigo_asm):
                            partes = linea.split()
                            if partes and partes[0] in ['add', 'sub', 'mul', 'div', 'addi', 'li', 
                                                         'fadd.s', 'fsub.s', 'fmul.s', 'fdiv.s', 'li.s']:
                                ultimo_destino = partes[1].rstrip(',')
                                break
                        
                        if ultimo_destino and ultimo_destino != reg_var:
                            if tipo_var == "real":
                                codigo_ensamblador_total.append(f"fmv.s {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
                            else:
                                codigo_ensamblador_total.append(f"mv {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
                    
                    codigo_ensamblador_total.append("")
        
        # Manejo de write y writeln dentro del FOR
        elif tokens[0].lower() in ['write', 'writeln']:
            es_writeln = tokens[0].lower() == 'writeln'

            if tokens[-1] == ';':
                tokens_sin_punto_coma = tokens[:-1]
            else:
                tokens_sin_punto_coma = tokens

            if len(tokens_sin_punto_coma) >= 3 and tokens_sin_punto_coma[1] == '(' and tokens_sin_punto_coma[-1] == ')':
                args_tokens = tokens_sin_punto_coma[2:-1]
                args = []
                temp = []
                for t in args_tokens:
                    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                        args.append(t)
                    elif t == ',':
                        if temp:
                            args.append(' '.join(temp).strip())
                            temp = []
                    else:
                        temp.append(t)
                if temp:
                    args.append(' '.join(temp).strip())

                codigo_ensamblador_total.append(f"# {tokens_sin_punto_coma[0].lower()}({', '.join(args)}) (dentro del FOR)")
                
                if es_writeln:
                    codigo_asm = generar_codigo_writeln_mejorado(args, tabla_var)
                else:
                    codigo_asm = generar_codigo_write_mejorado(args, tabla_var)
                
                if codigo_asm:
                    codigo_ensamblador_total.extend(codigo_asm)
                    codigo_ensamblador_total.append("")
        return True

    # caso end del FOR 
    elif (len(tokens) >= 1 and tokens[0].lower() == 'end' and 
          estado_for.get('activo', False)):
        
        if estado_for.get('dentro_bloque', False):
            estado_for['nivel_begin'] -= 1
            
            if estado_for['nivel_begin'] <= 0:
                # ejecutamos con todas las instrucciones acumuladas
                var_loop = estado_for['variable']
                valor_inicio = estado_for['valor_inicial']
                valor_final = estado_for['valor_final']
                
                # Determinar valores de inicio y final
                if es_constante(valor_inicio) and (es_constante(valor_final) or existe_var(tabla_var, valor_final)):
                    inicio_val = int(valor_inicio)
                    if es_constante(valor_final):
                        final_val = int(valor_final)
                    else:
                        final_val = get_valor(tabla_var, valor_final)
                        if final_val is None:
                            print(f"Error: variable {valor_final} no tiene valor")
                            return True
                        final_val = int(final_val)
                    
                    # ejecutamos la simulación del FOR
                    print(f"\nSimulando for {var_loop} desde {inicio_val} hasta {final_val}:")
                    for i in range(inicio_val, final_val + 1):
                        set_var(tabla_var, var_loop, i)
                        print(f"  Iteración {i}: {var_loop} = {i}")
                        
                        # Ejecutamos la instrucción del cuerpo
                        for instruccion in estado_for['instrucciones_cuerpo']:
                            if instruccion:
                                procesar_instruccion_sin_for(instruccion, tabla_var)
                
                # Generamos código del fin del FOR
                codigo_ensamblador_total.append(f"addi {estado_for['registro']}, {estado_for['registro']}, 1  # {estado_for['variable']}++")
                codigo_ensamblador_total.append(f"j {estado_for['etiqueta_inicio']}  # jump to loop start")
                codigo_ensamblador_total.append(f"{estado_for['etiqueta_fin']}:")
                codigo_ensamblador_total.append("")
                estado_for = {'activo': False}
        return True
    
    # manejo del Write o WriteLn (fuera del FOR)
    elif tokens[0].lower() in ['write', 'writeln']:
        es_writeln = tokens[0].lower() == 'writeln'

        if tokens[-1] == ';':
            tokens = tokens[:-1]

        if len(tokens) >= 3 and tokens[1] == '(' and tokens[-1] == ')':
            args_tokens = tokens[2:-1]
            args = []
            temp = []
            for t in args_tokens:
                if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                    args.append(t)
                elif t == ',':
                    if temp:
                        args.append(' '.join(temp).strip())
                        temp = []
                else:
                    temp.append(t)
            if temp:
                args.append(' '.join(temp).strip())

            codigo_ensamblador_total.append(f"# {tokens[0].lower()}({', '.join(args)})")
            
            if es_writeln:
                codigo_asm = generar_codigo_writeln_mejorado(args, tabla_var)
            else:
                codigo_asm = generar_codigo_write_mejorado(args, tabla_var)
            
            if codigo_asm:
                codigo_ensamblador_total.extend(codigo_asm)
                codigo_ensamblador_total.append("")  

            salida = ''
            for arg in args:
                arg = arg.strip()
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    salida += arg[1:-1]
                elif es_id(arg):
                    valor = get_valor(tabla_var, arg)
                    if valor is not None:
                        salida += str(valor)
                    else:
                        print(f'Error: variable "{arg}" no tiene valor asignado o no existe.')
                        salida += f'<{arg}>'
                else:
                    salida += arg

            if tokens[0].lower() == "write":
                print(salida, end="")
            elif tokens[0].lower() == "writeln":
                print(salida)
        else:
            print("Error en sintaxis de Write/WriteLn")
        return True

    #asignación(fuera del FOR)
    elif len(tokens) >= 4 and es_id(tokens[0]) and tokens[1] == ':=':
        var_nombre = tokens[0]
        expresion = []

        for t in tokens[2:]:# Tomamos todos los tokens desde después del := hasta el ;
            if t == ';':
                break
            expresion.append(t)
        # Detectar sin(), cos(), tan()
        if (tokens[2].lower() in ["sin", "cos", "tan"] 
            and tokens[3] == '(' and tokens[-2] == ')' and tokens[-1] == ';'):
    
            func = tokens[2].lower()
            expr_tokens = tokens[4:-2] 
            #Convertir a postfija
            postfija = infija_a_postfija(expr_tokens)

            #evaluamos expresión 
            codigo_int, codigo_asm = codigoInterEnsambla(postfija, tabla_var)
            if codigo_int:
                codigo_intermedio_total.append(f"# {tokens[0]} := {func}({''.join(expr_tokens)})")
                codigo_intermedio_total.extend(codigo_int)
                codigo_intermedio_total.append("")

            if codigo_asm:
                codigo_ensamblador_total.append(f"# {tokens[0]} := {func}({''.join(expr_tokens)})")
                codigo_ensamblador_total.extend(codigo_asm)

                # Detectar el último registro
                ultimo_destino = None
                for linea in reversed(codigo_asm):
                    partes = linea.split()
                    if partes and partes[0] in ['fadd.s', 'fsub.s', 'fmul.s', 'fdiv.s', 'li.s']:
                        ultimo_destino = partes[1].rstrip(',')
                        break
                #pasar argumento a fa0 y llamar a la función
                if ultimo_destino:
                    codigo_ensamblador_total.append(f"fmv.s fa0, {ultimo_destino}  # pasar arg a fa0")
                    codigo_ensamblador_total.append(f"call {func}                # llamar a {func}")
                # movemos el resultado a la variable 
                    var_dest = tokens[0]
                    reg_dest = get_registro_var(tabla_var, var_dest)
                    if reg_dest:
                        codigo_ensamblador_total.append(f"fmv.s {reg_dest}, fa0     # guardar resultado en {var_dest}")
                        valor_expr = evaluar_expresion(expr_tokens, tabla_var)
                        if valor_expr is not None:
                            if func == "sin":
                                resultado = math.sin(valor_expr)
                            elif func == "cos":
                                resultado = math.cos(valor_expr)
                            elif func == "tan":
                                resultado = math.tan(valor_expr)
                            else:
                                resultado = None

                            set_var(tabla_var, var_dest, resultado)
                            print(f'Variable {var_dest} asignada con valor {resultado}')
                        else:
                            set_var(tabla_var, var_dest, "ERROR")
                            print(f'Error al evaluar expresión para {var_dest}')

                codigo_ensamblador_total.append("")
            return True

        if expresion:
            postfija = infija_a_postfija(expresion)
            print(f'Expresión: {var_nombre} := {expresion}')
            codigo_int, codigo_asm = codigoInterEnsambla(postfija, tabla_var)
            
            if codigo_int:
                codigo_intermedio_total.append(f"# {var_nombre} := {' '.join(expresion)}")
                codigo_intermedio_total.extend(codigo_int)
                codigo_intermedio_total.append("")
            
            if codigo_asm:
                codigo_ensamblador_total.append(f"# {var_nombre} := {' '.join(expresion)}")
                codigo_ensamblador_total.extend(codigo_asm)
                reg_var = get_registro_var(tabla_var, var_nombre)
                tipo_var = get_tipo_var(tabla_var, var_nombre)
                
                if reg_var and codigo_asm:
                    # Encontrar el último registro usado
                    ultimo_destino = None
                    for linea in reversed(codigo_asm):
                        partes = linea.split()
                        if partes and partes[0] in ['add', 'sub', 'mul', 'div', 'addi', 'li', 
                                                     'fadd.s', 'fsub.s', 'fmul.s', 'fdiv.s', 'li.s']:
                            ultimo_destino = partes[1].rstrip(',')
                            break
                    
                    if ultimo_destino and ultimo_destino != reg_var:
                        if tipo_var == "real":
                            codigo_ensamblador_total.append(f"fmv.s {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
                        else:
                            codigo_ensamblador_total.append(f"mv {reg_var}, {ultimo_destino}  # {var_nombre} = resultado")
                
                codigo_ensamblador_total.append("")  
            # Evaluamos la expresión
            valor = evaluar_expresion(expresion, tabla_var)
            if valor is not None:
                set_var(tabla_var, var_nombre, valor)
                print(f'Variable {var_nombre} asignada con valor {valor}')
            else:
                set_var(tabla_var, var_nombre, "ERROR")
                print(f'Error al evaluar expresión para {var_nombre}')
        return True

    # Caso end;  
    elif len(tokens) == 2 and tokens[0].lower() == 'end' and tokens[1] == ';':
        return False
    elif len(tokens) == 1 and tokens[0].lower() == 'end.':
        return False
    else:
        return True


# procesamos instrucciones durante la simulación del FOR 
def procesar_instruccion_sin_for(tokens, tabla_var):
    if not tokens:
        return True
    
    # Manejo de asignaciones
    if len(tokens) >= 4 and es_id(tokens[0]) and tokens[1] == ':=':
        var_nombre = tokens[0]
        expresion = []
        
        for t in tokens[2:]:
            if t == ';':
                break
            expresion.append(t)
        
        if expresion:
            for token in expresion:# Mostramos los valores actuales de las variables
                if es_id(token):
                    valor_actual = get_valor(tabla_var, token)
            
            valor = evaluar_expresion(expresion, tabla_var)
            if valor is not None:
                valor_anterior = get_valor(tabla_var, var_nombre) # Verificar valor antes de asignar
                exito = set_var(tabla_var, var_nombre, valor)
                valor_nuevo = get_valor(tabla_var, var_nombre) # Verificar valor después de asignar
                if not exito:
                    print(f'ERROR: No se pudo asignar valor a {var_nombre}')
            else:
                print(f'ERROR: Error al evaluar expresión para {var_nombre}')
    
    # Manejo de write y writeln
    elif tokens[0].lower() in ['write', 'writeln']:
        es_writeln = tokens[0].lower() == 'writeln'

        if tokens[-1] == ';':
            tokens_sin_punto_coma = tokens[:-1]
        else:
            tokens_sin_punto_coma = tokens

        if len(tokens_sin_punto_coma) >= 3 and tokens_sin_punto_coma[1] == '(' and tokens_sin_punto_coma[-1] == ')':
            args_tokens = tokens_sin_punto_coma[2:-1]
            args = []
            temp = []
            for t in args_tokens:
                if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                    args.append(t)
                elif t == ',':
                    if temp:
                        args.append(' '.join(temp).strip())
                        temp = []
                else:
                    temp.append(t)
            if temp:
                args.append(' '.join(temp).strip())

            salida = ''
            for arg in args:
                arg = arg.strip()
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    salida += arg[1:-1]
                elif es_id(arg):
                    valor = get_valor(tabla_var, arg)
                    if valor is not None:
                        salida += str(valor)
                    else:
                        salida += f'<{arg}>'
                else:
                    salida += arg
            if es_writeln:
                print(salida)
            else:
                print(salida, end="")
    return True


def simular_for(var_loop, inicio, final, instrucciones_cuerpo, tabla_var):
    for i in range(inicio, final + 1):
        set_var(tabla_var, var_loop, i)
        print(f"  Iteración {i}: {var_loop} = {i}")
        
        for instruccion in instrucciones_cuerpo:
            if instruccion:
                
                if isinstance(instruccion, list):# Si es una lista de tokens, la procesamos como instrucción
                    procesar_instruccion_sin_for(instruccion, tabla_var)
                # Si es una cadena, la dividimos en tokens
                else:
                    tokens_instr = instruccion.split()
                    if tokens_instr:
                        procesar_instruccion_sin_for(tokens_instr, tabla_var)
