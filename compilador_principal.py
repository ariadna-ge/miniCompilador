from estructuras_datos import reset_registros, tabla_var, codigo_intermedio_total, codigo_ensamblador_total, seccion_data
from analisis_lexico import tokenizar, get_etiqueta
from analisis_sintactico import dividir_en_instrucciones
from analisis_semantico import imprime_tabla_var
from procesamiento_instrucciones import procesar_instruccion

def compilar_archivo(ruta_archivo):
    global codigo_intermedio_total, codigo_ensamblador_total, seccion_data
    # Reiniciar variables
    codigo_intermedio_total = []
    codigo_ensamblador_total = []
    seccion_data = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            texto = archivo.read()
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{ruta_archivo}'")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    reset_registros()
    print("--------------------------------- ANÁLISIS LÉXICO ---------------------------------")
    tokens = tokenizar(texto)
    print("\nTokens encontrados:")
    for token in tokens:
        etiqueta = get_etiqueta(token)
        print(f"{token} -> {etiqueta}")
    print("\n--------------------------------- ANÁLISIS SINTÁCTICO Y EJECUCIÓN ---------------------------------")
    
    instrucciones = dividir_en_instrucciones(tokens)
    for i, instruccion in enumerate(instrucciones):# Procesamos cada instrucción
        if instruccion:  # ignoramos instrucciones vacías
            print(f"\nProcesando instrucción {i+1}: {' '.join(instruccion)}")
            if not procesar_instruccion(instruccion, tabla_var):
                print("Programa terminado.")
                break
    print("\n--------------------------------- TABLA FINAL DE VARIABLES ---------------------------------")
    imprime_tabla_var(tabla_var)

    if codigo_intermedio_total:
        print("\n--------------------------------- CÓDIGO INTERMEDIO ---------------------------------")
        for linea in codigo_intermedio_total:
            if linea.startswith("#"):
                print(linea)
            elif linea:
                print(f"  {linea}")
            else:
                print()

    if codigo_ensamblador_total or seccion_data:
        print("\n--------------------------------- CÓDIGO ENSAMBLADOR RISC-V ---------------------------------")
        if seccion_data:
            print(".data")
            for dato in seccion_data:
                print(f"  {dato}")
            print("\n.text")
            print(".globl main")
            print("main:")
        else:
            print(".text")
            print(".globl main")
            print("main:")
        
        for linea in codigo_ensamblador_total:
            if linea.startswith("# ") and not linea.startswith("# Operación"):
                print(f"\n{linea}")
            elif not linea.startswith("#"):
                if linea:
                    print(f"  {linea}")
                else:
                    print()
        # Código de salida
        print("\n  # Exit")
        print("  li a7, 10       # Syscall para exit")
        print("  ecall           # Ejecutar syscall")

if __name__ == "__main__":
    compilar_archivo('archivosPascal/expresiones.pas')
    compilar_archivo('archivosPascal/for.pas')
    compilar_archivo('archivosPascal/main.pas')