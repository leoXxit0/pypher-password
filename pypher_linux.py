import random
import string
import re
from datetime import datetime
import os
import subprocess

class GeneradorContrasenasCLI:
    def __init__(self):
        self.caracteres_seguros = "!@#$%&()-_=+[]{}?"
        self.caracteres_completos = string.ascii_letters + string.digits + self.caracteres_seguros
        
        # Colores Cyberpunk
        self.colores = {
            "verde": "\033[38;2;0;255;200m",
            "rojo": "\033[38;2;255;0;100m",
            "naranja": "\033[38;2;255;165;0m",
            "azul": "\033[38;2;0;150;255m",
            "morado": "\033[38;2;150;0;255m",
            "cyan": "\033[38;2;0;255;255m",
            "negrita": "\033[1m",
            "reset": "\033[0m",
            "amarillo": "\033[38;2;255;255;0m",
            "rosa": "\033[38;2;255;0;255m",
            "blanco": "\033[38;2;220;220;255m",
            "gris": "\033[38;2;150;150;170m"
        }
        
        # Obtener la ruta de la carpeta Documentos
        self.documentos_path = self._obtener_ruta_documentos()

    def _obtener_ruta_documentos(self):
        """Obtiene la ruta de la carpeta Documentos del usuario"""
        home = os.path.expanduser("~")
        
        # Intentar con nombres comunes en diferentes idiomas
        posibles_nombres = ["Documentos", "Documents", "My Documents"]
        
        for nombre in posibles_nombres:
            ruta = os.path.join(home, nombre)
            if os.path.exists(ruta):
                return ruta
        
        # Si no existe ninguna, crear la carpeta en español
        ruta_es = os.path.join(home, "Documentos")
        if not os.path.exists(ruta_es):
            try:
                os.makedirs(ruta_es)
                print(f"{self.colores['verde']}│ ✓ Carpeta Documentos creada en: {ruta_es}{self.colores['reset']}")
            except:
                # Si falla, usar el directorio actual
                return "."
        return ruta_es

    def guardar_archivo(self, contrasena, nombre_archivo, fecha=None, subcarpeta=None):
        """Guarda la contraseña en un archivo de texto con formato en la carpeta Documentos"""
        if fecha is None:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        stats = self.analizar_fortaleza(contrasena)
        
        contenido = f"""╔═══════════════════════════════════════════════════════════════════════╗
║                     🐍 PYPHER - REGISTRO DE CONTRASEÑA                      ║
║                      ───────────────────────────                             ║
║  Fecha de creación : {fecha:<43} ║
║  Contraseña        : {contrasena:<43} ║
║  Longitud          : {str(stats['longitud'])+' caracteres':<43} ║
║  Mayúsculas        : {str(stats['mayusculas']):<43} ║
║  Minúsculas        : {str(stats['minusculas']):<43} ║
║  Números           : {str(stats['digitos']):<43} ║
║  Símbolos          : {str(stats['simbolos']):<43} ║
║  Fortaleza         : {stats['nivel'] + ' (' + str(stats['porcentaje']) + '%)':<43} ║
║  Caracteres usados : Letras + Números + !@#$%&()-_=+[]{{}}?                  ║
╚═══════════════════════════════════════════════════════════════════════╝
╔═══════════════════════════════════════════════════════════════════════╗
║  🔒 Recomendación: Guarda esta contraseña en un lugar seguro.       ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
        
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        
        # Construir la ruta completa
        if subcarpeta:
            ruta_carpeta = os.path.join(self.documentos_path, subcarpeta)
            # Crear subcarpeta si no existe
            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)
        else:
            ruta_carpeta = self.documentos_path
        
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        
        try:
            with open(ruta_completa, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            
            print(f"{self.colores['verde']}│ ✓ Archivo guardado en: {self.colores['blanco']}{ruta_completa}{self.colores['reset']}")
            return True
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al guardar: {str(e)}{self.colores['reset']}")
            return False

    def mostrar_historial(self, archivo="historial.txt", subcarpeta=None):
        """Muestra el historial de contraseñas guardadas desde la carpeta Documentos"""
        if subcarpeta:
            ruta_archivo = os.path.join(self.documentos_path, subcarpeta, archivo)
        else:
            ruta_archivo = os.path.join(self.documentos_path, archivo)
        
        if not os.path.exists(ruta_archivo):
            print(f"{self.colores['naranja']}│ ⚠ No hay historial disponible en: {ruta_archivo}{self.colores['reset']}")
            return
        
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}HISTORIAL DE CONTRASEÑAS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
                print(f"{self.colores['morado']}│{self.colores['reset']}")
                print(contenido)
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al leer historial: {str(e)}{self.colores['reset']}")

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
            color = self.colores["amarillo"]
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

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas detalladas de la contraseña"""
        stats = self.analizar_fortaleza(contrasena)
        
        # Barra de progreso
        bar_len = 20
        filled = int((stats['porcentaje'] / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"\n{self.colores['morado']}│ {self.colores['verde']}███ {self.colores['rosa']}ESTADÍSTICAS DE SEGURIDAD {self.colores['verde']}███{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}Longitud:  {self.colores['blanco']}{stats['longitud']:>3} caracteres")
        print(f"{self.colores['morado']}│ {self.colores['verde']}Mayúsculas:{self.colores['blanco']}{stats['mayusculas']:>3}")
        print(f"{self.colores['morado']}│ {self.colores['verde']}Minúsculas:{self.colores['blanco']}{stats['minusculas']:>3}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}Números:   {self.colores['blanco']}{stats['digitos']:>3}")
        print(f"{self.colores['morado']}│ {self.colores['amarillo']}Símbolos:  {self.colores['blanco']}{stats['simbolos']:>3}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['negrita']}Fortaleza: {stats['color']}{stats['nivel']} ({stats['porcentaje']}%){self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['gris']}[{self.colores['verde']}{bar}{self.colores['gris']}] {stats['porcentaje']:>3}%{self.colores['reset']}")

def main():
    """Función principal del programa"""
    generador = GeneradorContrasenasCLI()
    
    # Banner
    print(f"""
{generador.colores['cyan']}╔═══════════════════════════════════════════════════════════════════════╗
║ {generador.colores['rosa']}██████╗ {generador.colores['morado']}██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ {generador.colores['cyan']}║
║ {generador.colores['rosa']}██╔══██╗{generador.colores['morado']}╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗{generador.colores['cyan']}║
║ {generador.colores['rosa']}██████╔╝{generador.colores['morado']} ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝{generador.colores['cyan']}║
║ {generador.colores['rosa']}██╔═══╝ {generador.colores['morado']}  ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗{generador.colores['cyan']}║
║ {generador.colores['rosa']}██║     {generador.colores['morado']}   ██║   ██║     ██║  ██║███████╗██║  ██║{generador.colores['cyan']}║
║ {generador.colores['rosa']}╚═╝     {generador.colores['morado']}   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{generador.colores['cyan']}║
║        {generador.colores['verde']}★ GENERADOR DE CONTRASEÑAS SEGURAS ★{generador.colores['cyan']}        ║
║  {generador.colores['amarillo']}⚡ ¡La seguridad en la era digital empieza aquí! ⚡{generador.colores['cyan']}  ║
║  {generador.colores['azul']}📁 Archivos guardados en: {generador.documentos_path}{generador.colores['cyan']:<22} ║
╚═══════════════════════════════════════════════════════════════════════╝
{generador.colores['reset']}""")
    
    while True:
        print(f"\n{generador.colores['morado']}│ {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█ {generador.colores['blanco']}MENÚ PRINCIPAL {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█{generador.colores['reset']}")
        print(f"{generador.colores['morado']}│{generador.colores['reset']}")
        print(f"{generador.colores['morado']}│ {generador.colores['verde']}[1]{generador.colores['blanco']}  ⚡ Generar nueva contraseña")
        print(f"{generador.colores['morado']}│ {generador.colores['amarillo']}[2]{generador.colores['blanco']}  💾 Guardar contraseña en archivo")
        print(f"{generador.colores['morado']}│ {generador.colores['azul']}[3]{generador.colores['blanco']}  📜 Ver historial")
        print(f"{generador.colores['morado']}│ {generador.colores['rojo']}[4]{generador.colores['blanco']}  🚪 Salir")
        print(f"{generador.colores['morado']}│{generador.colores['reset']}")
        
        opcion = input(f"{generador.colores['morado']}│ {generador.colores['verde']}➤ {generador.colores['blanco']}Selecciona una opción: {generador.colores['reset']}").strip()
        
        if opcion == "1":
            try:
                print(f"{generador.colores['morado']}│ {generador.colores['azul']}Longitud de contraseña [8-20, Enter = 12]{generador.colores['reset']}")
                longitud = input(f"{generador.colores['morado']}│ {generador.colores['verde']}➤ {generador.colores['reset']}") or "12"
                longitud = int(longitud)
                
                if 8 <= longitud <= 20:
                    contrasena = generador.generar_contrasena(longitud)
                    
                    print(f"\n{generador.colores['morado']}│ {generador.colores['verde']}★ {generador.colores['rosa']}CONTRASEÑA GENERADA {generador.colores['verde']}★{generador.colores['reset']}")
                    print(f"{generador.colores['morado']}│{generador.colores['reset']}")
                    print(f"{generador.colores['morado']}│ {generador.colores['verde']}🔑 {generador.colores['negrita']}{contrasena}{generador.colores['reset']}")
                    
                    generador.mostrar_estadisticas(contrasena)
                    
                    try:
                        subprocess.run(['xclip', '-selection', 'clipboard'], input=contrasena.encode(), check=True)
                        print(f"{generador.colores['verde']}│ ✓ Copiada al portapapeles{generador.colores['reset']}")
                    except:
                        pass
                    
                    guardar = input(f"\n{generador.colores['morado']}│ {generador.colores['azul']}¿Guardar esta contraseña? (s/n): {generador.colores['reset']}").lower()
                    if guardar == 's':
                        nombre = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Nombre del archivo: {generador.colores['reset']}").strip()
                        if nombre:
                            # Preguntar si quiere una subcarpeta
                            subcarpeta = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Subcarpeta (opcional, Enter para omitir): {generador.colores['reset']}").strip()
                            generador.guardar_archivo(contrasena, nombre, subcarpeta=subcarpeta if subcarpeta else None)
                else:
                    print(f"{generador.colores['rojo']}│ ✗ La longitud debe estar entre 8 y 20{generador.colores['reset']}")
            except ValueError:
                print(f"{generador.colores['rojo']}│ ✗ Ingresa un número válido{generador.colores['reset']}")
        
        elif opcion == "2":
            contrasena = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Ingresa la contraseña a guardar: {generador.colores['reset']}").strip()
            if not contrasena:
                print(f"{generador.colores['rojo']}│ ✗ La contraseña no puede estar vacía{generador.colores['reset']}")
                continue
            
            nombre = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Nombre del archivo: {generador.colores['reset']}").strip()
            if nombre:
                subcarpeta = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Subcarpeta (opcional, Enter para omitir): {generador.colores['reset']}").strip()
                generador.guardar_archivo(contrasena, nombre, subcarpeta=subcarpeta if subcarpeta else None)
            else:
                print(f"{generador.colores['rojo']}│ ✗ El nombre no puede estar vacío{generador.colores['reset']}")
        
        elif opcion == "3":
            subcarpeta = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Subcarpeta del historial (opcional, Enter para omitir): {generador.colores['reset']}").strip()
            generador.mostrar_historial(subcarpeta=subcarpeta if subcarpeta else None)
        
        elif opcion == "4":
            print(f"\n{generador.colores['verde']}│ 👋 ¡Hasta luego! Mantén tus contraseñas seguras 🔒{generador.colores['reset']}")
            break
        
        else:
            print(f"{generador.colores['rojo']}│ ✗ Opción no válida{generador.colores['reset']}")

if __name__ == "__main__":
    main()
