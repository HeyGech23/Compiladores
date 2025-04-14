# main.py
import sys
from scanner import Escaner

def analizar_archivo(ruta_archivo):
    """
    Función para analizar código desde un archivo
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
        escaner = Escaner(codigo_fuente)
        tokens = escaner.escanear_tokens()
        for token in tokens:
            print(token)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

def analizar_texto(codigo_fuente):
    """
    Función para analizar código ingresado por el usuario
    """
    escaner = Escaner(codigo_fuente)
    tokens = escaner.escanear_tokens()
    for token in tokens:
        print(token)

def modo_interactivo():
    """"
    Función para ejecutar el modo interactivo donde el usuario puede ingresar texto
    """
    print("Bienvenido al Analizador Léxico - REPL")
    print("Ingresa el código para analizar (presiona Ctrl+Z y Enter para terminar):")
    
    lineas = []
    try:
        while True:
            linea = input(">> ")
            lineas.append(linea)
    except EOFError:
        # Ctrl+Z (Windows) o Ctrl+D (Unix) captado como EOFError
        print("\nFinalización de entrada detectada.")
    except KeyboardInterrupt:
        # Capturar Ctrl+C por si acaso
        print("\nOperación cancelada por el usuario.")
        return
    
    if lineas:
        codigo_fuente = "\n".join(lineas)
        print("\nResultados del análisis:")
        analizar_texto(codigo_fuente)

def principal():
    """
    Función principal
    """
    if len(sys.argv) == 1:
        # Sin argumentos, activar modo interactivo
        modo_interactivo()
    elif len(sys.argv) == 2:
        # Con un argumento, analizar archivo
        ruta_archivo = sys.argv[1]
        analizar_archivo(ruta_archivo)
    else:
        print("Uso: python main.py [nombre_del_archivo]")
        print("  - Sin argumentos: Inicia el modo interactivo")
        print("  - Con nombre de archivo: Analiza el archivo especificado")
        sys.exit(1)

if __name__ == "__main__":
    principal()
