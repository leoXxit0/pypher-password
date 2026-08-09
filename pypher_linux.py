#!/usr/bin/env python3
"""
🐍 PYPHER - CYBERPUNK EDITION
Generador de contraseñas con estética cyberpunk/neon
Adaptado de: https://github.com/leoXxit0/pypher-password
"""

import random
import string
import os
import re
import sys
import time
from datetime import datetime

# ====== SISTEMA DE COLORES CYBERPUNK ======
class CyberColors:
    """Paleta de colores cyberpunk para terminal"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"

    # Colores principales
    CYBER_GREEN = "\033[38;2;0;255;200m"      # #00FFC8 - Verde neón
    CYBER_PINK = "\033[38;2;255;0;150m"       # #FF0096 - Rosa neón
    CYBER_BLUE = "\033[38;2;0;150;255m"       # #0096FF - Azul neón
    CYBER_PURPLE = "\033[38;2;150;0;255m"     # #9600FF - Púrpura neón
    CYBER_YELLOW = "\033[38;2;255;255;0m"     # #FFFF00 - Amarillo neón
    CYBER_ORANGE = "\033[38;2;255;150;0m"     # #FF9600 - Naranja neón
    CYBER_RED = "\033[38;2;255;0;50m"         # #FF0032 - Rojo neón

    # Colores de fondo
    BG_DARK = "\033[48;2;5;5;20m"             # #050514 - Fondo oscuro
    BG_CYBER = "\033[48;2;10;10;30m"          # #0A0A1E - Fondo cyberpunk

    # Colores para la matriz (verde clásico)
    MATRIX_GREEN = "\033[38;2;0;255;65m"      # #00FF41

    # Efectos especiales
    GLITCH = "\033[38;2;200;0;255m"           # #C800FF - Efecto glitch

    @staticmethod
    def neon(texto, color):
        """Aplica efecto neón a un texto"""
        return f"{CyberColors.BOLD}{color}{texto}{CyberColors.RESET}"

    @staticmethod
    def glitch(texto):
        """Aplica efecto glitch (alterna colores)"""
        colores = [CyberColors.CYBER_PINK, CyberColors.CYBER_BLUE, CyberColors.CYBER_GREEN]
        resultado = ""
        for i, char in enumerate(texto):
            resultado += f"{colores[i % len(colores)]}{char}"
        return f"{resultado}{CyberColors.RESET}"

class PypherCyber:
    """Generador de contraseñas con temática cyberpunk"""

    def __init__(self):
        self.caracteres_seguros = "!@#$%&()-_=+[]{}?"
        self.caracteres_completos = string.ascii_letters + string.digits + self.caracteres_seguros
        self.contrasena_actual = ""
        self.nombre_archivo = ""
        self.fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historial = []  # Guarda últimas contraseñas generadas

        # Intentar importar pyperclip
        try:
            import pyperclip
            self.pyperclip = pyperclip
            self.soporte_portapapeles = True
        except ImportError:
            self.pyperclip = None
            self.soporte_portapapeles = False

        # Efectos especiales
        self.efectos_activados = True
        self.modo_matrix = False

    def limpiar_pantalla(self):
        """Limpia la terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def efecto_escritura(self, texto, delay=0.03):
        """Simula escritura estilo hacker"""
        if not self.efectos_activados:
            print(texto)
            return

        for char in texto:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def mostrar_banner(self):
        """Banner cyberpunk con arte ASCII"""
        banner = f"""
{CyberColors.BG_DARK}{CyberColors.CYBER_GREEN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  {CyberColors.CYBER_PINK}▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ {CyberColors.RESET}║
║  {CyberColors.CYBER_BLUE}▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌{CyberColors.RESET}║
║  {CyberColors.CYBER_PURPLE}▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ {CyberColors.RESET}║
║  {CyberColors.CYBER_PINK}▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌          {CyberColors.RESET}║
║  {CyberColors.CYBER_GREEN}▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌          {CyberColors.RESET}║
║  {CyberColors.CYBER_BLUE}▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          {CyberColors.RESET}║
║  {CyberColors.CYBER_PURPLE}▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌          {CyberColors.RESET}║
║  {CyberColors.CYBER_PINK}▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌          {CyberColors.RESET}║
║  {CyberColors.CYBER_GREEN}▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ {CyberColors.RESET}║
║  {CyberColors.CYBER_BLUE}▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌{CyberColors.RESET}║
║  {CyberColors.CYBER_PURPLE}▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀ {CyberColors.RESET}║
║                                                              ║
║  {CyberColors.neon('▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌', CyberColors.CYBER_GREEN)}{CyberColors.RESET}║
║  {CyberColors.BOLD}{CyberColors.CYBER_PINK}      ⚡ P Y P H E R  -  C Y B E R P U N K  ⚡{CyberColors.RESET}{CyberColors.RESET} ║
║  {CyberColors.neon('▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌', CyberColors.CYBER_GREEN)}{CyberColors.RESET}║
║  {CyberColors.DIM}{CyberColors.CYBER_BLUE}      ─── 🔐 Generador de Contraseñas Seguras ───{CyberColors.RESET} ║
║  {CyberColors.DIM}{CyberColors.CYBER_PURPLE}      ─── 🌐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ───{CyberColors.RESET} ║
╚══════════════════════════════════════════════════════════════╝
{CyberColors.RESET}"""
        print(banner)

    def mostrar_contraseña(self, contrasena):
        """Muestra la contraseña con estilo cyberpunk"""
        if not contrasena:
            return

        # Dividir en caracteres para efecto neón
        colores = [CyberColors.CYBER_PINK, CyberColors.CYBER_BLUE,
                   CyberColors.CYBER_GREEN, CyberColors.CYBER_PURPLE,
                   CyberColors.CYBER_YELLOW]

        print(f"\n{CyberColors.BOLD}{CyberColors.CYBER_GREEN}┌─────────────────────────────────────────────────────┐{CyberColors.RESET}")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}│ {CyberColors.CYBER_PINK}🔑 CONTRASEÑA GENERADA{CyberColors.CYBER_GREEN}                       │{CyberColors.RESET}")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}├─────────────────────────────────────────────────────┤{CyberColors.RESET}")

        # Mostrar contraseña con efecto neón
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}│ {CyberColors.RESET}", end="")
        for i, char in enumerate(contrasena):
            color = colores[i % len(colores)]
            print(f"{color}{CyberColors.BOLD}{char}{CyberColors.RESET}", end="")
        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN} │{CyberColors.RESET}")

        print(f"{CyberColors.BOLD}{CyberColors.CYBER_GREEN}└─────────────────────────────────────────────────────┘{CyberColors.RESET}")

    def analizar_fortaleza(self, contrasena):
        """Analiza fortaleza con estilo cyberpunk"""
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

        # Barras de progreso con estilo cyberpunk
        barra = ""
        for i in range(0, 100, 10):
            if i < porcentaje:
                barra += f"{CyberColors.CYBER_GREEN}█{CyberColors.RESET}"
            else:
                barra += f"{CyberColors.DIM}░{CyberColors.RESET}"

        if porcentaje >= 80:
            nivel = f"{CyberColors.CYBER_GREEN}███ FUERTE ███{CyberColors.RESET}"
            color = CyberColors.CYBER_GREEN
        elif porcentaje >= 60:
            nivel = f"{CyberColors.CYBER_YELLOW}██ MEDIA ██{CyberColors.RESET}"
            color = CyberColors.CYBER_YELLOW
        else:
            nivel = f"{CyberColors.CYBER_RED}█ DÉBIL █{CyberColors.RESET}"
            color = CyberColors.CYBER_RED

        return {
            "porcentaje": porcentaje,
            "nivel": nivel,
            "barra": barra,
            "color": color
        }

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas con estilo cyberpunk"""
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

        # Datos con formato cyberpunk
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_PINK}▶{CyberColors.RESET} Mayúsculas: {CyberColors.CYBER_BLUE}{mayus:>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_GREEN}▶{CyberColors.RESET} Minúsculas: {CyberColors.CYBER_BLUE}{minus:>3}{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_YELLOW}▶{CyberColors.RESET} Números:    {CyberColors.CYBER_BLUE}{digitos:>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_PINK}▶{CyberColors.RESET} Símbolos:   {CyberColors.CYBER_BLUE}{simbolos:>3}{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_BLUE}▶{CyberColors.RESET} Longitud:   {CyberColors.CYBER_BLUE}{len(contrasena):>3}{CyberColors.RESET}    {CyberColors.CYBER_PURPLE}│{CyberColors.RESET} {CyberColors.CYBER_PURPLE}▶{CyberColors.RESET} Fortaleza: {fortaleza['nivel']}")
        print(f"{CyberColors.CYBER_PURPLE}╠═══════════════════════════════════════════════════╣{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {CyberColors.CYBER_GREEN}BARRA:{CyberColors.RESET} [{fortaleza['barra']}] {CyberColors.CYBER_BLUE}{fortaleza['porcentaje']}%{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

    def generar_contrasena(self, longitud=10):
        """Genera contraseña con efecto de animación"""
        if self.efectos_activados:
            print(f"\n{CyberColors.CYBER_GREEN}⚡ GENERANDO CONTRASEÑA SEGURA...{CyberColors.RESET}")
            # Animación de barras de carga
            for i in range(4):
                sys.stdout.write(f"\r{CyberColors.CYBER_PURPLE}█{CyberColors.RESET}" * i)
                sys.stdout.write(f"{CyberColors.CYBER_BLUE}█{CyberColors.RESET}" * (3 - i))
                sys.stdout.write(f" {i*25}%")
                sys.stdout.flush()
                time.sleep(0.1)
            print()

        contrasena = ''.join(random.choice(self.caracteres_completos) for _ in range(longitud))

        # Guardar en historial
        self.historial.append(contrasena)
        if len(self.historial) > 10:
            self.historial.pop(0)

        return contrasena

    def copiar_portapapeles(self, contrasena):
        """Copia con efecto visual"""
        if not self.soporte_portapapeles:
            print(f"\n{CyberColors.CYBER_YELLOW}⚠️  pyperclip no instalado. Instálalo con: pip install pyperclip{CyberColors.RESET}")
            return False

        try:
            self.pyperclip.copy(contrasena)
            print(f"\n{CyberColors.CYBER_GREEN}✅ CONTRASEÑA COPIADA AL PORTAPAPELES{CyberColors.RESET}")

            # Efecto de confirmación
            if self.efectos_activados:
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
        """Guarda con estilo"""
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

        contenido = f"""╔════════════════════════════════════════════════════════════╗
