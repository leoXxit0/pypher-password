#!/usr/bin/env python3
"""
🐍 PYPHER - CYBERPUNK EDITION (VERSIÓN ESTABLE)
Generador de contraseñas con estética cyberpunk/neon
Adaptado para terminales FSOCIETY y compatibilidad máxima
"""

import random
import string
import os
import re
import sys
import time
from datetime import datetime

# ====== DETECCIÓN DE SOPORTE DE COLORES ======
def soporta_colores():
    """Detecta si la terminal soporta colores ANSI"""
    if not sys.stdout.isatty():
        return False
    if os.name == 'nt':  # Windows
        return False
    # Verificar variable de entorno TERM
    term = os.environ.get('TERM', '')
    if term in ('dumb', 'unknown'):
        return False
    return True

SOPORTE_COLOR = soporta_colores()

# ====== SISTEMA DE COLORES CON FALLBACK ======
class CyberColors:
    """Paleta de colores cyberpunk con fallback para terminales sin soporte"""
    
    RESET = "\033[0m" if SOPORTE_COLOR else ""
    BOLD = "\033[1m" if SOPORTE_COLOR else ""
    DIM = "\033[2m" if SOPORTE_COLOR else ""
    ITALIC = "\033[3m" if SOPORTE_COLOR else ""
    UNDERLINE = "\033[4m" if SOPORTE_COLOR else ""
    BLINK = "\033[5m" if SOPORTE_COLOR else ""
    
    # Colores principales (con fallback a vacío)
    CYBER_GREEN = "\033[38;2;0;255;200m" if SOPORTE_COLOR else ""
    CYBER_PINK = "\033[38;2;255;0;150m" if SOPORTE_COLOR else ""
    CYBER_BLUE = "\033[38;2;0;150;255m" if SOPORTE_COLOR else ""
    CYBER_PURPLE = "\033[38;2;150;0;255m" if SOPORTE_COLOR else ""
    CYBER_YELLOW = "\033[38;2;255;255;0m" if SOPORTE_COLOR else ""
    CYBER_ORANGE = "\033[38;2;255;150;0m" if SOPORTE_COLOR else ""
    CYBER_RED = "\033[38;2;255;0;50m" if SOPORTE_COLOR else ""
    CYBER_WHITE = "\033[38;2;200;200;220m" if SOPORTE_COLOR else ""
    
    # Fondo
    BG_DARK = "\033[48;2;5;5;20m" if SOPORTE_COLOR else ""
    BG_CYBER = "\033[48;2;10;10;30m" if SOPORTE_COLOR else ""
    
    @staticmethod
    def neon(texto, color):
        """Aplica efecto neón (con fallback)"""
        if SOPORTE_COLOR:
            return f"{CyberColors.BOLD}{color}{texto}{CyberColors.RESET}"
        return texto
    
    @staticmethod
    def glitch(texto):
        """Efecto glitch (con fallback)"""
        if SOPORTE_COLOR:
            colores = [CyberColors.CYBER_PINK, CyberColors.CYBER_BLUE, CyberColors.CYBER_GREEN]
            resultado = ""
            for i, char in enumerate(texto):
                resultado += f"{colores[i % len(colores)]}{char}"
            return f"{resultado}{CyberColors.RESET}"
        return texto

