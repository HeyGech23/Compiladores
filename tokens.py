# constants.py
# Definir palabras clave, operadores y símbolos con nombres específicos en español

PALABRAS_CLAVE = {
    "else": "SINO", "fun": "FUNCION", "print": "IMPRIMIR", "var": "VARIABLE",
    "false": "FALSO", "if": "SI", "return": "RETORNO", "while": "MIENTRAS",
    "for": "PARA", "null": "NULO", "true": "VERDADERO"
}

OPERADORES = {
    "+": "MAS", "-": "MENOS", "*": "ASTERISCO", "/": "DIVISION",
    "<": "MENOR", "<=": "MENOR_IGUAL", ">": "MAYOR", ">=": "MAYOR_IGUAL",
    "==": "IGUAL_IGUAL", "!=": "DISTINTO", "and": "Y", "or": "O",
    "=": "IGUAL", "!": "NEGACION", "++": "INCREMENTO", "--": "DECREMENTO"
}

PUNTUACION = {"(": "PARENTESIS_IZQ", ")": "PARENTESIS_DER", ",": "COMA", ";": "PUNTO_COMA", 
              "{": "LLAVE_IZQ", "}": "LLAVE_DER"}

TIPOS_TOKEN = {
    "IDENTIFIER": "IDENTIFICADOR",
    "NUMBER": "NUMERO",
    "STRING": "CADENA",
    "BOOLEAN": "BOOLEANO",
    "NULL": "NULO",
    "EOF": "EOF",
    "ERROR": "ERROR"
}

