# 💫 Mini Compilador Pascal 💫
## Descripción del Proyecto
Este proyecto implementa un compilador simplificado para un subconjunto del lenguaje Pascal. Abarca las etapas fundamentales de un proceso de compilación. Como salida, el sistema produce la tabla de símbolos, el código intermedio y el código ensamblador RISC-V.

## Archivos 🗂️

### estructuras_datos.py

- Clase Variable
- Definición de registros RISC-V
- Variables globales del compilador
- Función `reset_registros()`

### analisis_lexico.py

- Funciones de clasificación de tokens
- Función `tokenizar()` que elimina comentarios y genera tokens
- Función `get_etiqueta()` para clasificar tokens
- Validación de sintaxis básica (punto y coma)

### analisis_sintactico.py

- Conversión de infija a postfija
- Conversión de infija a prefija
- Extracción de instrucciones begin/end
- División de tokens en instrucciones

### analisis_semantico.py

- Gestión de la tabla de variables
- Asignación y liberación de registros
- Evaluación de expresiones
- Funciones de acceso a variables

### generacion_codigo.py

- Generación de código intermedio y RISC-V
- Funciones para read, write, writeln
- Procesamiento de expresiones aritméticas
- Visualización de correspondencia de código

### procesamiento_instrucciones.py

- Función principal `procesar_instruccion()`
- Manejo de bucles FOR
- Procesamiento de asignaciones
- Manejo de funciones trigonométricas
- Simulación de ejecución

### compilador_principal.py

- Función `compilar_archivo()` que orquesta todo el proceso
- Manejo de archivos
- Salida formateada de resultados
- Punto de entrada del programa

### MiniCompilador.pdf
Se anexa un **[documento📄](https://github.com/ariadna-ge/miniCompilador/blob/ceaea5f340eb8c387da20937c964dadac34bc386/documento/MiniCompilador.pdf)** que contiene diversas pruebas sobre el funcionamiento del compilador, así como una breve descripción de cada parte del código.

## Colaboradoras 👩🏼‍💻
El proyecto fue realizado para la materia de **_Compiladores_** en la Facultad de Estudios Superiores Aragón durante el semestre **2025-II**.

🎀 Ariadna Denisse García Estrada **([ariadna-ge](https://github.com/ariadna-ge))**  
🎀 Alexandra Galilea González Arias **([Galilea44](https://github.com/Galilea44))**