class PypherCyber:
    """Generador de contraseñas con temática cyberpunk (versión estable)"""

    def __init__(self):
        self.caracteres_seguros = "!@#$%&()-_=+[]{}?"
        self.caracteres_completos = string.ascii_letters + string.digits + self.caracteres_seguros
        self.contrasena_actual = ""
        self.nombre_archivo = ""
        self.fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historial = []
        self.efectos_activados = True

        # Intentar importar pyperclip
        try:
            import pyperclip
            self.pyperclip = pyperclip
            self.soporte_portapapeles = True
        except ImportError:
            self.pyperclip = None
            self.soporte_portapapeles = False

    def limpiar_pantalla(self):
        """Limpia la terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_banner(self):
        """Banner cyberpunk (versión simplificada y estable)"""
        banner = f"""
{CyberColors.CYBER_GREEN}╔══════════════════════════════════════════════════════════════╗
║                                                                  ║
║  {CyberColors.CYBER_PINK}██████╗ ██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ {CyberColors.CYBER_GREEN}║
║  {CyberColors.CYBER_BLUE}██╔══██╗╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗{CyberColors.CYBER_GREEN}║
║  {CyberColors.CYBER_PURPLE}██████╔╝ ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝{CyberColors.CYBER_GREEN}║
║  {CyberColors.CYBER_PINK}██╔═══╝   ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗{CyberColors.CYBER_GREEN}║
║  {CyberColors.CYBER_GREEN}██║        ██║   ██║     ██║  ██║███████╗██║  ██║{CyberColors.CYBER_GREEN}║
║  {CyberColors.CYBER_BLUE}╚═╝        ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{CyberColors.CYBER_GREEN}║
║                                                                  ║
║  {CyberColors.neon('▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌', CyberColors.CYBER_GREEN)}{CyberColors.CYBER_GREEN}║
║  {CyberColors.BOLD}{CyberColors.CYBER_PINK}      ⚡ P Y P H E R  -  C Y B E R P U N K  ⚡{CyberColors.RESET}{CyberColors.CYBER_GREEN} ║
║  {CyberColors.neon('▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌', CyberColors.CYBER_GREEN)}{CyberColors.CYBER_GREEN}║
║  {CyberColors.DIM}{CyberColors.CYBER_BLUE}      ─── 🔐 Generador de Contraseñas Seguras ───{CyberColors.CYBER_GREEN} ║
║  {CyberColors.DIM}{CyberColors.CYBER_PURPLE}      ─── 🌐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ───{CyberColors.CYBER_GREEN} ║
╚══════════════════════════════════════════════════════════════╝
{CyberColors.RESET}"""
        print(banner)

    def mostrar_contraseña(self, contrasena):
        """Muestra la contraseña con estilo cyberpunk (versión estable)"""
        if not contrasena:
            return

        colores = [CyberColors.CYBER_PINK, CyberColors.CYBER_BLUE,
                   CyberColors.CYBER_GREEN, CyberColors.CYBER_PURPLE,
                   CyberColors.CYBER_YELLOW]

        print(f"\n{CyberColors.BOLD}{CyberColors.CYBER_GREEN}┌─────────────────────────────────────────────────────┐{CyberColors.RESET}")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}│ {CyberColors.CYBER_PINK}🔑 CONTRASEÑA GENERADA{CyberColors.CYBER_GREEN}                       │{CyberColors.RESET}")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}├─────────────────────────────────────────────────────┤{CyberColors.RESET}")

        # Mostrar contraseña
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}│ {CyberColors.RESET}", end="")
        if SOPORTE_COLOR:
            for i, char in enumerate(contrasena):
                color = colores[i % len(colores)]
                print(f"{color}{CyberColors.BOLD}{char}{CyberColors.RESET}", end="")
        else:
            print(contrasena, end="")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN} │{CyberColors.RESET}")

        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}└─────────────────────────────────────────────────────┘{CyberColors.RESET}")

    def analizar_fortaleza(self, contrasena):
        """Analiza fortaleza de la contraseña"""
        longitud = len(contrasena)
        puntaje = 0

        if longitud >= 8:
            puntaje += 1
        if longitud >= 12:
            puntaje += 1
        if longitud >= 16:
            puntaje += 1
        if re.search(r"[A-Z]", contrasena):
            puntaje += 1
        if re.search(r"[a-z]", contrasena):
            puntaje += 1
        if re.search(r"\d", contrasena):
            puntaje += 1
        if re.search(r"[!@#$%&()\-_=+[\]{}?]", contrasena):
            puntaje += 1

        max_puntaje = 8
        porcentaje = int((puntaje / max_puntaje) * 100)

        # Barras de progreso
        barra = ""
        for i in range(0, 100, 10):
            if i < porcentaje:
                barra += f"{CyberColors.CYBER_GREEN}█{CyberColors.RESET}" if SOPORTE_COLOR else "█"
            else:
                barra += f"{CyberColors.DIM}░{CyberColors.RESET}" if SOPORTE_COLOR else "░"

        if porcentaje >= 80:
            nivel = f"{CyberColors.CYBER_GREEN}███ FUERTE ███{CyberColors.RESET}" if SOPORTE_COLOR else "FUERTE"
        elif porcentaje >= 60:
            nivel = f"{CyberColors.CYBER_YELLOW}██ MEDIA ██{CyberColors.RESET}" if SOPORTE_COLOR else "MEDIA"
        else:
            nivel = f"{CyberColors.CYBER_RED}█ DÉBIL █{CyberColors.RESET}" if SOPORTE_COLOR else "DÉBIL"

        return {
            "porcentaje": porcentaje,
            "nivel": nivel,
            "barra": barra
        }

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas de la contraseña"""
        if not contrasena:
            return

        mayus = sum(1 for c in contrasena if c.isupper())
        minus = sum(1 for c in contrasena if c.islower())
        digitos = sum(1 for c in contrasena if c.isdigit())
        simbolos = len(contrasena) - mayus - minus - digitos

        fortaleza = self.analizar_fortaleza(contrasena)

        print(f"\n{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.CYBER_PINK} 📊 ESTADÍSTICAS DE SEGURIDAD{CyberColors.CYBER_PURPLE}                 ║{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╠═══════════════════════════════════════════════════╣{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_PINK}▶{CyberColors.RESET} Mayúsculas: {CyberColors.CYBER_BLUE}{mayus:>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_GREEN}▶{CyberColors.RESET} Minúsculas: {CyberColors.CYBER_BLUE}{minus:>3}{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_YELLOW}▶{CyberColors.RESET} Números:    {CyberColors.CYBER_BLUE}{digitos:>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_PINK}▶{CyberColors.RESET} Símbolos:   {CyberColors.CYBER_BLUE}{simbolos:>3}{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_BLUE}▶{CyberColors.RESET} Longitud:   {CyberColors.CYBER_BLUE}{len(contrasena):>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_PURPLE}▶{CyberColors.RESET} Fortaleza: {fortaleza['nivel']}")
        print(f"{CyberColors.CYBER_PURPLE}╠═══════════════════════════════════════════════════╣{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_GREEN}BARRA:{CyberColors.RESET} [{fortaleza['barra']}] {CyberColors.CYBER_BLUE}{fortaleza['porcentaje']}%{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

    def generar_contrasena(self, longitud=10):
        """Genera una contraseña aleatoria"""
        if self.efectos_activados:
            print(f"\n{CyberColors.CYBER_GREEN}⚡ GENERANDO CONTRASEÑA...{CyberColors.RESET}")
            if SOPORTE_COLOR:
                for i in range(4):
                    sys.stdout.write(f"\r{CyberColors.CYBER_PURPLE}█{CyberColors.RESET}" * i)
                    sys.stdout.write(f"{CyberColors.CYBER_BLUE}█{CyberColors.RESET}" * (3 - i))
                    sys.stdout.write(f" {i*25}%")
                    sys.stdout.flush()
                    time.sleep(0.1)
                print()

        contrasena = ''.join(random.choice(self.caracteres_completos) for _ in range(longitud))
        self.historial.append(contrasena)
        if len(self.historial) > 10:
            self.historial.pop(0)
        return contrasena

    def copiar_portapapeles(self, contrasena):
        """Copia al portapapeles"""
        if not self.soporte_portapapeles:
            print(f"\n{CyberColors.CYBER_YELLOW}⚠️  pyperclip no instalado. Instálalo con: pip install pyperclip{CyberColors.RESET}")
            return False

        try:
            self.pyperclip.copy(contrasena)
            print(f"\n{CyberColors.CYBER_GREEN}✅ CONTRASEÑA COPIADA AL PORTAPAPELES{CyberColors.RESET}")
            if self.efectos_activados and SOPORTE_COLOR:
                for _ in range(3):
                    sys.stdout.write(f"\r{CyberColors.CYBER_PINK}✨{CyberColors.RESET}")
                    time.sleep(0.1)
                    sys.stdout.write(f"\r{CyberColors.CYBER_BLUE}✨{CyberColors.RESET}")
                    time.sleep(0.1)
                print()
            return True
        except Exception as e:
            print(f"\n{CyberColors.CYBER_RED}❌ Error al copiar: {e}{CyberColors.RESET}")
            return False

    def guardar_archivo(self, contrasena, nombre, fecha):
        """Guarda la contraseña en un archivo"""
        if not contrasena:
            print(f"\n{CyberColors.CYBER_RED}❌ No hay contraseña para guardar{CyberColors.RESET}")
            return

        if not nombre:
            nombre = f"pypher_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not nombre.endswith('.txt'):
            nombre += '.txt'

        mayus = sum(1 for c in contrasena if c.isupper())
        minus = sum(1 for c in contrasena if c.islower())
        digitos = sum(1 for c in contrasena if c.isdigit())
        simbolos = len(contrasena) - mayus - minus - digitos

        contenido = f"""==================================================
              🐍 PYPHER - REGISTRO DE CONTRASEÑA
==================================================
Fecha de creación : {fecha}
Contraseña        : {contrasena}
Longitud          : {len(contrasena)} caracteres
Mayúsculas        : {mayus}
Minúsculas        : {minus}
Números           : {digitos}
Símbolos          : {simbolos}
Caracteres usados : Letras + Números + !@#$%&()-_=+[]{{}}?
==================================================
🔒 Recomendación: Guarda esta contraseña en un lugar seguro.
⚡ Generado con Pypher Cyberpunk Edition
==================================================
"""

        try:
            with open(nombre, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print(f"\n{CyberColors.CYBER_GREEN}✅ ARCHIVO GUARDADO EXITOSAMENTE{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_BLUE}📁 {os.path.abspath(nombre)}{CyberColors.RESET}")
        except Exception as e:
            print(f"\n{CyberColors.CYBER_RED}❌ Error al guardar: {e}{CyberColors.RESET}")