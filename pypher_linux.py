import random
import string
import re
from datetime import datetime
import os

class GeneradorContrasenasCLI:
    def __init__(self):
        self.caracteres_seguros = "!@#$%&()-_=+[]{}?"
        self.caracteres_completos = string.ascii_letters + string.digits + self.caracteres_seguros
        self.colores = {
            "verde": "\033[92m",
            "rojo": "\033[91m",
            "naranja": "\033[93m",
            "azul": "\033[94m",
            "morado": "\033[95m",
            "cyan": "\033[96m",
            "negrita": "\033[1m",
            "reset": "\033[0m"
        }

    def generar_contrasena(self, longitud=12):
        """Genera una contraseña aleatoria con la longitud especificada"""
        return ''.join(random.choice(self.caracteres_completos) for _ in range(longitud))

    def analizar_fortaleza(self, contrasena):
        """Analiza la fortaleza de la contraseña y devuelve métricas"""
        longitud = len(contrasena)
        mayus = sum(1 for c in contrasena if c.isupper())
        minus = sum(1 for c in contrasena if c.islower())
        digitos = sum(1 for c in contrasena if c.isdigit())
        simbolos = longitud - mayus - minus - digitos
        
        # Cálculo de puntaje
        puntaje = 0
        if longitud >= 8: puntaje += 1
        if longitud >= 12: puntaje += 1
        if longitud >= 16: puntaje += 1
        if mayus > 0: puntaje += 1
        if minus > 0: puntaje += 1
        if digitos > 0: puntaje += 1
        if simbolos > 0: puntaje += 1
        
        max_puntaje = 8
        porcentaje = int((puntaje / max_puntaje) * 100)
        
        if porcentaje >= 80:
            nivel = "FUERTE"
            color = self.colores["verde"]
        elif porcentaje >= 60:
            nivel = "MEDIA"
            color = self.colores["naranja"]
        else:
            nivel = "DÉBIL"
            color = self.colores["rojo"]
        
        return {
            "longitud": longitud,
            "mayusculas": mayus,
            "minusculas": minus,
            "digitos": digitos,
            "simbolos": simbolos,
            "porcentaje": porcentaje,
            "nivel": nivel,
            "color": color
        }

    def guardar_archivo(self, contrasena, nombre_archivo, fecha=None):
        """Guarda la contraseña en un archivo de texto con formato"""
        if fecha is None:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        stats = self.analizar_fortaleza(contrasena)
        
        contenido = f"""==================================================
              🐍 PYPHER - REGISTRO DE CONTRASEÑA
==================================================
Fecha de creación : {fecha}
Contraseña        : {contrasena}
Longitud          : {stats['longitud']} caracteres
Mayúsculas        : {stats['mayusculas']}
Minúsculas        : {stats['minusculas']}
Números           : {stats['digitos']}
Símbolos          : {stats['simbolos']}
Fortaleza         : {stats['nivel']} ({stats['porcentaje']}%)
Caracteres usados : Letras + Números + !@#$%&()-_=+[]{{}}?
==================================================
Recomendación: Guarda esta contraseña en un lugar seguro.
"""
        
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print(f"{self.colores['verde']}✓ Archivo guardado: {nombre_archivo}{self.colores['reset']}")
            return True
        except Exception as e:
            print(f"{self.colores['rojo']}✗ Error al guardar: {str(e)}{self.colores['reset']}")
            return False

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas detalladas de la contraseña"""
        stats = self.analizar_fortaleza(contrasena)
        
        print(f"\n{self.colores['negrita']}📊 Estadísticas de la contraseña:{self.colores['reset']}")
        print(f"  Longitud: {stats['longitud']} caracteres")
        print(f"  Mayúsculas: {stats['mayusculas']}")
        print(f"  Minúsculas: {stats['minusculas']}")
        print(f"  Números: {stats['digitos']}")
        print(f"  Símbolos: {stats['simbolos']}")
        print(f"  {self.colores['negrita']}Fortaleza: {stats['color']}{stats['nivel']} ({stats['porcentaje']}%){self.colores['reset']}")

    def mostrar_historial(self, archivo="historial.txt"):
        """Muestra el historial de contraseñas guardadas"""
        if not os.path.exists(archivo):
            print(f"{self.colores['naranja']}⚠ No hay historial disponible{self.colores['reset']}")
            return
        
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                print(f"\n{self.colores['negrita']}📜 Historial de contraseñas:{self.colores['reset']}")
                print(contenido)
        except Exception as e:
            print(f"{self.colores['rojo']}✗ Error al leer historial: {str(e)}{self.colores['reset']}")

def main():
    """Función principal del programa"""
    generador = GeneradorContrasenasCLI()
    
    print(f"""
{generador.colores['negrita']}{generador.colores['cyan']}🐍 PYPHER - Generador de Contraseñas Seguras{generador.colores['reset']}
{generador.colores['azul']}================================================{generador.colores['reset']}
""")
    
    while True:
        print(f"\n{generador.colores['negrita']}📌 Menú principal:{generador.colores['reset']}")
        print("  1. Generar nueva contraseña")
        print("  2. Guardar contraseña en archivo")
        print("  3. Ver historial")
        print("  4. Salir")
        
        opcion = input(f"\n{generador.colores['azul']}➤ Selecciona una opción: {generador.colores['reset']}").strip()
        
        if opcion == "1":
            # Generar contraseña
            try:
                longitud = int(input(f"  Longitud de contraseña [8-20, default 12]: ") or "12")
                if 8 <= longitud <= 20:
                    contrasena = generador.generar_contrasena(longitud)
                    print(f"\n{generador.colores['verde']}🔑 Contraseña generada: {generador.colores['negrita']}{contrasena}{generador.colores['reset']}")
                    generador.mostrar_estadisticas(contrasena)
                    
                    # Copiar al portapapeles (solo en sistemas con xclip)
                    try:
                        import subprocess
                        subprocess.run(['xclip', '-selection', 'clipboard'], input=contrasena.encode(), check=True)
                        print(f"{generador.colores['verde']}✓ Copiada al portapapeles{generador.colores['reset']}")
                    except:
                        pass  # Si no hay xclip, simplemente no copia
                    
                    # Preguntar si guardar
                    guardar = input(f"\n{generador.colores['azul']}¿Guardar esta contraseña? (s/n): {generador.colores['reset']}").lower()
                    if guardar == 's':
                        nombre = input("  Nombre del archivo: ").strip()
                        if nombre:
                            generador.guardar_archivo(contrasena, nombre)
                else:
                    print(f"{generador.colores['rojo']}✗ La longitud debe estar entre 8 y 20{generador.colores['reset']}")
            except ValueError:
                print(f"{generador.colores['rojo']}✗ Ingresa un número válido{generador.colores['reset']}")
        
        elif opcion == "2":
            # Guardar contraseña manual
            contrasena = input("  Ingresa la contraseña a guardar: ").strip()
            if not contrasena:
                print(f"{generador.colores['rojo']}✗ La contraseña no puede estar vacía{generador.colores['reset']}")
                continue
            
            nombre = input("  Nombre del archivo: ").strip()
            if nombre:
                generador.guardar_archivo(contrasena, nombre)
            else:
                print(f"{generador.colores['rojo']}✗ El nombre no puede estar vacío{generador.colores['reset']}")
        
        elif opcion == "3":
            generador.mostrar_historial()
        
        elif opcion == "4":
            print(f"{generador.colores['verde']}👋 ¡Hasta luego!{generador.colores['reset']}")
            break
        
        else:
            print(f"{generador.colores['rojo']}✗ Opción no válida{generador.colores['reset']}")

if __name__ == "__main__":
    main()