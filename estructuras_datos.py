import math
import re

class Variable:
    def __init__(self, nombre, tipo, valor, registro):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor 
        self.registro = registro 

# Registros disponibles
registros_real = [f"ft{i}" for i in range(32)]
registros_int = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"]
registros_char = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
registros_string = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]

# Variables globales
memoria_spill = []
tabla_var = []
codigo_intermedio_total = []
codigo_ensamblador_total = []
seccion_data = []  # para las cadenas 
estado_for = {'activo': False} # variable para el estado del FOR

def reset_registros(): #reiniciamos los registros
    global registros_real, registros_int, registros_char, registros_string, memoria_spill, tabla_var, estado_for
    registros_real = [f"ft{i}" for i in range(32)]
    registros_int = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"]
    registros_char = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
    registros_string = ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"]
    memoria_spill = []
    tabla_var = []
    estado_for = {'activo': False}