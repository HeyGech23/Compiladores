# scanner.py
from tokens import PALABRAS_CLAVE, OPERADORES, PUNTUACION, TIPOS_TOKEN

class Escaner:
    def __init__(self, codigo_fuente):
        self.fuente = codigo_fuente
        self.tokens = []
        self.actual = 0
        self.linea = 1
        self.tiene_error = False

    def escanear_tokens(self):
        while self.actual < len(self.fuente) and not self.tiene_error:
            caracter = self.fuente[self.actual]
            
            if caracter.isspace():
                # Incrementar contador de línea para saltos de línea
                if caracter == "\n":
                    self.linea += 1
                self.actual += 1
            elif caracter == '/' and self.mirar_siguiente() == '/':
                self.saltar_comentario_linea()
            elif caracter == '/' and self.mirar_siguiente() == '*':
                self.saltar_comentario_bloque()
            elif caracter in PUNTUACION:
                self.agregar_token(PUNTUACION[caracter])
                self.actual += 1
            elif caracter.isalpha() or caracter == "_":
                self.manejar_identificador()
                self.actual += 1
            elif caracter in OPERADORES:
                self.manejar_operador()
                self.actual += 1
            elif caracter.isdigit():
                self.manejar_numero()
                self.actual += 1
            elif caracter == '"':
                self.manejar_cadena()
            else:
                self.reportar_error(f"ERROR: Caracter no válido '{caracter}' en la línea {self.linea}")
                self.actual += 1
        
        if not self.tiene_error:
            self.tokens.append("<EOF, lexema: $>")
        return self.tokens
    
    def agregar_token(self, tipo_token, lexema=None, literal=None):
        if lexema is None:
            self.tokens.append(f"<{tipo_token}, línea: {self.linea}>")
        elif literal is None:
            self.tokens.append(f"<{tipo_token}, lexema: {lexema}, línea: {self.linea}>")
        else:
            self.tokens.append(f"<{tipo_token}, lexema: {lexema}, literal: {literal}, línea: {self.linea}>")

    def reportar_error(self, mensaje):
        self.tokens.append(mensaje)
        self.tiene_error = True

    def mirar_siguiente(self):
        return self.fuente[self.actual + 1] if self.actual + 1 < len(self.fuente) else "\0"

    def avanzar(self):
        self.actual += 1
        return self.fuente[self.actual] if self.actual < len(self.fuente) else "\0"
    
    def manejar_operador(self):
        lexema = self.fuente[self.actual]
        if lexema in {"<", ">", "=", "!"} and self.mirar_siguiente() == "=":
            lexema += self.avanzar()
        elif lexema in {"+", "-"} and self.mirar_siguiente() == lexema:
            lexema += self.avanzar()
        self.agregar_token(OPERADORES.get(lexema, "OPERADOR"))
    
    def manejar_numero(self):
        inicio = self.actual
        lexema = ""
        es_decimal = False
        tiene_exponente = False
        
        # Procesar dígitos de la parte entera
        while self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
            lexema += self.fuente[self.actual]
            self.actual += 1
        
        # Procesar parte decimal si existe
        if self.actual < len(self.fuente) and self.fuente[self.actual] == '.':
            # Verificar que el siguiente caracter sea un dígito
            if self.actual + 1 < len(self.fuente) and self.fuente[self.actual + 1].isdigit():
                es_decimal = True
                lexema += self.fuente[self.actual]  # Añadir el punto
                self.actual += 1
                
                # Procesar dígitos después del punto
                while self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
                    lexema += self.fuente[self.actual]
                    self.actual += 1
        
        # Procesar notación exponencial si existe
        if self.actual < len(self.fuente) and (self.fuente[self.actual] == 'e' or self.fuente[self.actual] == 'E'):
            # Verificar que el siguiente caracter sea un dígito o un signo seguido de dígito
            if self.actual + 1 < len(self.fuente):
                siguiente = self.fuente[self.actual + 1]
                
                if siguiente.isdigit() or ((siguiente == '+' or siguiente == '-') and 
                                          self.actual + 2 < len(self.fuente) and 
                                          self.fuente[self.actual + 2].isdigit()):
                    tiene_exponente = True
                    lexema += self.fuente[self.actual]  # Añadir la 'e' o 'E'
                    self.actual += 1
                    
                    # Procesar signo del exponente si existe
                    if self.actual < len(self.fuente) and (self.fuente[self.actual] == '+' or self.fuente[self.actual] == '-'):
                        lexema += self.fuente[self.actual]
                        self.actual += 1
                    
                    # Debe haber al menos un dígito después del exponente
                    if self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
                        # Procesar dígitos del exponente
                        while self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
                            lexema += self.fuente[self.actual]
                            self.actual += 1
                    else:
                        self.reportar_error(f"ERROR: Se esperaba al menos un dígito después de 'e' en la línea {self.linea}")
                        return
        
        # Retroceder una posición para que el ciclo principal pueda avanzar correctamente
        self.actual -= 1
        
        try:
            # Convertir a valor numérico
            valor = float(lexema)
            
            # Si no tiene punto decimal ni exponente, convertir a entero
            if not es_decimal and not tiene_exponente:
                valor = int(valor)
                
            self.agregar_token("NUMERO", lexema, valor)
        except ValueError:
            self.reportar_error(f"ERROR: Número inválido '{lexema}' en la línea {self.linea}")

    def manejar_cadena(self):
        lexema = ""
        self.actual += 1  # Saltar la comilla inicial
        linea_inicio = self.linea  

        while self.actual < len(self.fuente):
            if self.fuente[self.actual] == "\n":  
                # Contar saltos de línea dentro de cadenas sin cerrar como líneas válidas
                self.linea += 1
                self.reportar_error(f"ERROR: Se detectó una cadena sin cerrar en la línea {linea_inicio}")
                self.actual += 1
                return  

            if self.fuente[self.actual] == '"':  
                self.actual += 1  # Consumir la comilla final
                self.agregar_token("CADENA", f'"{lexema}"', lexema)
                return  

            lexema += self.fuente[self.actual]
            self.actual += 1

        # Si llegamos aquí, la cadena nunca se cerró
        self.reportar_error(f"ERROR: Se detectó una cadena sin cerrar en la línea {linea_inicio}")

    def manejar_identificador(self):
        lexema = ""
        while self.actual < len(self.fuente) and (self.fuente[self.actual].isalnum() or self.fuente[self.actual] == "_"):
            lexema += self.fuente[self.actual]
            self.actual += 1
        self.actual -= 1

        if lexema in OPERADORES:
            self.agregar_token(OPERADORES[lexema])
        elif lexema in PALABRAS_CLAVE:
            self.agregar_token(PALABRAS_CLAVE[lexema])
        else:
            self.agregar_token("IDENTIFICADOR", lexema)

    def saltar_comentario_linea(self):
        # Avanzar hasta encontrar un salto de línea o EOF
        self.actual += 2  # Saltar los dos caracteres de '//'
        while self.actual < len(self.fuente):
            if self.fuente[self.actual] == "\n":
                self.linea += 1  # Incrementar el contador de líneas
                self.actual += 1
                break
            self.actual += 1

    def saltar_comentario_bloque(self):
        self.actual += 2  # Saltar los dos caracteres de '/*'
        
        while self.actual < len(self.fuente):
            if self.fuente[self.actual] == "\n":
                self.linea += 1  # Contar todas las líneas dentro del comentario
            # Verificar si encontramos el cierre del comentario
            elif self.actual + 1 < len(self.fuente) and self.fuente[self.actual] == '*' and self.fuente[self.actual + 1] == '/':
                self.actual += 2  # Consumir '*/'
                return
            self.actual += 1
            
        # Si llegamos aquí, el comentario nunca se cerró
        self.reportar_error(f"ERROR: Comentario de bloque sin cerrar")