║                    🐍 PYPHER - REGISTRO DE CONTRASEÑA                ║
╠════════════════════════════════════════════════════════════╣
║  Fecha de creación : {fecha}
║  Contraseña        : {contrasena}
║  Longitud          : {len(contrasena)} caracteres
║  Mayúsculas        : {mayus}
║  Minúsculas        : {minus}
║  Números           : {digitos}
║  Símbolos          : {simbolos}
║  Caracteres usados : Letras + Números + !@#$%&()-_=+[]{{}}?
╠════════════════════════════════════════════════════════════╣
║  🔒 Recomendación: Guarda esta contraseña en un lugar seguro.
║  ⚡ Generado con Pypher Cyberpunk Edition
╚════════════════════════════════════════════════════════════╝
"""

        try:
            with open(nombre, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)

            print(f"\n{CyberColors.CYBER_GREEN}✅ ARCHIVO GUARDADO EXITOSAMENTE{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_BLUE}📁 {os.path.abspath(nombre)}{CyberColors.RESET}")
        except Exception as e:
            print(f"\n{CyberColors.CYBER_RED}❌ Error al guardar: {e}{CyberColors.RESET}")

    def menu_principal(self):
        """Menú principal cyberpunk"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()

            # Mostrar contraseña actual
            if self.contrasena_actual:
                self.mostrar_contraseña(self.contrasena_actual)
                self.mostrar_estadisticas(self.contrasena_actual)
                print()

            # Menú con estilo cyberpunk
            print(f"{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.CYBER_PINK}   📋 MENÚ PRINCIPAL{CyberColors.CYBER_PURPLE}                         ║{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_PURPLE}╠═══════════════════════════════════════════════════╣{CyberColors.RESET}")

            opciones = [
                ("1", "🔐", "Generar nueva contraseña", CyberColors.CYBER_GREEN),
                ("2", "📋", "Copiar al portapapeles", CyberColors.CYBER_BLUE),
                ("3", "💾", "Guardar en archivo", CyberColors.CYBER_YELLOW),
                ("4", "📝", "Configurar nombre", CyberColors.CYBER_PURPLE),
                ("5", "📅", "Cambiar fecha", CyberColors.CYBER_ORANGE),
                ("6", "🔄", "Mostrar historial", CyberColors.CYBER_PINK),
                ("7", "⚙️", "Efectos (ON/OFF)", CyberColors.CYBER_RED),
                ("8", "🚪", "Salir", CyberColors.CYBER_RED)
            ]

            for num, icono, texto, color in opciones:
                print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.RESET} {color}{icono} [{num}] {texto:<30}{CyberColors.CYBER_PURPLE}║{CyberColors.RESET}")

            print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

            try:
                opcion = input(f"\n{CyberColors.CYBER_PINK}➜ {CyberColors.BOLD}INGRESA OPCIÓN:{CyberColors.RESET} ").strip()

                if opcion == "1":
                    self.submenu_generar()
                elif opcion == "2":
                    if self.contrasena_actual:
                        self.copiar_portapapeles(self.contrasena_actual)
                        input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")
                    else:
                        print(f"\n{CyberColors.CYBER_RED}❌ No hay contraseña para copiar{CyberColors.RESET}")
                        input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")
                elif opcion == "3":
                    self.guardar_archivo(
                        self.contrasena_actual,
                        self.nombre_archivo,
                        self.fecha_actual
                    )
                    input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")
                elif opcion == "4":
                    self.submenu_configurar_nombre()
                elif opcion == "5":
                    self.submenu_cambiar_fecha()
                elif opcion == "6":
                    self.mostrar_historial()
                elif opcion == "7":
                    self.toggle_efectos()
                elif opcion == "8":
                    self.despedida()
                    sys.exit(0)
                else:
                    print(f"\n{CyberColors.CYBER_RED}❌ OPCIÓN INVÁLIDA{CyberColors.RESET}")
                    time.sleep(1)

            except KeyboardInterrupt:
                self.despedida()
                sys.exit(0)
            except Exception as e:
                print(f"\n{CyberColors.CYBER_RED}❌ ERROR: {e}{CyberColors.RESET}")
                input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")

    def submenu_generar(self):
        """Submenú para generar contraseña"""
        self.limpiar_pantalla()
        self.mostrar_banner()

        print(f"\n{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.CYBER_PINK}   🔐 GENERAR CONTRASEÑA{CyberColors.CYBER_PURPLE}                     ║{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

        try:
            longitud_input = input(f"\n{CyberColors.CYBER_GREEN}⚡ Longitud (8-20, Enter=10): {CyberColors.RESET}").strip()
            if not longitud_input:
                longitud = 10
            else:
                longitud = int(longitud_input)

            if longitud < 8:
                print(f"{CyberColors.CYBER_YELLOW}⚠️  Mínimo 8 caracteres{CyberColors.RESET}")
                longitud = 8
            elif longitud > 20:
                print(f"{CyberColors.CYBER_YELLOW}⚠️  Máximo 20 caracteres{CyberColors.RESET}")
                longitud = 20

            self.contrasena_actual = self.generar_contrasena(longitud)

            self.limpiar_pantalla()
            self.mostrar_banner()
            self.mostrar_contraseña(self.contrasena_actual)
            self.mostrar_estadisticas(self.contrasena_actual)

            # Preguntar acciones
            print(f"\n{CyberColors.CYBER_PURPLE}┌─────────────────────────────────────────────────────┐{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_PURPLE}│{CyberColors.CYBER_PINK}   ACCIONES RÁPIDAS{CyberColors.CYBER_PURPLE}                                │{CyberColors.RESET}")
            print(f"{CyberColors.CYBER_PURPLE}└─────────────────────────────────────────────────────┘{CyberColors.RESET}")

            copiar = input(f"\n{CyberColors.CYBER_GREEN}📋 ¿Copiar al portapapeles? (s/N): {CyberColors.RESET}").strip().lower()
            if copiar in ['s', 'si', 'sí', 'y', 'yes']:
                self.copiar_portapapeles(self.contrasena_actual)

            guardar = input(f"\n{CyberColors.CYBER_GREEN}💾 ¿Guardar en archivo? (s/N): {CyberColors.RESET}").strip().lower()
            if guardar in ['s', 'si', 'sí', 'y', 'yes']:
                nombre = input(f"{CyberColors.CYBER_BLUE}📝 Nombre del archivo (Enter=auto): {CyberColors.RESET}").strip()
                if not nombre:
                    nombre = f"pypher_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.guardar_archivo(self.contrasena_actual, nombre, self.fecha_actual)

        except ValueError:
            print(f"\n{CyberColors.CYBER_RED}❌ Error: Introduce un número válido{CyberColors.RESET}")

        input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")

    def submenu_configurar_nombre(self):
        """Configurar nombre del archivo"""
        self.limpiar_pantalla()
        self.mostrar_banner()

        print(f"\n{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.CYBER_PINK}   📝 CONFIGURAR NOMBRE{CyberColors.CYBER_PURPLE}                     ║{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

        print(f"\n{CyberColors.CYBER_BLUE}📁 Nombre actual: {self.nombre_archivo or '(no definido)'}{CyberColors.RESET}")

        nombre = input(f"\n{CyberColors.CYBER_GREEN}✏️  Nuevo nombre (Enter para cancelar): {CyberColors.RESET}").strip()
        if nombre:
            self.nombre_archivo = nombre
            print(f"\n{CyberColors.CYBER_GREEN}✅ Nombre configurado: {nombre}{CyberColors.RESET}")
        else:
            print(f"\n{CyberColors.CYBER_YELLOW}⚠️  Nombre no modificado{CyberColors.RESET}")

        input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")

    def submenu_cambiar_fecha(self):
        """Cambiar fecha"""
        self.limpiar_pantalla()
        self.mostrar_banner()

        print(f"\n{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}║{CyberColors.CYBER_PINK}   📅 CAMBIAR FECHA{CyberColors.CYBER_PURPLE}                         ║{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}╚═══════════════════════════════════════════════════╝{CyberColors.RESET}")

        print(f"\n{CyberColors.CYBER_BLUE}📅 Fecha actual: {self.fecha_actual}{CyberColors.RESET}")

        print(f"\n{CyberColors.CYBER_YELLOW}Formato: DD/MM/AAAA HH:MM{CyberColors.RESET}")
        nueva_fecha = input(f"\n{CyberColors.CYBER_GREEN}✏️  Nueva fecha (Enter=restaurar actual): {CyberColors.RESET}").strip()

        if not nueva_fecha:
            self.fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            print(f"\n{CyberColors.CYBER_GREEN}✅ Fecha restaurada: {self.fecha_actual}{CyberColors.RESET}")
        else:
            try:
                datetime.strptime(nueva_fecha, "%d/%m/%Y %H:%M")
                self.fecha_actual = nueva_fecha
                print(f"\n{CyberColors.CYBER_GREEN}✅ Fecha actualizada: {self.fecha_actual}{CyberColors.RESET}")
            except ValueError:
                print(f"\n{CyberColors.CYBER_RED}❌ Formato inválido. Usa DD/MM/AAAA HH:MM{CyberColors.RESET}")

        input(f"\n{CyberColors.CYBER_BLUE}Presiona Enter para continuar...{CyberColors.RESET}")

    def mostrar_historial(self):
        """Muestra historial de contraseñas"""
        self.limpiar_pantalla()
        self.mostrar_banner()

        print(f"\n{CyberColors.CYBER_PURPLE}╔═══════════════════════════════════════════════════╗{CyberColors.RESET}")
        print(f"{CyberColors.CYBER_PURPLE}