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
        
        # Colores Cyberpunk mejorados
        self.colores = {
            "verde": "\033[38;2;0;255;255m",      # Cyan neón
            "rojo": "\033[38;2;255;0;100m",       # Rosa neón
            "naranja": "\033[38;2;255;165;0m",    # Naranja neón
            "azul": "\033[38;2;0;150;255m",       # Azul neón
            "morado": "\033[38;2;150;0;255m",     # Púrpura neón
            "cyan": "\033[38;2;0;255;200m",       # Verde azulado
            "negrita": "\033[1m",
            "reset": "\033[0m",
            "fondo": "\033[48;2;10;10;30m",       # Fondo oscuro con azul
            "amarillo": "\033[38;2;255;255;0m",   # Amarillo neón
            "rosa": "\033[38;2;255;0;255m",       # Rosa fuerte
            "blanco": "\033[38;2;220;220;255m"    # Blanco azulado
        }
        
        self.bordes = {
            "sup": "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄",
            "inf": "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
            "lat": "▌",
            "der": "▐"
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

    def guardar_archivo(self, contrasena, nombre_archivo, fecha=None):
        """Guarda la contraseña en un archivo de texto con formato"""
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
        
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print(f"{self.colores['verde']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {self.colores['verde']}✓ ARCHIVO GUARDADO EXITOSAMENTE: {self.colores['blanco']}{nombre_archivo:<45}║")
            print(f"{self.colores['verde']}╚═══════════════════════════════════════════════════════════════════════╝{self.colores['reset']}")
            return True
        except Exception as e:
            print(f"{self.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {self.colores['rojo']}✗ ERROR: {str(e):<60}║")
            print(f"{self.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{self.colores['reset']}")
            return False

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas detalladas de la contraseña con estilo cyberpunk"""
        stats = self.analizar_fortaleza(contrasena)
        
        # Barra de progreso cyberpunk
        bar_len = 20
        filled = int((stats['porcentaje'] / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"\n{self.colores['morado']}╔═══════════════════════════════════════════════════════════════════════╗")
        print(f"║ {self.colores['verde']}███ {self.colores['rosa']}ESTADÍSTICAS DE SEGURIDAD {self.colores['verde']}███{self.colores['blanco']}{' ' * 36}║")
        print(f"{self.colores['morado']}╠═══════════════════════════════════════════════════════════════════════╣")
        print(f"║ {self.colores['azul']}🔑 Longitud: {self.colores['blanco']}{str(stats['longitud'])+' caracteres':<31} {self.colores['azul']}🔢 Números: {self.colores['blanco']}{str(stats['digitos']):<8} ║")
        print(f"║ {self.colores['verde']}⬆ Mayúsculas: {self.colores['blanco']}{str(stats['mayusculas']):<27} {self.colores['azul']}⬇ Minúsculas: {self.colores['blanco']}{str(stats['minusculas']):<8} ║")
        print(f"║ {self.colores['amarillo']}✨ Símbolos: {self.colores['blanco']}{str(stats['simbolos']):<30} {self.colores['azul']}🎯 Total: {self.colores['blanco']}{str(stats['longitud']):<12} ║")
        print(f"{self.colores['morado']}╠═══════════════════════════════════════════════════════════════════════╣")
        print(f"║ {self.colores['verde']}NIVEL: {stats['color']}{stats['nivel']}{self.colores['reset']}{' ' * (43 - len(stats['nivel']))}║")
        print(f"║ {self.colores['verde']}BARRA DE SEGURIDAD: [{self.colores['verde']}{bar}{self.colores['reset']}] {stats['porcentaje']:>3}% ║")
        print(f"{self.colores['morado']}╚═══════════════════════════════════════════════════════════════════════╝{self.colores['reset']}")

    def mostrar_historial(self, archivo="historial.txt"):
        """Muestra el historial de contraseñas guardadas con estilo cyberpunk"""
        if not os.path.exists(archivo):
            print(f"{self.colores['amarillo']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {self.colores['amarillo']}⚠  NO HAY HISTORIAL DISPONIBLE{self.colores['reset']}{' ' * 32}║")
            print(f"{self.colores['amarillo']}╚═══════════════════════════════════════════════════════════════════════╝{self.colores['reset']}")
            return
        
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                print(f"\n{self.colores['morado']}╔═══════════════════════════════════════════════════════════════════════╗")
                print(f"║ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}HISTORIAL DE CONTRASEÑAS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['blanco']}{' ' * 37}║")
                print(f"{self.colores['morado']}╚═══════════════════════════════════════════════════════════════════════╝")
                print(f"{self.colores['blanco']}{contenido}{self.colores['reset']}")
        except Exception as e:
            print(f"{self.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {self.colores['rojo']}✗ ERROR AL LEER HISTORIAL: {str(e):<39}║")
            print(f"{self.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{self.colores['reset']}")

def mostrar_banner():
    """Muestra un banner cyberpunk"""
    banner = f"""
{'\033[38;2;0;255;255m'}╔═══════════════════════════════════════════════════════════════════════╗
║ {'\033[38;2;255;0;100m'}██████╗ {'\033[38;2;150;0;255m'}██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ {'\033[38;2;0;255;255m'}║
║ {'\033[38;2;255;0;100m'}██╔══██╗{'\033[38;2;150;0;255m'}╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗{'\033[38;2;0;255;255m'}║
║ {'\033[38;2;255;0;100m'}██████╔╝{'\033[38;2;150;0;255m'} ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝{'\033[38;2;0;255;255m'}║
║ {'\033[38;2;255;0;100m'}██╔═══╝ {'\033[38;2;150;0;255m'}  ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗{'\033[38;2;0;255;255m'}║
║ {'\033[38;2;255;0;100m'}██║     {'\033[38;2;150;0;255m'}   ██║   ██║     ██║  ██║███████╗██║  ██║{'\033[38;2;0;255;255m'}║
║ {'\033[38;2;255;0;100m'}╚═╝     {'\033[38;2;150;0;255m'}   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{'\033[38;2;0;255;255m'}║
║        {'\033[38;2;0;255;200m'}★ GENERADOR DE CONTRASEÑAS SEGURAS ★{'\033[38;2;0;255;255m'}        ║
║  {'\033[38;2;255;165;0m'}⚡ ¡La seguridad en la era digital empieza aquí! ⚡{'\033[38;2;0;255;255m'}  ║
╚═══════════════════════════════════════════════════════════════════════╝
{'\033[0m'}"""
    return banner

def main():
    """Función principal del programa"""
    generador = GeneradorContrasenasCLI()
    
    print(generador.colores["fondo"] + mostrar_banner() + generador.colores["reset"])
    
    while True:
        print(f"\n{generador.colores['morado']}╔═══════════════════════════════════════════════════════════════════════╗")
        print(f"║ {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█ {generador.colores['blanco']}MENÚ PRINCIPAL {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█{generador.colores['blanco']}{' ' * 42}║")
        print(f"{generador.colores['morado']}╠═══════════════════════════════════════════════════════════════════════╣")
        print(f"║ {generador.colores['verde']}[1]{generador.colores['blanco']}  ⚡ Generar nueva contraseña{' ' * 44}║")
        print(f"║ {generador.colores['amarillo']}[2]{generador.colores['blanco']}  💾 Guardar contraseña en archivo{' ' * 39}║")
        print(f"║ {generador.colores['azul']}[3]{generador.colores['blanco']}  📜 Ver historial{' ' * 48}║")
        print(f"║ {generador.colores['rojo']}[4]{generador.colores['blanco']}  🚪 Salir{' ' * 56}║")
        print(f"{generador.colores['morado']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
        
        opcion = input(f"\n{generador.colores['rosa']}┌─ {generador.colores['verde']}➤ {generador.colores['blanco']}Selecciona una opción: {generador.colores['reset']}").strip()
        
        if opcion == "1":
            try:
                print(f"{generador.colores['azul']}┌─ {generador.colores['blanco']}Longitud de contraseña [8-20, Enter = 12]{generador.colores['reset']}")
                longitud = input(f"{generador.colores['rosa']}└─ {generador.colores['verde']}➤ {generador.colores['reset']}") or "12"
                longitud = int(longitud)
                
                if 8 <= longitud <= 20:
                    contrasena = generador.generar_contrasena(longitud)
                    
                    print(f"\n{generador.colores['verde']}╔═══════════════════════════════════════════════════════════════════════╗")
                    print(f"║ {generador.colores['verde']}★ {generador.colores['rosa']}CONTRASEÑA GENERADA {generador.colores['verde']}★{generador.colores['blanco']}{' ' * 41}║")
                    print(f"║ {generador.colores['blanco']}🔑 {generador.colores['verde']}{contrasena}{' ' * (49 - len(contrasena))}║")
                    print(f"{generador.colores['verde']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
                    
                    generador.mostrar_estadisticas(contrasena)
                    
                    try:
                        import subprocess
                        subprocess.run(['xclip', '-selection', 'clipboard'], input=contrasena.encode(), check=True)
                        print(f"{generador.colores['verde']}╔═══════════════════════════════════════════════════════════════════════╗")
                        print(f"║ {generador.colores['verde']}✓ COPIADA AL PORTAPAPELES{generador.colores['blanco']}{' ' * 40}║")
                        print(f"{generador.colores['verde']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
                    except:
                        pass
                    
                    guardar = input(f"\n{generador.colores['azul']}┌─ {generador.colores['blanco']}¿Guardar esta contraseña? (s/n): {generador.colores['reset']}").lower()
                    if guardar == 's':
                        nombre = input(f"{generador.colores['azul']}└─ {generador.colores['blanco']}Nombre del archivo: {generador.colores['reset']}").strip()
                        if nombre:
                            generador.guardar_archivo(contrasena, nombre)
                else:
                    print(f"{generador.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
                    print(f"║ {generador.colores['rojo']}✗ ERROR: La longitud debe estar entre 8 y 20{generador.colores['blanco']}{' ' * 15}║")
                    print(f"{generador.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
            except ValueError:
                print(f"{generador.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
                print(f"║ {generador.colores['rojo']}✗ ERROR: Ingresa un número válido{generador.colores['blanco']}{' ' * 31}║")
                print(f"{generador.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
        
        elif opcion == "2":
            contrasena = input(f"{generador.colores['azul']}┌─ {generador.colores['blanco']}Ingresa la contraseña a guardar: {generador.colores['reset']}").strip()
            if not contrasena:
                print(f"{generador.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
                print(f"║ {generador.colores['rojo']}✗ ERROR: La contraseña no puede estar vacía{generador.colores['blanco']}{' ' * 23}║")
                print(f"{generador.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
                continue
            
            nombre = input(f"{generador.colores['azul']}└─ {generador.colores['blanco']}Nombre del archivo: {generador.colores['reset']}").strip()
            if nombre:
                generador.guardar_archivo(contrasena, nombre)
            else:
                print(f"{generador.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
                print(f"║ {generador.colores['rojo']}✗ ERROR: El nombre no puede estar vacío{generador.colores['blanco']}{' ' * 27}║")
                print(f"{generador.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
        
        elif opcion == "3":
            generador.mostrar_historial()
        
        elif opcion == "4":
            print(f"\n{generador.colores['verde']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {generador.colores['verde']}👋 ¡HASTA LUEGO! {generador.colores['blanco']}Mantén tus contraseñas seguras 🔒{generador.colores['verde']}{' ' * 16}║")
            print(f"{generador.colores['verde']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")
            break
        
        else:
            print(f"{generador.colores['rojo']}╔═══════════════════════════════════════════════════════════════════════╗")
            print(f"║ {generador.colores['rojo']}✗ OPCIÓN NO VÁLIDA{generador.colores['blanco']}{' ' * 48}║")
            print(f"{generador.colores['rojo']}╚═══════════════════════════════════════════════════════════════════════╝{generador.colores['reset']}")

if __name__ == "__main__":
    main()
