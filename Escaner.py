import sys
import difflib
from gramatica import PALABRAS_CLAVE, PUNTUACION, OPERADORES, TIPOS_TOKEN

class Escaner:
    def __init__(self, codigo_fuente):
        self.fuente = codigo_fuente
        self.tokens = []
        self.actual = 0
        self.linea = 1
        self.pila_parentesis = []  # Para balance de paréntesis y llaves

    def verificar_cabecera_for(self):
        # Saltar espacios
        while self.actual < len(self.fuente) and self.fuente[self.actual].isspace():
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1

        if self.actual >= len(self.fuente) or self.fuente[self.actual] != '(':
            raise SyntaxError(f"Error sintáctico en la línea {self.linea}: se esperaba '(' después de 'for'.")

        self.actual += 1  # Saltar '('

        contenido = ""
        profundidad = 1

        while self.actual < len(self.fuente) and profundidad > 0:
            c = self.fuente[self.actual]
            if c == "(":
                profundidad += 1
            elif c == ")":
                profundidad -= 1
                if profundidad == 0:
                    break
            if profundidad > 0:
                contenido += c
            if c == "\n":
                self.linea += 1
            self.actual += 1

        if profundidad != 0:
            raise SyntaxError(f"Error sintáctico en la línea {self.linea}: se esperaba ')' en la cabecera del for.")

        n_puntosycoma = contenido.count(";")
        if n_puntosycoma != 2:
            raise SyntaxError(
                f"Error sintáctico en la línea {self.linea}: la cabecera del for debe tener 2 ';', pero tiene {n_puntosycoma}. Cabecera: ({contenido.strip()})"
            )
        self.actual += 1  # Saltar ')'

    def verificar_parametros_funcion(self):
        # Saltar espacios en blanco
        while self.actual < len(self.fuente) and self.fuente[self.actual].isspace():
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1

        # Leer nombre de la función (identificador)
        inicio_nombre = self.actual
        while self.actual < len(self.fuente) and (
                self.fuente[self.actual].isalnum() or self.fuente[self.actual] == "_"):
            self.actual += 1
        nombre_funcion = self.fuente[inicio_nombre:self.actual].strip()
        if not nombre_funcion:
            raise SyntaxError(
                f"Error sintáctico en la línea {self.linea}: falta el nombre de la función después de 'fun'.")

        # Saltar espacios en blanco otra vez
        while self.actual < len(self.fuente) and self.fuente[self.actual].isspace():
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1

        # Debe aparecer un '('
        if self.actual >= len(self.fuente) or self.fuente[self.actual] != '(':
            raise SyntaxError(
                f"Error sintáctico en la línea {self.linea}: se esperaba '(' después del nombre de la función '{nombre_funcion}'.")

        self.actual += 1  # Saltar '('

        parametros = ''
        profundidad = 1
        while self.actual < len(self.fuente) and profundidad > 0:
            c = self.fuente[self.actual]
            if c == '(':
                profundidad += 1
            elif c == ')':
                profundidad -= 1
                if profundidad == 0:
                    if parametros.rstrip().endswith(','):
                        raise SyntaxError(
                            f"Error sintáctico en la línea {self.linea}: no debe haber una coma antes de ')'. Parámetros: ({parametros.strip()})"
                        )
                    break
            if profundidad > 0:
                parametros += c
            if c == '\n':
                self.linea += 1
            self.actual += 1

        if profundidad != 0:
            raise SyntaxError(f"Error sintáctico en la línea {self.linea}: se esperaba ')' en parámetros de función.")
        self.actual += 1  # Saltar ')'

        # Saltar espacios antes de la llave
        while self.actual < len(self.fuente) and self.fuente[self.actual].isspace():
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1

        # Debe aparecer una llave de apertura
        if self.actual >= len(self.fuente) or self.fuente[self.actual] != "{":
            raise SyntaxError(
                f"Error sintáctico en la línea {self.linea}: se esperaba '{{' después de los parámetros de la función '{nombre_funcion}'."
            )
        self.actual += 1  # Saltar '{'
        inicio_cuerpo = self.actual
        profundidad_llave = 1

        while self.actual < len(self.fuente) and profundidad_llave > 0:
            c = self.fuente[self.actual]
            if c == "{":
                profundidad_llave += 1
            elif c == "}":
                profundidad_llave -= 1
                if profundidad_llave == 0:
                    # Verifica que haya algo entre las llaves (con contenido real)
                    cuerpo = self.fuente[inicio_cuerpo:self.actual]
                    if not any(not x.isspace() for x in cuerpo):
                        raise SyntaxError(
                            f"Error sintáctico en la línea {self.linea}: el cuerpo de la función '{nombre_funcion}' está vacío."
                        )
                    break
            if c == '\n':
                self.linea += 1
            self.actual += 1

        if profundidad_llave != 0:
            raise SyntaxError(
                f"Error sintáctico en la línea {self.linea}: se esperaba '}}' para cerrar el cuerpo de la función '{nombre_funcion}'.")
        self.actual += 1  # Saltar '}'

    def escanear_tokens(self):
        while self.actual < len(self.fuente):
            caracter = self.fuente[self.actual]

            if caracter.isspace():
                # Si es un espacio en blanco, salta a la siguiente posición
                if caracter == "\n":
                    self.linea += 1
                self.actual += 1
            elif self.siguiente_es("//"):  # Comentarios de una sola línea
                self.saltar_comentario_linea()
            elif self.siguiente_es("/*"):  # Comentarios de bloque
                self.saltar_comentario_bloque()
            elif caracter.isalpha() or caracter == "_":  # Identificadores (funciones, variables)
                self.manejar_identificador()
            elif caracter in PUNTUACION:  # Manejo de puntuaciones (paréntesis, llaves, etc.)
                self.manejar_puntuacion(caracter)
                self.actual += 1
            elif caracter == '"' or caracter == "'":  # Cadenas
                self.manejar_cadena(caracter)
            elif caracter.isdigit():  # Números
                self.manejar_numero()
            else:
                # Si el carácter no es reconocido, avanzamos un paso
                self.actual += 1

        # Verifica si hay paréntesis o llaves que no se han cerrado
        if self.pila_parentesis:
            char, linea = self.pila_parentesis[-1]
            lexema = self.fuente[self.actual - 1] if self.actual > 0 else "fin de archivo"
            if char == "{":
                raise SyntaxError(
                    f"Error sintáctico en la línea {linea}: Se esperaba '}}' pero se encontró '{lexema}'.")
            elif char == "(":
                raise SyntaxError(f"Error sintáctico en la línea {linea}: Se esperaba ')' pero se encontró '{lexema}'.")

    def manejar_identificador(self):
        inicio = self.actual
        while self.actual < len(self.fuente) and (
                self.fuente[self.actual].isalnum() or self.fuente[self.actual] == "_"):
            self.actual += 1
        lexema = self.fuente[inicio:self.actual]

        if lexema in PALABRAS_CLAVE:
            if lexema == "fun":
                # Solo agregar el token si toda la definición es válida
                try:
                    self.verificar_parametros_funcion()
                    self.agregar_token(PALABRAS_CLAVE[lexema], lexema)
                except SyntaxError as e:
                    raise e
            else:
                self.agregar_token(PALABRAS_CLAVE[lexema], lexema)
        else:
            sugerencias = difflib.get_close_matches(lexema, PALABRAS_CLAVE.keys(), n=1, cutoff=0.8)
            if sugerencias:
                sugerencia = sugerencias[0]
                raise SyntaxError(
                    f"Error sintáctico en la línea {self.linea}. Se esperaba '{sugerencia}' pero se encontró '{lexema}'.")
            else:
                self.agregar_token("IDENTIFICADOR", lexema)

    def manejar_puntuacion(self, caracter):
        if caracter in "({":
            self.pila_parentesis.append((caracter, self.linea))
        elif caracter == ")":
            if not self.pila_parentesis or self.pila_parentesis[-1][0] != "(":
                raise SyntaxError(f"Error sintáctico en la línea {self.linea}: Se encontró ')' sin un '(' correspondiente.")
            self.pila_parentesis.pop()
        elif caracter == "}":
            if not self.pila_parentesis or self.pila_parentesis[-1][0] != "{":
                raise SyntaxError(f"Error sintáctico en la línea {self.linea}: Se encontró '}}' sin un '{{' correspondiente.")
            self.pila_parentesis.pop()
        self.agregar_token(caracter)

    def manejar_cadena(self, delimitador):
        self.actual += 1
        inicio = self.actual
        while self.actual < len(self.fuente) and self.fuente[self.actual] != delimitador:
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1
        if self.actual >= len(self.fuente):
            raise SyntaxError(f"Error sintáctico en la línea {self.linea}: cadena no cerrada.")
        valor = self.fuente[inicio:self.actual]
        self.actual += 1  # Saltar delimitador de cierre
        self.agregar_token("CADENA", valor)

    def manejar_numero(self):
        inicio = self.actual
        while self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
            self.actual += 1
        if self.actual < len(self.fuente) and self.fuente[self.actual] == "." and self.peek_proximo().isdigit():
            self.actual += 1
            while self.actual < len(self.fuente) and self.fuente[self.actual].isdigit():
                self.actual += 1
        valor = self.fuente[inicio:self.actual]
        self.agregar_token("NUMERO", float(valor))

    def siguiente_es(self, esperado):
        return self.actual + 1 < len(self.fuente) and self.fuente[self.actual + 1] == esperado

    def peek_proximo(self):
        if self.actual + 1 < len(self.fuente):
            return self.fuente[self.actual + 1]
        return "\0"

    def saltar_comentario_linea(self):
        while self.actual < len(self.fuente) and self.fuente[self.actual] != "\n":
            self.actual += 1

    def saltar_comentario_bloque(self):
        self.actual += 2
        while self.actual < len(self.fuente) - 1:
            if self.fuente[self.actual] == "*" and self.siguiente_es("/"):
                self.actual += 2
                return
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1
        raise SyntaxError(f"Error sintáctico en la línea {self.linea}: se esperaba '*/' para cerrar el bloque.")

    def agregar_token(self, tipo, literal=None):
        lexema = literal if literal is not None else self.fuente[self.actual - 1]
        self.tokens.append({
            "tipo": tipo,
            "lexema": lexema,
            "literal": literal,
            "linea": self.linea
        })

    def reportar_error(self, param):
        pass

def analizar_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
        escaner = Escaner(codigo_fuente)
        escaner.escanear_tokens()
        print("Código válido")
    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        analizar_archivo(sys.argv[1])
    else:
        print("Uso: python Escaner.py [nombre_del_archivo]")

