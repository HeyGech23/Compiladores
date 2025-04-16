import sys
import difflib

# Palabras clave, operadores y puntuación
PALABRAS_CLAVE = {
    "else": "SINO", "fun": "FUNCION", "print": "IMPRIMIR", "var": "VARIABLE",
    "false": "FALSO", "true": "VERDADERO", "return": "RETORNO",
    "while": "MIENTRAS", "if": "SI", "for": "PARA", "null": "NULO",
    "and": "Y", "or": "O"
}

OPERADORES = {"+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!=", "=", "!"}
PUNTUACION = {"(", ")", "{", "}", ";", ","}

TIPOS_TOKEN = {
    "NUMERO": "NUMERO",
    "CADENA": "CADENA",
    "IDENTIFICADOR": "IDENTIFICADOR",
    "EOF": "EOF",
}


class Escaner:
    def __init__(self, codigo_fuente):
        self.fuente = codigo_fuente
        self.tokens = []
        self.actual = 0
        self.linea = 1
        self.pila_parentesis = []  # Para verificar balance de paréntesis

    def escanear_tokens(self):
        """
        Escanea el código fuente y devuelve la lista de tokens.
        Si hay errores, los reporta de inmediato.
        """
        while self.actual < len(self.fuente):
            caracter = self.fuente[self.actual]

            if caracter.isspace():
                if caracter == "\n":
                    self.linea += 1
                self.actual += 1

            elif caracter == "/" and self.siguiente_es("/"):
                self.saltar_comentario_linea()

            elif caracter == "/" and self.siguiente_es("*"):
                self.saltar_comentario_bloque()

            elif caracter in OPERADORES:
                self.manejar_operador()

            elif caracter in PUNTUACION:
                self.manejar_puntuacion(caracter)

            elif caracter == '"':
                self.manejar_cadena()

            elif caracter.isdigit():
                self.manejar_numero()

            elif caracter.isalpha() or caracter == "_":
                self.manejar_identificador()

            else:
                self.reportar_error(f"Carácter inesperado '{caracter}'.")
                self.actual += 1

        # Si hay paréntesis no balanceados, arrojar un error
        if self.pila_parentesis:
            linea_error = self.pila_parentesis[-1]  # La línea del paréntesis que no se cerró
            raise SyntaxError(f"Error sintáctico en la línea {linea_error}. Se esperaba ')' pero no se encontró.")

        self.agregar_token("EOF")
        return self.tokens

    def manejar_puntuacion(self, caracter):
        """
        Maneja puntuación y verifica paréntesis balanceados.
        """
        if caracter == "(":
            self.pila_parentesis.append(self.linea)  # Registra la línea del paréntesis abierto
        elif caracter == ")":
            if not self.pila_parentesis:
                raise SyntaxError(f"Error sintáctico en la línea {self.linea}. Se encontró ')' sin un '(' correspondiente.")
            self.pila_parentesis.pop()  # Elimina el paréntesis correctamente balanceado

        self.agregar_token(caracter)
        self.actual += 1

    def manejar_identificador(self):
        """
        Maneja palabras clave, identificadores y detecta errores sintácticos en palabras clave mal escritas.
        """
        inicio = self.actual
        while self.actual < len(self.fuente) and (self.fuente[self.actual].isalnum() or self.fuente[self.actual] == "_"):
            self.actual += 1
        lexema = self.fuente[inicio:self.actual]

        if lexema in PALABRAS_CLAVE:
            self.agregar_token(PALABRAS_CLAVE[lexema])
        else:
            # Verificar si es similar a alguna palabra clave conocida
            sugerencias = difflib.get_close_matches(lexema, PALABRAS_CLAVE.keys(), n=1, cutoff=0.8)
            if sugerencias:
                sugerencia = sugerencias[0]
                raise SyntaxError(f"Error sintáctico en la línea {self.linea}. Se esperaba '{sugerencia}' pero se encontró '{lexema}'.")
            else:
                self.agregar_token("IDENTIFICADOR", lexema)

    def manejar_operador(self):
        if self.actual + 1 < len(self.fuente):  # Verifica si hay un carácter siguiente.
            combinacion = self.fuente[self.actual:self.actual + 2]
            if combinacion in OPERADORES:
                self.agregar_token(combinacion)
                self.actual += 2
                return
        if self.fuente[self.actual] in OPERADORES:
            self.agregar_token(self.fuente[self.actual])
        self.actual += 1

    def manejar_cadena(self):
        inicio = self.actual + 1
        self.actual += 1

        while self.actual < len(self.fuente) and self.fuente[self.actual] != '"':
            if self.fuente[self.actual] == "\n":
                self.linea += 1
            self.actual += 1

        if self.actual >= len(self.fuente):  # Si llega al final sin encontrar el cierre.
            raise SyntaxError(f"Error sintáctico en la línea {self.linea}. Se esperaba '\"'.")
        else:
            self.actual += 1
            valor = self.fuente[inicio:self.actual - 1]
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
        """Verifica si el siguiente carácter coincide con el esperado."""
        return self.actual + 1 < len(self.fuente) and self.fuente[self.actual + 1] == esperado

    def peek_proximo(self):
        """Devuelve el carácter después del siguiente (para números decimales)."""
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
        raise SyntaxError(f"Error sintáctico en la línea {self.linea}. Se esperaba '*/' para cerrar el bloque.")

    def agregar_token(self, tipo, literal=None):
        texto = self.fuente[self.actual - 1] if self.actual > 0 else ""
        self.tokens.append({"tipo": tipo, "lexema": texto, "literal": literal, "linea": self.linea})


def analizar_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()

        escaner = Escaner(codigo_fuente)
        escaner.escanear_tokens()

        # Ningún error: el código es válido.
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
