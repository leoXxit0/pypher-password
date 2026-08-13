#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pypher - Generador y Analizador de Contraseñas
# Copyright (C) 2024  Pypher Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Pypher CLI - Generador y Analizador de Contraseñas
====================================================

Herramienta de línea de comandos, con estética "Cyberpunk", para:

* Generar contraseñas aleatorias seguras.
* Analizar la fortaleza de contraseñas existentes (con estadísticas
  avanzadas: entropía, tiempo estimado de crackeo, patrones inseguros).
* Generar wordlists con fines educativos y de auditoría de seguridad
  (pruebas de fortaleza propias, CTFs, pentesting autorizado, etc.).

Puede usarse en modo interactivo (menú) o en modo no interactivo
(argumentos de línea de comandos), lo que la hace apta tanto para uso
manual como para integrarse en scripts.

Licencia: GNU GPLv3. Ver el archivo LICENSE del repositorio para más
información, o https://www.gnu.org/licenses/gpl-3.0.html
"""

import argparse
import getpass
import gzip
import hashlib
import itertools
import json
import math
import os
import random
import re
import shutil
import string
import subprocess
import sys
from datetime import datetime

# =====================================================================
# === Versión del programa (usada por --version y en la config) ===
# =====================================================================
__version__ = "1.0.0"

# =====================================================================
# === Sistema de configuración de usuario (~/.config/pypher/) ===
# =====================================================================
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "pypher")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "ultima_carpeta": None,
    "preferencias": {
        "longitud_por_defecto": 12,
    },
}


def cargar_configuracion() -> dict:
    """Carga la configuración de usuario desde ``~/.config/pypher/config.json``.

    Si el directorio o el archivo no existen todavía, los crea con los
    valores por defecto (``DEFAULT_CONFIG``). Si el archivo existe pero
    está corrupto o no se puede leer, se devuelve una copia de los
    valores por defecto sin modificar el archivo original.

    Returns:
        dict: Diccionario de configuración con, al menos, las claves
        ``ultima_carpeta`` y ``preferencias``.
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    except OSError:
        return dict(DEFAULT_CONFIG)

    if not os.path.exists(CONFIG_FILE):
        guardar_configuracion(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Aseguramos que existan todas las claves esperadas
            merged = dict(DEFAULT_CONFIG)
            merged.update(config)
            return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)


def guardar_configuracion(config: dict) -> bool:
    """Guarda el diccionario de configuración en ``~/.config/pypher/config.json``.

    Args:
        config: Diccionario de configuración a persistir.

    Returns:
        bool: ``True`` si se guardó correctamente, ``False`` en caso de error.
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False

try:
    import pyperclip
    _PYPERCLIP_DISPONIBLE = True
except ImportError:
    _PYPERCLIP_DISPONIBLE = False


def copiar_portapapeles(texto):
    """Copia texto al portapapeles. Intenta primero pyperclip (multiplataforma);
    si no está instalado, cae a xclip (X11) y luego a wl-copy (Wayland).
    Devuelve True si tuvo éxito, False si ningún método estuvo disponible."""
    if _PYPERCLIP_DISPONIBLE:
        try:
            pyperclip.copy(texto)
            return True
        except Exception:
            pass  # sigue con los métodos de línea de comandos

    for comando in (["xclip", "-selection", "clipboard"], ["wl-copy"]):
        if shutil.which(comando[0]):
            try:
                subprocess.run(comando, input=texto.encode(), check=True)
                return True
            except Exception:
                continue

    return False


def pegar_portapapeles():
    """Obtiene texto del portapapeles. Intenta pyperclip, luego xclip,
    luego wl-paste. Lanza RuntimeError si ningún método está disponible."""
    if _PYPERCLIP_DISPONIBLE:
        try:
            return pyperclip.paste()
        except Exception:
            pass

    for comando in (["xclip", "-selection", "clipboard", "-o"], ["wl-paste"]):
        if shutil.which(comando[0]):
            try:
                resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
                return resultado.stdout
            except Exception:
                continue

    raise RuntimeError(
        "No se pudo acceder al portapapeles: instala 'pyperclip' "
        "(pip install pyperclip) o 'xclip'/'wl-clipboard' en el sistema."
    )

# =====================================================================
# === RESTRICCIÓN CRÍTICA DEL MÓDULO 3 ===
# El generador de wordlists NUNCA debe superar este número total de
# variantes por ejecución, sin importar el modo usado, para evitar un
# consumo excesivo de RAM/disco.
# =====================================================================
MAX_VARIANTES = 150000 # 150 mil variantes

# =====================================================================
# === Patrones comunes a evitar (usado solo como advertencia informativa) ===
# Idénticos a los usados en pypher.py (versión con interfaz gráfica)
# =====================================================================
PATRONES_COMUNES = [
    (r"123456", "secuencia numérica"),
    (r"abcdef", "secuencia alfabética"),
    (r"qwerty", "teclado"),
    (r"password", "palabra común"),
    (r"admin", "palabra común"),
    (r"user", "palabra común"),
    (r"contraseña", "palabra común"),
    (r"contrasena", "palabra común"),
]


def calcular_puntaje_password(contrasena):
    """
    Sistema ÚNICO y riguroso de evaluación de contraseñas (máx. 8 puntos).
    Idéntico al usado en pypher.py (Generador y Analizador con interfaz),
    para que ambas herramientas (GUI y CLI) evalúen con el mismo estándar.

    Criterios:
      1. Longitud >= 8    -> +1
      2. Longitud >= 12   -> +1
      3. Longitud >= 16   -> +1
      4. Mayúsculas       -> +1
      5. Minúsculas       -> +1
      6. Números          -> +1
      7. Símbolos         -> +1
      8. Variedad (>=3 tipos de caracteres distintos) -> +1

    Devuelve: (puntaje, max_puntaje, detalles, mayus, minus, digitos, simbolos, longitud)
    """
    longitud = len(contrasena)
    mayus = sum(1 for c in contrasena if c.isupper())
    minus = sum(1 for c in contrasena if c.islower())
    digitos = sum(1 for c in contrasena if c.isdigit())
    simbolos = longitud - mayus - minus - digitos

    puntaje = 0
    max_puntaje = 8
    detalles = []

    # 1-3. Longitud
    if longitud >= 8:
        puntaje += 1
        detalles.append(f"✅ Longitud: {longitud} caracteres (≥8)")
    else:
        detalles.append(f"❌ Longitud insuficiente: {longitud} caracteres (mínimo 8)")

    if longitud >= 12:
        puntaje += 1
        detalles.append("✅ Longitud recomendada (≥12)")
    else:
        detalles.append("⚠️ Longitud menor a 12 caracteres")

    if longitud >= 16:
        puntaje += 1
        detalles.append("✅ Longitud óptima (≥16)")
    else:
        detalles.append("⚠️ Longitud menor a 16 caracteres")

    # 4. Mayúsculas
    if mayus > 0:
        puntaje += 1
        detalles.append(f"✅ Mayúsculas: {mayus}")
    else:
        detalles.append("❌ Sin mayúsculas")

    # 5. Minúsculas
    if minus > 0:
        puntaje += 1
        detalles.append(f"✅ Minúsculas: {minus}")
    else:
        detalles.append("❌ Sin minúsculas")

    # 6. Números
    if digitos > 0:
        puntaje += 1
        detalles.append(f"✅ Números: {digitos}")
    else:
        detalles.append("❌ Sin números")

    # 7. Símbolos
    if simbolos > 0:
        puntaje += 1
        detalles.append(f"✅ Símbolos: {simbolos}")
    else:
        detalles.append("❌ Sin símbolos")

    # 8. Variedad real: al menos 3 de los 4 tipos de caracteres presentes
    tipos = sum(1 for cantidad in (mayus, minus, digitos, simbolos) if cantidad > 0)
    if tipos >= 3:
        puntaje += 1
        detalles.append(f"✅ Variedad de caracteres: {tipos}/4 tipos")
    else:
        detalles.append(f"⚠️ Poca variedad: {tipos}/4 tipos")

    # Advertencia informativa (no resta puntos, pero se muestra en el detalle)
    for patron, nombre in PATRONES_COMUNES:
        if re.search(patron, contrasena.lower()):
            detalles.append(f"⚠️ Contiene patrón común: {nombre}")
            break

    return puntaje, max_puntaje, detalles, mayus, minus, digitos, simbolos, longitud


class GeneradorContrasenasCLI:
    """Motor principal de Pypher: generación y análisis de contraseñas,
    junto con la persistencia de contraseñas y análisis en archivos de
    texto dentro de ``~/pypher``."""

    def __init__(self) -> None:
        """Inicializa la paleta de colores 'Cyberpunk' y prepara la
        carpeta de datos del usuario (``~/pypher``)."""
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

        # Obtener la ruta de la carpeta de datos de Pypher (~/pypher)
        self.documentos_path = self._obtener_ruta_documentos()

    def _obtener_ruta_documentos(self):
        """Obtiene (y crea si hace falta) la carpeta ~/pypher, usada para
        guardar todos los archivos generados por la herramienta. Se usa
        siempre la raíz del home del usuario en lugar de buscar carpetas
        como 'Documentos'/'Documents', para evitar problemas de
        compatibilidad entre distintos idiomas, distros y entornos
        (servidores sin carpetas de usuario estándar, contenedores, etc.)."""
        home = os.path.expanduser("~")
        ruta_pypher = os.path.join(home, "pypher")

        if not os.path.exists(ruta_pypher):
            try:
                os.makedirs(ruta_pypher)
                print(f"{self.colores['verde']}│ ✓ Carpeta creada en: {ruta_pypher}{self.colores['reset']}")
            except Exception:
                # Si falla, usar el directorio actual
                return "."
        return ruta_pypher

    # =================================================================
    # === Análisis de fortaleza (motor unificado, igual que la GUI) ===
    # =================================================================
    def analizar_fortaleza(self, contrasena):
        """Analiza la fortaleza de la contraseña usando el sistema unificado
        de 8 puntos (idéntico al de pypher.py) y devuelve un diccionario
        con las métricas, el detalle criterio por criterio y el nivel."""
        puntaje, max_puntaje, detalles, mayus, minus, digitos, simbolos, longitud = calcular_puntaje_password(contrasena)

        porcentaje = int((puntaje / max_puntaje) * 100)

        if porcentaje >= 80:
            nivel = "FUERTE"
            emoji_nivel = "🔒"
            color = self.colores["verde"]
            descripcion = "¡Excelente contraseña! Es muy segura."
        elif porcentaje >= 60:
            nivel = "MEDIA"
            emoji_nivel = "⚡"
            color = self.colores["amarillo"]
            descripcion = "Contraseña aceptable, pero puede mejorar."
        else:
            nivel = "DÉBIL"
            emoji_nivel = "⚠️"
            color = self.colores["rojo"]
            descripcion = "¡Contraseña insegura! Considera cambiarla."

        return {
            "longitud": longitud,
            "mayusculas": mayus,
            "minusculas": minus,
            "digitos": digitos,
            "simbolos": simbolos,
            "puntaje": puntaje,
            "max_puntaje": max_puntaje,
            "porcentaje": porcentaje,
            "nivel": nivel,
            "emoji_nivel": emoji_nivel,
            "descripcion": descripcion,
            "detalles": detalles,
            "color": color
        }

    def mostrar_estadisticas(self, contrasena):
        """Muestra estadísticas resumidas de la contraseña (usado tras generar)"""
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
        print(f"{self.colores['morado']}│ {self.colores['negrita']}Fortaleza: {stats['color']}{stats['emoji_nivel']} {stats['nivel']} ({stats['puntaje']}/{stats['max_puntaje']} · {stats['porcentaje']}%){self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['gris']}[{self.colores['verde']}{bar}{self.colores['gris']}] {stats['porcentaje']:>3}%{self.colores['reset']}")

    def mostrar_analisis_detallado(self, contrasena):
        """Réplica en terminal del panel 'Analizador' de la interfaz gráfica:
        muestra puntuación, barra de fortaleza y el detalle criterio por
        criterio (incluyendo advertencias de patrones comunes)."""
        stats = self.analizar_fortaleza(contrasena)

        bar_len = 30
        filled = int((stats['porcentaje'] / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"\n{self.colores['morado']}╔{'═' * 60}╗{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']} {self.colores['negrita']}{self.colores['blanco']}🔍 ANÁLISIS DE CONTRASEÑA{self.colores['reset']}")
        print(f"{self.colores['morado']}╚{'═' * 60}╝{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│{self.colores['reset']} Nivel: {stats['color']}{self.colores['negrita']}{stats['emoji_nivel']} {stats['nivel']}{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']} Puntuación: {self.colores['blanco']}{stats['puntaje']}/{stats['max_puntaje']} ({stats['porcentaje']}%){self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']} [{self.colores['verde']}{bar}{self.colores['reset']}]")

        print(f"\n{self.colores['morado']}│ {self.colores['blanco']}DETALLES:{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {'-' * 40}{self.colores['reset']}")
        for detalle in stats["detalles"]:
            if detalle.startswith("✅"):
                col = self.colores["verde"]
            elif detalle.startswith("❌"):
                col = self.colores["rojo"]
            else:
                col = self.colores["naranja"]
            print(f"{self.colores['morado']}│{self.colores['reset']} {col}{detalle}{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│{self.colores['reset']} {stats['color']}{self.colores['negrita']}{stats['descripcion']}{self.colores['reset']}\n")

        return stats

    def analizar_contrasena_interactivo(self):
        """Flujo interactivo del Analizador de Contraseñas para terminal.
        Réplica sin GUI del panel 'Analizador' de pypher.py: permite
        ingresar la contraseña oculta o visible, pegarla desde el
        portapapeles, analizarla y opcionalmente guardar el reporte."""
        print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}ANALIZADOR DE CONTRASEÑAS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['gris']}Verifica la seguridad de tus contraseñas{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}¿Cómo quieres ingresar la contraseña?{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[1]{self.colores['blanco']} Escribirla oculta (recomendado)")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[2]{self.colores['blanco']} Escribirla visible")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[3]{self.colores['blanco']} Pegar desde el portapapeles")

        modo = input(f"{self.colores['morado']}│ {self.colores['verde']}➤ {self.colores['reset']}").strip()

        contrasena = ""
        if modo == "2":
            contrasena = input(f"{self.colores['morado']}│ {self.colores['azul']}Contraseña a analizar: {self.colores['reset']}")
        elif modo == "3":
            try:
                contrasena = pegar_portapapeles()
                print(f"{self.colores['verde']}│ ✓ Contenido pegado desde el portapapeles{self.colores['reset']}")
            except Exception as e:
                print(f"{self.colores['rojo']}│ ✗ {str(e)}{self.colores['reset']}")
                return
        else:
            contrasena = getpass.getpass(f"{self.colores['morado']}│ {self.colores['azul']}Contraseña a analizar (oculta): {self.colores['reset']}")

        if not contrasena:
            print(f"{self.colores['rojo']}│ ✗ Ingresa una contraseña para analizar{self.colores['reset']}")
            return

        stats = self.mostrar_analisis_detallado(contrasena)

        guardar = input(f"{self.colores['morado']}│ {self.colores['azul']}¿Guardar este análisis en un archivo? (s/n): {self.colores['reset']}").strip().lower()
        if guardar == 's':
            nombre = input(f"{self.colores['morado']}│ {self.colores['azul']}Nombre del archivo: {self.colores['reset']}").strip()
            if nombre:
                subcarpeta = input(f"{self.colores['morado']}│ {self.colores['azul']}Subcarpeta (opcional, Enter para omitir): {self.colores['reset']}").strip()
                self.guardar_analisis(contrasena, stats, nombre, subcarpeta=subcarpeta if subcarpeta else None)
            else:
                print(f"{self.colores['rojo']}│ ✗ El nombre no puede estar vacío{self.colores['reset']}")

    # =================================================================
    # === Generación de contraseñas ===
    # =================================================================
    def generar_contrasena(self, longitud=12):
        """Genera una contraseña aleatoria con la longitud especificada"""
        return ''.join(random.choice(self.caracteres_completos) for _ in range(longitud))

    # =================================================================
    # === Persistencia en archivo (carpeta ~/pypher del usuario) ===
    # =================================================================
    def guardar_archivo(self, contrasena, nombre_archivo, fecha=None, subcarpeta=None):
        """Guarda la contraseña en un archivo de texto con formato en la carpeta ~/pypher"""
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
║  Fortaleza         : {stats['nivel'] + ' (' + str(stats['puntaje']) + '/' + str(stats['max_puntaje']) + ' - ' + str(stats['porcentaje']) + '%)':<43} ║
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

    def guardar_analisis(self, contrasena, stats, nombre_archivo, subcarpeta=None):
        """Guarda el reporte detallado de un análisis de contraseña en un
        archivo de texto en la carpeta ~/pypher (o subcarpeta indicada)."""
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        detalles_txt = "\n".join(f"  {d}" for d in stats["detalles"])

        contenido = f"""========================================
    Pypher - Análisis de Contraseña
========================================

📅 Fecha: {fecha}
🔐 Contraseña analizada: {contrasena}

🔒 Nivel de seguridad: {stats['nivel']} ({stats['puntaje']}/{stats['max_puntaje']} - {stats['porcentaje']}%)

📊 Estadísticas:
- Longitud: {stats['longitud']} caracteres
- Mayúsculas: {stats['mayusculas']}
- Minúsculas: {stats['minusculas']}
- Números: {stats['digitos']}
- Símbolos: {stats['simbolos']}

📋 Detalles del análisis:
{detalles_txt}

💬 {stats['descripcion']}

========================================
    Generado con Pypher
    https://github.com/tu-usuario/pypher
========================================
"""

        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'

        if subcarpeta:
            ruta_carpeta = os.path.join(self.documentos_path, subcarpeta)
            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)
        else:
            ruta_carpeta = self.documentos_path

        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)

        try:
            with open(ruta_completa, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print(f"{self.colores['verde']}│ ✓ Análisis guardado en: {self.colores['blanco']}{ruta_completa}{self.colores['reset']}")
            return True
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al guardar: {str(e)}{self.colores['reset']}")
            return False

    def mostrar_historial(self, archivo="historial.txt", subcarpeta=None):
        """Muestra el historial de contraseñas guardadas desde la carpeta ~/pypher"""
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


class WordlistGenerator:
    """
    === Módulo 3: Generador de Wordlists ===
    RESTRICCIÓN CRÍTICA: nunca genera más de MAX_VARIANTES contraseñas
    (constante definida al inicio del módulo) en una sola ejecución,
    sin importar el modo usado, para evitar un
    consumo excesivo de RAM/disco. El corte se aplica con un contador
    dentro de cada generador (yield), así que nunca se materializa en
    memoria más de lo permitido.
    """

    # -----------------------------------------------------------------
    # === Datos base para la generación inteligente ===
    # -----------------------------------------------------------------
    SIMBOLOS_FINALES = ["!", "@", "#", "$", "*", "?", "01", "123"]
    ANIOS = [str(a) for a in range(1990, 2027)]
    NUMEROS_COMUNES = ["01", "123", "1234", "4321", "0000", "9999"]
    PREFIJOS = ["admin_", "user_", "pass_", "root_", "system_", "!", "@", "#", "$"]

    # Sustituciones leetspeak: cada letra puede mapear a varios símbolos.
    LEETSPEAK = {
        "a": ["@", "4", "Á"],
        "e": ["3", "É"],
        "i": ["1", "Í"],
        "o": ["0", "Ó"],
        "s": ["5", "$", "Z"],
        "t": ["7", "+"],
        "b": ["8", "6"],
        "g": ["9", "6"],
        "l": ["1", "¡"],
        "z": ["2"],
        "c": ["(", "<"],
        "u": ["v"],
        "m": ["n", "r", "w"],
    }

    # Sustitución simple (compatibilidad con el modo "Mutaciones" clásico)
    SUSTITUCIONES = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "5"}

    # Patrones de teclado/palabras que la gente realmente usa (en vez de
    # fuerza bruta ciega tipo "aaa", "aab", "aac"...)
    PATRONES_TECLADO = [
        "abc", "abcd", "qwerty", "asdf", "zxcv", "123", "1234",
        "2024", "2025", "2026", "admin", "user", "pass", "root",
    ]

    # Diccionario base: 200 palabras/contraseñas comunes.
    DICCIONARIO_BASE = [
    '123456', 'password', '123456789', '12345', '12345678', '1234567',
    'qwerty', '1234567890', '1234', '111111', '123123', '12345678910',
    'admin', 'iloveyou', '1234567890', 'password123', '123321', '000000',
    '1111', 'root', '666666', '12345678901', '123456789012', 'qwertyuiop',
    'asdfghjkl', 'qwert', '1234567890qwe', '1234567890123', 'princess', '12345678901234',
    'monkey', '123456789012345', '1234567890123456', 'dragon', '12345678901234567', '123456789012345678',
    'sunshine', '1234567890123456789', '12345678901234567890', 'letmein', 'baseball', 'trustno1',
    'superman', 'master', '1234567890qwer', 'welcome', 'pass', 'football',
    '1234567890asdf', 'password1', '1234567890zxcv', 'admin123', '1234567890qwerty', '1234567890asdfgh',
    '1234567890zxcvbn', '123456789011', '123456789022', '123456789033', '123456789044', '123456789055',
    '123456789066', '123456789077', '123456789088', '123456789099', '123456789000', 'qwerty123456',
    'asdfghjkl123', 'zxcvbnm123456', '123456qwerty', '123456asdfgh', '123456zxcvbn', '123qwerty',
    '123asdfgh', '123zxcvbn', 'qwertyuiop123', 'qazwsxedc', 'asdf', '1234567890!',
    '1234567890@', '1234567890#', '1234567890$', '1234567890%', '1234567890^', '1234567890&',
    '1234567890*', '1234567890(', '1234567890)', '1234567890-', '1234567890_', '1234567890=',
    '1234567890+', '1234567890[', '1234567890]', '1234567890{', '1234567890}', '1234567890\\',
    '1234567890|', '1234567890;', '1234567890:', "1234567890'", '1234567890"', '1234567890,',
    '1234567890<', '1234567890.', '1234567890>', '1234567890/', '1234567890?', '1234567890`',
    '1234567890~', 'michael', 'joshua', 'matthew', 'daniel', 'david',
    'joseph', 'andrew', 'james', 'john', 'robert', 'william',
    'christopher', 'thomas', 'charles', 'richard', 'mary', 'patricia',
    'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 'jessica',
    'sarah', 'karen', 'nancy', 'lisa', 'betty', 'margaret',
    'sandra', 'ashley', 'kimberly', 'emily', 'donna', 'michelle',
    'dorothy', 'carol', 'amanda', 'melissa', 'deborah', 'stephanie',
    'rebecca', 'sharon', 'laura', 'cynthia', 'kathleen', 'amy',
    'shirley', 'angela', 'helen', 'anna', 'brenda', 'pamela',
    'nicole', 'emma', 'samantha', 'katherine', 'christine', 'debra',
    'rachel', 'catherine', 'carolyn', 'janet', 'ruth', 'maria',
    'heather', 'diane', 'virginia', 'julie', 'joyce', 'victoria',
    'olivia', 'kelly', 'christina', 'lauren', 'joan', 'evelyn',
    'judith', 'megan', 'andrea', 'cheryl', 'hannah', 'jacqueline',
    'martha', 'gloria', 'teresa', 'ann', 'sara', 'madison',
    'frances', 'kathryn',
    ]

  # Palabras clave muy comunes en español e internacionalmente
NUEVAS_PALABRAS = [
    'hola', 'teamo', 'amigos', 'familia', 'contraseña', 'sistemas',
    'invitado', 'soporte', 'prueba', 'temporal', 'santiago', 'carlos',
    'alejandro', 'maria', 'juan', 'pepito', '1234567890ñ'
]

# Cultura pop, deportes y marcas (muy utilizadas)
CULTURA_POP = [
    'starwars', 'pokemon', 'batman', 'superman', 'naruto', 'matrix',
    'harrypotter', 'gandalf', 'marvel', 'avengers', 'metallica', 
    'barcelona', 'realmadrid', 'lakers', 'yankees', 'chelsea', 'america'
]

# Patrones de teclado avanzados (diagonales y zig-zag)
TECLADO_AVANZADO = [
    'qazwsx', 'wsxedc', 'edcrfv', 'tgbvhu', 'yhnmju', 'ujmiko',
    '1qaz2wsx', '1qaz', '1qazxsw2', 'qweasdzxc', 'zxcvbnm', 'mnbvcxz',
    'poiuytrewq', 'lkjhgfdsa'
]

# Nombres de mascotas comunes
MASCOTAS = [
    'luna', 'bella', 'max', 'charlie', 'lucy', 'cooper', 'daisy', 
    'rocky', 'toby', 'lola', 'simba', 'nala'
]

# Actualización de tu diccionario base
DICCIONARIO_BASE.extend(NUEVAS_PALABRAS + CULTURA_POP + TECLADO_AVANZADO + MASCOTAS)

    def __init__(self, colores: dict, documentos_path: str) -> None:
        """Args:
            colores: Paleta de colores ANSI compartida con el resto del programa.
            documentos_path: Carpeta donde se guardarán las wordlists generadas.
        """
        self.colores = colores
        self.documentos_path = documentos_path

    # -----------------------------------------------------------------
    # === Barra de progreso en tiempo real ===
    # -----------------------------------------------------------------
    def _mostrar_progreso(self, actual: int, total_referencia: int) -> None:
        """Imprime/actualiza una barra de progreso en la misma línea de
        terminal, usada durante la generación de wordlists grandes."""
        total_referencia = max(total_referencia, 1)
        porcentaje = min(int((actual / total_referencia) * 100), 100)
        bar_len = 24
        filled = int((porcentaje / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(
            f"\r{self.colores['morado']}│ {self.colores['gris']}[{self.colores['verde']}{bar}"
            f"{self.colores['gris']}] {self.colores['blanco']}{porcentaje:>3}% "
            f"{self.colores['gris']}({actual}/{total_referencia}){self.colores['reset']}",
            end="", flush=True
        )
        if actual >= total_referencia:
            print()

    def _advertir_si_excede(self, total_posible: int) -> None:
        """Imprime una advertencia si el número de variantes posibles
        supera ``MAX_VARIANTES`` (el resultado real se trunca en el
        generador correspondiente, nunca aquí)."""
        if total_posible > MAX_VARIANTES:
            print(
                f"{self.colores['naranja']}│ ⚠ Se solicitaron/son posibles {total_posible} variantes, "
                f"pero el límite de seguridad es de {MAX_VARIANTES}. Se truncará automáticamente."
                f"{self.colores['reset']}"
            )

    # -----------------------------------------------------------------
    # === Utilidades de mutación (usadas por todos los modos) ===
    # -----------------------------------------------------------------
    def _mayusculas_alternadas(self, palabra):
        """Ej: 'password' -> 'PaSsWoRd'"""
        return "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(palabra))

    def _duplicados_parciales(self, palabra):
        """Genera duplicados parciales realistas: 'abcd' -> 'abcdab', 'ababcd', 'abcdabcd'."""
        variantes = []
        n = len(palabra)
        if n >= 2:
            mitad = max(n // 2, 1)
            variantes.append(palabra + palabra[:mitad])          # abcdab
            variantes.append(palabra[:mitad] + palabra)           # ababcd (aprox.)
            variantes.append(palabra + palabra)                   # abcdabcd
        return variantes

    def _variantes_leet(self, palabra, max_variantes=8):
        """Aplica sustituciones leetspeak MÚLTIPLES Y SIMULTÁNEAS sobre la
        misma palabra (no solo una letra a la vez), devolviendo hasta
        max_variantes formas distintas, incluida la sustitución completa
        (todas las letras posibles sustituidas) y combinaciones parciales."""
        posiciones = [(i, c.lower()) for i, c in enumerate(palabra) if c.lower() in self.LEETSPEAK]
        if not posiciones:
            return [palabra]

        variantes = {palabra}

        # Sustitución completa (todas las letras sustituibles a la vez)
        completa = list(palabra)
        for i, c in posiciones:
            completa[i] = self.LEETSPEAK[c][0]
        variantes.add("".join(completa))

        # Combinaciones parciales/aleatorias con sustitutos alternativos
        intentos = 0
        while len(variantes) < max_variantes and intentos < max_variantes * 5:
            intentos += 1
            nueva = list(palabra)
            for i, c in posiciones:
                if random.random() < 0.65:
                    nueva[i] = random.choice(self.LEETSPEAK[c])
            variantes.add("".join(nueva))

        return list(variantes)[:max_variantes]

    def generar_variantes_palabra(self, palabra_base, max_variantes=50):
        """
        MOTOR DE MUTACIONES: a partir de UNA palabra base genera hasta
        max_variantes formas realistas y únicas, combinando:
          - Leetspeak múltiple/simultáneo (ej. 'password' -> 'P@$$w0rd')
          - Mayúsculas alternadas, capitalizado, todo mayús./minús.
          - Reverso de la palabra
          - Duplicados parciales
          - Combinaciones de todo lo anterior
        Nunca supera max_variantes (protección de memoria).
        """
        base_limpia = palabra_base.strip()
        if not base_limpia:
            return []

        formas = set()

        formas_estilo = [
            base_limpia.lower(),
            base_limpia.upper(),
            base_limpia.capitalize(),
            self._mayusculas_alternadas(base_limpia),
            base_limpia[::-1].lower(),
            base_limpia[::-1].capitalize(),
        ]
        formas_estilo.extend(self._duplicados_parciales(base_limpia.lower()))

        for forma in formas_estilo:
            if len(formas) >= max_variantes:
                break
            formas.add(forma)
            for variante_leet in self._variantes_leet(forma, max_variantes=6):
                formas.add(variante_leet)
                if len(formas) >= max_variantes:
                    break

        return list(formas)[:max_variantes]

    # -----------------------------------------------------------------
    # 1) NUEVO — Generación inteligente (modo recomendado por defecto)
    # -----------------------------------------------------------------
    def generar_inteligente(self, palabras_extra=None, incluir_diccionario=True, aplicar_afijos=True):
        """
        MODO RECOMENDADO. Usa un diccionario interno (>100 palabras
        realmente usadas en contraseñas) + palabras personalizadas
        opcionales. A cada palabra le aplica el motor de mutaciones
        (hasta 50 variantes) y luego prefijos/sufijos realistas (años,
        números comunes, símbolos). Corta estrictamente en MAX_VARIANTES,
        sin duplicados.
        """
        palabras = []
        if incluir_diccionario:
            palabras.extend(self.DICCIONARIO_BASE)
        if palabras_extra:
            palabras.extend(p.strip() for p in palabras_extra if p.strip())
        palabras = list(dict.fromkeys(palabras))  # sin duplicados, conserva orden

        if not palabras:
            return

        sufijos = [""] + self.ANIOS + self.SIMBOLOS_FINALES + self.NUMEROS_COMUNES
        prefijos = [""] + (self.PREFIJOS if aplicar_afijos else [])

        total_estimado = len(palabras) * 50 * len(sufijos) * len(prefijos)
        self._advertir_si_excede(total_estimado)

        contador = 0
        vistos = set()
        for palabra in palabras:
            for forma in self.generar_variantes_palabra(palabra, max_variantes=50):
                for prefijo in prefijos:
                    for sufijo in sufijos:
                        candidata = f"{prefijo}{forma}{sufijo}"
                        if candidata in vistos:
                            continue
                        vistos.add(candidata)
                        if contador >= MAX_VARIANTES:
                            return
                        contador += 1
                        yield candidata

    # -----------------------------------------------------------------
    # 2) Diccionario personalizado (palabras del usuario + mutaciones)
    # -----------------------------------------------------------------
    def generar_diccionario_personalizado(self, texto_palabras, incluir_interno=False):
        """Recibe palabras separadas por coma ingresadas por el usuario,
        les aplica el motor de mutaciones completo (leetspeak, mayúsculas
        alternadas, reverso, duplicados, prefijos/sufijos). Opcionalmente
        añade también el diccionario interno."""
        palabras_usuario = [p.strip() for p in texto_palabras.split(",") if p.strip()]
        yield from self.generar_inteligente(palabras_extra=palabras_usuario, incluir_diccionario=incluir_interno)

    # -----------------------------------------------------------------
    # 3) Fuerza bruta: caracteres personalizados + rango de longitudes
    #    (o, por defecto, patrones realistas en vez de fuerza bruta ciega)
    # -----------------------------------------------------------------
    def generar_fuerza_bruta(self, caracteres, longitud_min, longitud_max, patrones=False):
        """
        Si patrones=True (recomendado): en vez de recorrer TODAS las
        combinaciones de 'caracteres' (que produce basura tipo 'aaa',
        'aab', 'aac'...), genera combinaciones a partir de patrones de
        teclado/palabras comunes (abc, qwerty, admin, 1234...) + sufijos
        realistas — mucho más útil para auditorías.

        Si patrones=False (comportamiento original): fuerza bruta pura
        sobre el conjunto de caracteres indicado. Solo debería usarse si
        el usuario la solicita explícitamente. Corta en MAX_VARIANTES.
        """
        if patrones:
            sufijos = [""] + self.SIMBOLOS_FINALES + self.ANIOS[-6:] + self.NUMEROS_COMUNES
            total_posible = len(self.PATRONES_TECLADO) * 3 * len(sufijos)
            self._advertir_si_excede(total_posible)

            contador = 0
            vistos = set()
            for patron in self.PATRONES_TECLADO:
                for forma in (patron, patron.upper(), patron.capitalize()):
                    for sufijo in sufijos:
                        candidata = f"{forma}{sufijo}"
                        if candidata in vistos:
                            continue
                        vistos.add(candidata)
                        if contador >= MAX_VARIANTES:
                            return
                        contador += 1
                        yield candidata
            return

        # ---- Fuerza bruta pura (comportamiento original, sin cambios) ----
        caracteres = list(dict.fromkeys(caracteres))  # sin duplicados, conserva orden
        total_posible = sum(len(caracteres) ** l for l in range(longitud_min, longitud_max + 1))
        self._advertir_si_excede(total_posible)

        contador = 0
        for longitud in range(longitud_min, longitud_max + 1):
            for combinacion in itertools.product(caracteres, repeat=longitud):
                if contador >= MAX_VARIANTES:
                    return
                contador += 1
                yield ''.join(combinacion)

    # -----------------------------------------------------------------
    # 4) Mutaciones a partir de una única palabra base (modo clásico,
    #    ahora reutiliza el motor de mutaciones completo)
    # -----------------------------------------------------------------
    def generar_mutaciones(self, palabra_base):
        """Genera variantes de una palabra base: motor de mutaciones
        completo (leetspeak múltiple, mayúsculas alternadas, reverso,
        duplicados) + años (1990-2026) y símbolos finales como sufijos.
        Corta en MAX_VARIANTES."""
        formas_base = self.generar_variantes_palabra(palabra_base, max_variantes=50)
        sufijos = [""] + self.ANIOS + self.SIMBOLOS_FINALES

        total_posible = len(formas_base) * len(sufijos)
        self._advertir_si_excede(total_posible)

        contador = 0
        for forma in formas_base:
            for sufijo in sufijos:
                if contador >= MAX_VARIANTES:
                    return
                contador += 1
                yield f"{forma}{sufijo}"

    # -----------------------------------------------------------------
    # 5) Combinaciones de dos listas (ej. nombres + apellidos), ahora con
    #    mutaciones opcionales por elemento y varios separadores
    # -----------------------------------------------------------------
    def generar_combinaciones(self, lista1, lista2, separador="", aplicar_mutaciones=False, separadores=None):
        """Une dos listas de palabras mediante producto cartesiano.
        Si aplicar_mutaciones=True, primero aplica el motor de mutaciones
        a CADA elemento de ambas listas (leetspeak, mayúsculas, reverso...)
        antes de combinarlas — ej. 'Juan'+'Perez' -> 'Ju@n_P3r3z!'.
        Si separadores (lista) se indica, se prueba cada uno; si no, se usa
        únicamente 'separador'. Si el resultado supera MAX_VARIANTES,
        trunca y avisa."""
        lista1 = [p.strip() for p in lista1 if p.strip()]
        lista2 = [p.strip() for p in lista2 if p.strip()]

        if aplicar_mutaciones:
            lista1_final, lista2_final = [], []
            for palabra in lista1:
                lista1_final.extend(self.generar_variantes_palabra(palabra, max_variantes=15))
            for palabra in lista2:
                lista2_final.extend(self.generar_variantes_palabra(palabra, max_variantes=15))
            lista1_final = list(dict.fromkeys(lista1_final))
            lista2_final = list(dict.fromkeys(lista2_final))
        else:
            lista1_final, lista2_final = lista1, lista2

        if len(lista1_final) > MAX_VARIANTES:
            print(
                f"{self.colores['naranja']}│ ⚠ La primera lista tiene {len(lista1_final)} elementos, "
                f"se usarán solo los primeros {MAX_VARIANTES}.{self.colores['reset']}"
            )
            lista1_final = lista1_final[:MAX_VARIANTES]
        if len(lista2_final) > MAX_VARIANTES:
            print(
                f"{self.colores['naranja']}│ ⚠ La segunda lista tiene {len(lista2_final)} elementos, "
                f"se usarán solo los primeros {MAX_VARIANTES}.{self.colores['reset']}"
            )
            lista2_final = lista2_final[:MAX_VARIANTES]

        seps = separadores if separadores else [separador]

        total_posible = len(lista1_final) * len(lista2_final) * len(seps)
        self._advertir_si_excede(total_posible)

        contador = 0
        for palabra1 in lista1_final:
            for palabra2 in lista2_final:
                for sep in seps:
                    if contador >= MAX_VARIANTES:
                        return
                    contador += 1
                    yield f"{palabra1}{sep}{palabra2}"

    # -----------------------------------------------------------------
    # === Filtro de longitud (usado por el flujo interactivo) ===
    # -----------------------------------------------------------------
    def _preguntar_filtro_longitud(self) -> tuple:
        """Pregunta al usuario si quiere filtrar por longitud.
        Returns: (min_len, max_len) o (None, None) si no hay filtro."""
        aplicar = input(f"{self.colores['morado']}│ {self.colores['azul']}¿Filtrar por longitud? (s/n): {self.colores['reset']}").strip().lower()
        if aplicar != 's':
            return None, None

        try:
            min_len = input(f"{self.colores['morado']}│ {self.colores['azul']}Longitud mínima [Enter para omitir]: {self.colores['reset']}").strip()
            max_len = input(f"{self.colores['morado']}│ {self.colores['azul']}Longitud máxima [Enter para omitir]: {self.colores['reset']}").strip()

            min_len = int(min_len) if min_len else None
            max_len = int(max_len) if max_len else None

            if min_len is not None and min_len < 1:
                print(f"{self.colores['rojo']}│ ✗ La longitud mínima debe ser al menos 1{self.colores['reset']}")
                return None, None
            if min_len is not None and max_len is not None and min_len > max_len:
                print(f"{self.colores['rojo']}│ ✗ La longitud mínima no puede ser mayor que la máxima{self.colores['reset']}")
                return None, None

            return min_len, max_len
        except ValueError:
            print(f"{self.colores['rojo']}│ ✗ Ingresa números válidos{self.colores['reset']}")
            return None, None

    # -----------------------------------------------------------------
    # === Persistencia en archivo (.txt o .gz) dentro de ~/pypher ===
    # -----------------------------------------------------------------
    def guardar_wordlist(self, generador, nombre_archivo, comprimir=False, subcarpeta=None, min_len=None, max_len=None):
        """Consume el generador de palabras (yield) y escribe cada línea
        en disco, respetando siempre ``MAX_VARIANTES`` como tope
        absoluto. Opcionalmente comprime el resultado con gzip.
        Filtra por longitud si se especifica min_len y/o max_len.

        Args:
            generador: Iterable/generador que produce cada contraseña candidata.
            nombre_archivo: Nombre base del archivo de salida (se añade extensión).
            comprimir: Si ``True``, el archivo final se guarda como ``.gz``.
            subcarpeta: Subcarpeta opcional dentro de ``documentos_path``.
            min_len: Longitud mínima aceptada (inclusive), o ``None`` para no filtrar.
            max_len: Longitud máxima aceptada (inclusive), o ``None`` para no filtrar.

        Returns:
            tuple[str | None, int]: Ruta completa del archivo guardado (o
            ``None`` si falló) y el número de contraseñas escritas.
        """
        if subcarpeta:
            ruta_carpeta = os.path.join(self.documentos_path, subcarpeta)
            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)
        else:
            ruta_carpeta = self.documentos_path

        if comprimir:
            if not nombre_archivo.endswith(".gz"):
                if not nombre_archivo.endswith(".txt"):
                    nombre_archivo += ".txt"
                nombre_archivo += ".gz"
        elif not nombre_archivo.endswith(".txt"):
            nombre_archivo += ".txt"

        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)

        print(f"\n{self.colores['morado']}│ {self.colores['verde']}Generando wordlist (límite {MAX_VARIANTES})...{self.colores['reset']}")

        try:
            if comprimir:
                archivo = gzip.open(ruta_completa, "wt", encoding="utf-8")
            else:
                archivo = open(ruta_completa, "w", encoding="utf-8")

            contador = 0
            with archivo:
                for palabra in generador:
                    if min_len is not None and len(palabra) < min_len:
                        continue
                    if max_len is not None and len(palabra) > max_len:
                        continue
                    archivo.write(palabra + "\n")
                    contador += 1
                    self._mostrar_progreso(contador, MAX_VARIANTES)

            if contador == 0:
                if min_len is not None or max_len is not None:
                    print(f"{self.colores['rojo']}│ ⚠ No se generó ninguna contraseña con el rango de longitud especificado{self.colores['reset']}")
                else:
                    print(f"{self.colores['rojo']}│ ✗ No se generó ninguna contraseña{self.colores['reset']}")
                return None, 0
            if contador < MAX_VARIANTES:
                # Cierra la barra de progreso en el 100% relativo a lo realmente generado
                self._mostrar_progreso(contador, contador)

            print(f"{self.colores['verde']}│ ✓ Wordlist generada: {self.colores['blanco']}{contador} contraseñas{self.colores['reset']}")
            if contador >= MAX_VARIANTES:
                print(
                    f"{self.colores['naranja']}│ ⚠ Se alcanzó el límite de seguridad "
                    f"({MAX_VARIANTES} variantes). La wordlist fue truncada.{self.colores['reset']}"
                )
            print(f"{self.colores['verde']}│ ✓ Guardada en: {self.colores['blanco']}{ruta_completa}{self.colores['reset']}")
            return ruta_completa, contador
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al guardar wordlist: {str(e)}{self.colores['reset']}")
            return None, 0

    # -----------------------------------------------------------------
    # === Acceso rápido: alias en ~/.bashrc ===
    # -----------------------------------------------------------------
    def mostrar_alias_rapido(self) -> None:
        """Muestra instrucciones para crear un acceso directo ('pypher')
        adaptadas automáticamente al shell del usuario (Bash, Zsh, Fish
        u otro) y a la ruta real donde está instalado el script.

        No depende de una ruta fija ni de un shell concreto: detecta el
        shell activo con la variable de entorno ``SHELL`` y calcula la
        ruta absoluta del propio archivo con ``os.path.abspath(__file__)``.
        También ofrece la alternativa de crear un comando global del
        sistema mediante un enlace simbólico en ``/usr/local/bin``.
        """
        c = self.colores
        ruta_script = os.path.abspath(__file__) if "__file__" in globals() else "/ruta/completa/a/pypher_linux.py"
        shell_path = os.environ.get("SHELL", "")
        shell_nombre = os.path.basename(shell_path).lower() if shell_path else ""

        print(f"{c['morado']}│ {c['gris']}💡 Acceso rápido: crea un comando 'pypher' para no escribir la ruta completa.{c['reset']}")

        if shell_nombre == "bash":
            print(f"{c['morado']}│ {c['cyan']}   Bash — añade esto a ~/.bashrc:{c['reset']}")
            print(
                f"{c['morado']}│ {c['blanco']}   echo 'alias pypher=\"python3 {ruta_script}\"' >> ~/.bashrc "
                f"&& source ~/.bashrc{c['reset']}"
            )
        elif shell_nombre == "zsh":
            print(f"{c['morado']}│ {c['cyan']}   Zsh — añade esto a ~/.zshrc:{c['reset']}")
            print(
                f"{c['morado']}│ {c['blanco']}   echo 'alias pypher=\"python3 {ruta_script}\"' >> ~/.zshrc "
                f"&& source ~/.zshrc{c['reset']}"
            )
        elif shell_nombre == "fish":
            print(f"{c['morado']}│ {c['cyan']}   Fish — añade esto a ~/.config/fish/config.fish:{c['reset']}")
            print(
                f"{c['morado']}│ {c['blanco']}   echo 'alias pypher \"python3 {ruta_script}\"' >> "
                f"~/.config/fish/config.fish && source ~/.config/fish/config.fish{c['reset']}"
            )
        else:
            # Fallback para shells no detectados (ksh, dash, tcsh, SHELL vacío, etc.)
            print(f"{c['morado']}│ {c['naranja']}   No se detectó automáticamente tu shell ({shell_nombre or 'desconocido'}).{c['reset']}")
            print(f"{c['morado']}│ {c['gris']}   Añade una línea equivalente a tu alias a la configuración de tu shell:{c['reset']}")
            print(f"{c['morado']}│ {c['blanco']}   alias pypher=\"python3 {ruta_script}\"{c['reset']}")

        print(f"{c['morado']}│{c['reset']}")
        print(f"{c['morado']}│ {c['gris']}   Alternativa multiplataforma — comando global del sistema:{c['reset']}")
        print(
            f"{c['morado']}│ {c['blanco']}   sudo ln -s {ruta_script} /usr/local/bin/pypher{c['reset']}"
        )
        print(f"{c['morado']}│ {c['gris']}   (requiere que {ruta_script} tenga permiso de ejecución: chmod +x {ruta_script}){c['reset']}")
        print(f"{c['morado']}│ {c['gris']}   También puedes ejecutar {c['blanco']}./install.sh{c['gris']} en la raíz del proyecto para hacerlo de forma interactiva.{c['reset']}")
        print(f"{c['morado']}│ {c['gris']}   Después, solo escribe {c['blanco']}pypher{c['gris']} para ejecutar el programa.{c['reset']}")

    # -----------------------------------------------------------------
    # === Flujo interactivo (menú) ===
    # -----------------------------------------------------------------
    def generar_wordlist_interactivo(self) -> None:
        """Flujo interactivo del menú 'Generar wordlist': pregunta al
        usuario el modo de generación deseado (inteligente, diccionario,
        mutaciones, combinaciones o fuerza bruta) y delega en el
        generador correspondiente, guardando el resultado en disco."""
        print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}GENERADOR DE WORDLISTS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['gris']}Límite de seguridad: {MAX_VARIANTES} variantes por ejecución{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[1]{self.colores['blanco']}  🧠 Generación inteligente (recomendado)")
        print(f"{self.colores['morado']}│ {self.colores['cyan']}[2]{self.colores['blanco']}  📖 Diccionario personalizado (tus propias palabras)")
        print(f"{self.colores['morado']}│ {self.colores['amarillo']}[3]{self.colores['blanco']}  🔤 Mutaciones (una sola palabra base)")
        print(f"{self.colores['morado']}│ {self.colores['azul']}[4]{self.colores['blanco']}  🔗 Combinaciones (dos listas de palabras)")
        print(f"{self.colores['morado']}│ {self.colores['naranja']}[5]{self.colores['blanco']}  💥 Fuerza bruta (patrones realistas o pura)")

        modo = input(f"{self.colores['morado']}│ {self.colores['verde']}➤ {self.colores['reset']}").strip()

        generador = None
        if modo == "1":
            print(f"{self.colores['morado']}│ {self.colores['gris']}Ej. 'admin' -> P@$$w0rd, Adm1n2024, @DMIN!, ...{self.colores['reset']}")
            extra = input(
                f"{self.colores['morado']}│ {self.colores['azul']}Palabras extra, separadas por coma (opcional, Enter para omitir): {self.colores['reset']}"
            ).strip()
            palabras_extra = [p.strip() for p in extra.split(",") if p.strip()] if extra else None
            generador = self.generar_inteligente(palabras_extra=palabras_extra, incluir_diccionario=True)

        elif modo == "2":
            palabras_texto = input(
                f"{self.colores['morado']}│ {self.colores['azul']}Tus palabras, separadas por coma (ej. nombredelamascota,equipo): {self.colores['reset']}"
            ).strip()
            if not palabras_texto:
                print(f"{self.colores['rojo']}│ ✗ Debes indicar al menos una palabra{self.colores['reset']}")
                return
            incluir_interno = input(
                f"{self.colores['morado']}│ {self.colores['azul']}¿Añadir también el diccionario interno? (s/n): {self.colores['reset']}"
            ).strip().lower() == 's'
            generador = self.generar_diccionario_personalizado(palabras_texto, incluir_interno=incluir_interno)

        elif modo == "3":
            palabra_base = input(f"{self.colores['morado']}│ {self.colores['azul']}Palabra base: {self.colores['reset']}").strip()
            if not palabra_base:
                print(f"{self.colores['rojo']}│ ✗ Debes indicar una palabra base{self.colores['reset']}")
                return
            print(f"{self.colores['morado']}│ {self.colores['gris']}Ejemplo: {', '.join(self.generar_variantes_palabra(palabra_base, max_variantes=5))}...{self.colores['reset']}")
            generador = self.generar_mutaciones(palabra_base)

        elif modo == "4":
            entrada1 = input(f"{self.colores['morado']}│ {self.colores['azul']}Primera lista, separada por comas (ej. Juan,Ana): {self.colores['reset']}").strip()
            entrada2 = input(f"{self.colores['morado']}│ {self.colores['azul']}Segunda lista, separada por comas (ej. Perez,Lopez): {self.colores['reset']}").strip()
            if not entrada1 or not entrada2:
                print(f"{self.colores['rojo']}│ ✗ Ambas listas son obligatorias{self.colores['reset']}")
                return
            aplicar_mutaciones = input(
                f"{self.colores['morado']}│ {self.colores['azul']}¿Aplicar mutaciones a cada palabra antes de combinar? (s/n): {self.colores['reset']}"
            ).strip().lower() == 's'
            usar_varios_separadores = input(
                f"{self.colores['morado']}│ {self.colores['azul']}¿Probar varios separadores (_ - . espacio)? (s/n): {self.colores['reset']}"
            ).strip().lower() == 's'
            separadores = ["", "_", "-", ".", " "] if usar_varios_separadores else None
            separador = "" if usar_varios_separadores else input(
                f"{self.colores['morado']}│ {self.colores['azul']}Separador (opcional, Enter para ninguno): {self.colores['reset']}"
            )
            lista1 = [p.strip() for p in entrada1.split(",") if p.strip()]
            lista2 = [p.strip() for p in entrada2.split(",") if p.strip()]
            generador = self.generar_combinaciones(
                lista1, lista2, separador=separador,
                aplicar_mutaciones=aplicar_mutaciones, separadores=separadores
            )

        elif modo == "5":
            usar_patrones = input(
                f"{self.colores['morado']}│ {self.colores['azul']}¿Usar patrones realistas (abc, qwerty, admin...) en vez de fuerza bruta pura? (s/n, recomendado s): {self.colores['reset']}"
            ).strip().lower() != 'n'

            if usar_patrones:
                generador = self.generar_fuerza_bruta("", 0, 0, patrones=True)
            else:
                print(f"{self.colores['morado']}│{self.colores['reset']}")
                print(f"{self.colores['morado']}│ {self.colores['azul']}Conjuntos de caracteres a incluir (elige uno o varios):{self.colores['reset']}")
                print(f"{self.colores['morado']}│ {self.colores['verde']}[1]{self.colores['blanco']} Minúsculas (a-z)")
                print(f"{self.colores['morado']}│ {self.colores['verde']}[2]{self.colores['blanco']} Mayúsculas (A-Z)")
                print(f"{self.colores['morado']}│ {self.colores['verde']}[3]{self.colores['blanco']} Números (0-9)")
                print(f"{self.colores['morado']}│ {self.colores['verde']}[4]{self.colores['blanco']} Símbolos (!@#$%&()-_=+[]{{}}?)")
                print(f"{self.colores['morado']}│ {self.colores['gris']} Ejemplo: '1,3,4' para minúsculas + números + símbolos{self.colores['reset']}")
                seleccion = input(
                    f"{self.colores['morado']}│ {self.colores['azul']}Conjuntos (opcional, Enter para omitir): {self.colores['reset']}"
                ).strip()

                caracteres_predefinidos = ""
                mapa_conjuntos = {
                    "1": string.ascii_lowercase,
                    "2": string.ascii_uppercase,
                    "3": string.digits,
                    "4": "!@#$%&()-_=+[]{}?",
                }
                for opcion_conjunto in seleccion.split(","):
                    caracteres_predefinidos += mapa_conjuntos.get(opcion_conjunto.strip(), "")

                caracteres_custom = input(
                    f"{self.colores['morado']}│ {self.colores['azul']}Caracteres adicionales/personalizados (opcional, ej. abc123!@): {self.colores['reset']}"
                ).strip()

                caracteres = caracteres_predefinidos + caracteres_custom
                if not caracteres:
                    print(f"{self.colores['rojo']}│ ✗ Debes indicar al menos un carácter (conjunto predefinido o personalizado){self.colores['reset']}")
                    return
                try:
                    longitud_min = int(input(f"{self.colores['morado']}│ {self.colores['azul']}Longitud mínima: {self.colores['reset']}").strip() or "2")
                    longitud_max = int(input(f"{self.colores['morado']}│ {self.colores['azul']}Longitud máxima: {self.colores['reset']}").strip() or "3")
                    if longitud_min < 1 or longitud_max < longitud_min:
                        print(f"{self.colores['rojo']}│ ✗ Rango de longitud inválido{self.colores['reset']}")
                        return
                except ValueError:
                    print(f"{self.colores['rojo']}│ ✗ Ingresa números válidos{self.colores['reset']}")
                    return
                generador = self.generar_fuerza_bruta(caracteres, longitud_min, longitud_max, patrones=False)

        else:
            print(f"{self.colores['rojo']}│ ✗ Opción no válida{self.colores['reset']}")
            return

        min_len, max_len = self._preguntar_filtro_longitud()

        nombre = input(f"{self.colores['morado']}│ {self.colores['azul']}Nombre del archivo: {self.colores['reset']}").strip()
        if not nombre:
            print(f"{self.colores['rojo']}│ ✗ El nombre no puede estar vacío{self.colores['reset']}")
            return

        comprimir = input(f"{self.colores['morado']}│ {self.colores['azul']}¿Comprimir en .gz? (s/n): {self.colores['reset']}").strip().lower() == 's'
        subcarpeta = input(f"{self.colores['morado']}│ {self.colores['azul']}Subcarpeta (opcional, Enter para omitir): {self.colores['reset']}").strip()

        self.guardar_wordlist(generador, nombre, comprimir=comprimir,
                               subcarpeta=subcarpeta if subcarpeta else None,
                               min_len=min_len, max_len=max_len)


class AdvancedAnalyzer:
    """
    === Módulo 4: Estadísticas Avanzadas ===
    Complementa el puntaje 0-8 de calcular_puntaje_password con entropía,
    tiempo estimado de crackeo, detección de patrones y consulta opcional
    contra leaks locales.
    """

    VELOCIDADES = {
        "MD5":    {"GPU": 10_000_000_000, "CPU": 100_000_000},
        "SHA256": {"GPU": 5_000_000_000,  "CPU": 50_000_000},
        "bcrypt": {"GPU": 100_000,        "CPU": 10_000},
    }

    PALABRAS_DICCIONARIO = [
        "password", "contraseña", "contrasena", "love", "dragon", "master",
        "monkey", "football", "baseball", "welcome", "admin", "iloveyou",
        "princess", "sunshine", "shadow", "letmein", "freedom", "whatever",
        "qwerty", "trustno1",
    ]

    TECLADOS_ADYACENTES = [
        "qwertyuiop", "qwerty", "asdfghjkl", "asdf", "zxcvbnm", "zxcv",
        "1234567890", "poiuy", "lkjh", "mnbvc",
    ]

    def __init__(self, colores: dict, documentos_path: str) -> None:
        """Args:
            colores: Paleta de colores ANSI compartida con el resto del programa.
            documentos_path: Carpeta base (``~/pypher``) usada para guardar
                reportes y buscar el archivo opcional ``leaks_hashes.txt``.
        """
        self.colores = colores
        self.documentos_path = documentos_path

    # -----------------------------------------------------------------
    # a) Entropía en bits
    # -----------------------------------------------------------------
    def calcular_entropia(self, contrasena):
        """Entropía = longitud * log2(caracteres_posibles), estimando el
        espacio de caracteres a partir de los tipos presentes."""
        espacio = 0
        if any(c.islower() for c in contrasena):
            espacio += 26
        if any(c.isupper() for c in contrasena):
            espacio += 26
        if any(c.isdigit() for c in contrasena):
            espacio += 10
        if any(not c.isalnum() for c in contrasena):
            espacio += 32
        if espacio == 0 or len(contrasena) == 0:
            return 0.0
        return len(contrasena) * math.log2(espacio)

    # -----------------------------------------------------------------
    # b) Tiempo estimado de crackeo (MD5, SHA256, bcrypt · GPU/CPU)
    # -----------------------------------------------------------------
    def _formatear_tiempo(self, segundos: float) -> str:
        """Convierte un número de segundos en una cadena legible
        (segundos, minutos, horas, días, años o siglos), usada para
        mostrar los tiempos estimados de crackeo."""
        if segundos < 1:
            return "instantáneo (<1 segundo)"
        unidades = [
            ("siglos", 60 * 60 * 24 * 365 * 100),
            ("años", 60 * 60 * 24 * 365),
            ("días", 60 * 60 * 24),
            ("horas", 60 * 60),
            ("minutos", 60),
            ("segundos", 1),
        ]
        for nombre, factor in unidades:
            if segundos >= factor:
                valor = segundos / factor
                if valor > 1_000_000:
                    return f"{valor:.2e} {nombre} (prácticamente imposible)"
                return f"{valor:.1f} {nombre}"
        return f"{segundos:.1f} segundos"

    def calcular_tiempos_crackeo(self, entropia_bits):
        """Tiempo promedio de crackeo (se asume que en promedio hay que
        probar la mitad del espacio de combinaciones)."""
        combinaciones = 2 ** entropia_bits if entropia_bits > 0 else 1
        resultados = {}
        for algoritmo, velocidades in self.VELOCIDADES.items():
            resultados[algoritmo] = {}
            for tipo_hw, hashes_seg in velocidades.items():
                segundos = (combinaciones / 2) / hashes_seg
                resultados[algoritmo][tipo_hw] = self._formatear_tiempo(segundos)
        return resultados

    # -----------------------------------------------------------------
    # c) Detección de patrones
    # -----------------------------------------------------------------
    def _contiene_secuencia(self, texto, longitud_min):
        """Detecta secuencias ascendentes o descendentes (ej. 1234, abcd,
        4321) de al menos longitud_min caracteres consecutivos."""
        for i in range(len(texto) - longitud_min + 1):
            fragmento = texto[i:i + longitud_min]
            codigos = [ord(c) for c in fragmento]
            ascendente = all(codigos[j] + 1 == codigos[j + 1] for j in range(len(codigos) - 1))
            descendente = all(codigos[j] - 1 == codigos[j + 1] for j in range(len(codigos) - 1))
            if ascendente or descendente:
                return True
        return False

    def detectar_patrones(self, contrasena: str) -> list:
        """Analiza una contraseña en busca de patrones débiles conocidos:
        fechas, secuencias de teclado, secuencias ascendentes/descendentes,
        caracteres repetidos y palabras comunes de diccionario.

        Returns:
            list[str]: Lista de descripciones (con emoji) de cada patrón
            encontrado. Lista vacía si no se detectó ninguno.
        """
        patrones_encontrados = []
        texto = contrasena.lower()

        # Fechas dd/mm/aaaa o mm/dd/aaaa (con separador / - .)
        patron_fecha_1 = r"(0[1-9]|[12]\d|3[01])[/\-.](0[1-9]|1[0-2])[/\-.](19|20)\d{2}"
        patron_fecha_2 = r"(0[1-9]|1[0-2])[/\-.](0[1-9]|[12]\d|3[01])[/\-.](19|20)\d{2}"
        if re.search(patron_fecha_1, contrasena) or re.search(patron_fecha_2, contrasena):
            patrones_encontrados.append("📅 Contiene una fecha (dd/mm/aaaa o mm/dd/aaaa)")

        # Teclados adyacentes
        for patron in self.TECLADOS_ADYACENTES:
            if patron in texto or patron[::-1] in texto:
                patrones_encontrados.append(f"⌨️ Secuencia de teclado adyacente: '{patron}'")
                break

        # Secuencias ascendentes/descendentes (4+)
        if self._contiene_secuencia(texto, 4):
            patrones_encontrados.append("🔢 Contiene una secuencia ascendente/descendente (ej. 1234, abcd)")

        # Repeticiones (3+ del mismo carácter)
        if re.search(r"(.)\1{2,}", contrasena):
            patrones_encontrados.append("🔁 Contiene caracteres repetidos consecutivos (ej. 'aaa', '111')")

        # Palabras de diccionario básico
        for palabra in self.PALABRAS_DICCIONARIO:
            if palabra in texto:
                patrones_encontrados.append(f"📖 Contiene palabra común de diccionario: '{palabra}'")
                break

        return patrones_encontrados

    # -----------------------------------------------------------------
    # d) Frecuencia en leaks (opcional, archivo local leaks_hashes.txt)
    # -----------------------------------------------------------------
    def verificar_leaks(self, contrasena):
        """Si existe ~/pypher/leaks_hashes.txt, consulta el SHA1 de la
        contraseña contra ese archivo. Soporta líneas 'HASH' o
        'HASH:contador'. Devuelve None si el archivo no existe."""
        ruta_leaks = os.path.join(self.documentos_path, "leaks_hashes.txt")
        if not os.path.exists(ruta_leaks):
            return None

        sha1_contrasena = hashlib.sha1(contrasena.encode("utf-8")).hexdigest().upper()
        ocurrencias = 0
        try:
            with open(ruta_leaks, "r", encoding="utf-8", errors="ignore") as archivo:
                for linea in archivo:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(":")
                    hash_linea = partes[0].strip().upper()
                    if hash_linea == sha1_contrasena:
                        if len(partes) > 1:
                            try:
                                ocurrencias += int(partes[1])
                            except ValueError:
                                ocurrencias += 1
                        else:
                            ocurrencias += 1
        except Exception:
            return None

        return ocurrencias

    # -----------------------------------------------------------------
    # === Presentación en terminal ===
    # -----------------------------------------------------------------
    def mostrar_estadisticas_avanzadas(self, contrasena: str) -> dict:
        """Calcula e imprime en terminal el reporte avanzado completo de
        una contraseña: entropía, tiempos de crackeo estimados por
        algoritmo/hardware, patrones débiles detectados y, si existe
        ``leaks_hashes.txt``, su frecuencia en esa lista.

        Args:
            contrasena: Contraseña a analizar.

        Returns:
            dict: Diccionario con las claves ``entropia``, ``tiempos``,
            ``patrones`` y ``leaks``, útil para reutilizar los datos
            (p. ej. al guardar el análisis en un archivo).
        """
        entropia = self.calcular_entropia(contrasena)
        tiempos = self.calcular_tiempos_crackeo(entropia)
        patrones = self.detectar_patrones(contrasena)
        leaks = self.verificar_leaks(contrasena)

        print(f"\n{self.colores['morado']}╔{'═' * 60}╗{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']} {self.colores['negrita']}{self.colores['blanco']}📊 ESTADÍSTICAS AVANZADAS{self.colores['reset']}")
        print(f"{self.colores['morado']}╚{'═' * 60}╝{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['azul']}Entropía estimada: {self.colores['blanco']}{entropia:.1f} bits{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['blanco']}⏱ TIEMPO ESTIMADO DE CRACKEO (promedio):{self.colores['reset']}")
        for algoritmo, valores in tiempos.items():
            print(f"{self.colores['morado']}│ {self.colores['cyan']}{algoritmo}:{self.colores['reset']}")
            print(f"{self.colores['morado']}│   {self.colores['gris']}GPU: {self.colores['blanco']}{valores['GPU']}{self.colores['reset']}")
            print(f"{self.colores['morado']}│   {self.colores['gris']}CPU: {self.colores['blanco']}{valores['CPU']}{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['blanco']}🧩 PATRONES DETECTADOS:{self.colores['reset']}")
        if patrones:
            for patron in patrones:
                print(f"{self.colores['morado']}│ {self.colores['naranja']}{patron}{self.colores['reset']}")
        else:
            print(f"{self.colores['morado']}│ {self.colores['verde']}✅ No se detectaron patrones débiles evidentes{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['blanco']}🕵 FRECUENCIA EN LEAKS:{self.colores['reset']}")
        if leaks is None:
            print(f"{self.colores['morado']}│ {self.colores['gris']}(No se encontró leaks_hashes.txt en ~/pypher, verificación omitida){self.colores['reset']}")
        elif leaks > 0:
            print(f"{self.colores['morado']}│ {self.colores['rojo']}⚠️ Encontrada en {leaks} leak(s){self.colores['reset']}")
        else:
            print(f"{self.colores['morado']}│ {self.colores['verde']}✅ No encontrada en leaks{self.colores['reset']}")

        return {"entropia": entropia, "tiempos": tiempos, "patrones": patrones, "leaks": leaks}

    def analizar_wordlist_archivo(self, ruta_archivo):
        """Analiza un archivo de wordlist (.txt o .gz) y muestra un resumen
        estadístico: entropía media, puntaje medio y las contraseñas más
        débiles / más fuertes de la lista."""
        if not os.path.exists(ruta_archivo):
            print(f"{self.colores['rojo']}│ ✗ El archivo no existe: {ruta_archivo}{self.colores['reset']}")
            return

        try:
            if ruta_archivo.endswith(".gz"):
                archivo = gzip.open(ruta_archivo, "rt", encoding="utf-8", errors="ignore")
            else:
                archivo = open(ruta_archivo, "r", encoding="utf-8", errors="ignore")
            with archivo:
                contrasenas = [linea.strip() for linea in archivo if linea.strip()]
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al leer el archivo: {str(e)}{self.colores['reset']}")
            return

        if not contrasenas:
            print(f"{self.colores['naranja']}│ ⚠ El archivo está vacío{self.colores['reset']}")
            return

        resultados = []
        for contrasena in contrasenas:
            puntaje, max_puntaje, _, _, _, _, _, _ = calcular_puntaje_password(contrasena)
            entropia = self.calcular_entropia(contrasena)
            resultados.append((contrasena, puntaje, max_puntaje, entropia))

        resultados.sort(key=lambda r: r[3])  # ordenar por entropía ascendente

        entropia_media = sum(r[3] for r in resultados) / len(resultados)
        puntaje_medio = sum(r[1] for r in resultados) / len(resultados)

        print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}RESUMEN DE WORDLIST {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}Contraseñas analizadas: {self.colores['blanco']}{len(resultados)}{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}Entropía media: {self.colores['blanco']}{entropia_media:.1f} bits{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['azul']}Puntaje medio: {self.colores['blanco']}{puntaje_medio:.1f}/8{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['rojo']}Las más débiles:{self.colores['reset']}")
        for contrasena, puntaje, max_puntaje, entropia in resultados[:5]:
            print(f"{self.colores['morado']}│   {self.colores['blanco']}{contrasena:<20}{self.colores['gris']} puntaje {puntaje}/{max_puntaje} · {entropia:.1f} bits{self.colores['reset']}")

        print(f"\n{self.colores['morado']}│ {self.colores['verde']}Las más fuertes:{self.colores['reset']}")
        for contrasena, puntaje, max_puntaje, entropia in resultados[-5:]:
            print(f"{self.colores['morado']}│   {self.colores['blanco']}{contrasena:<20}{self.colores['gris']} puntaje {puntaje}/{max_puntaje} · {entropia:.1f} bits{self.colores['reset']}")

    # -----------------------------------------------------------------
    # === Persistencia en archivo del análisis avanzado ===
    # -----------------------------------------------------------------
    def guardar_analisis_avanzado(self, contrasena, stats, nombre_archivo, subcarpeta=None):
        """Guarda el reporte de estadísticas avanzadas (entropía, tiempos
        estimados de crackeo, patrones detectados y resultado de leaks)
        en un archivo de texto dentro de ~/pypher (o subcarpeta indicada)."""
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        tiempos_txt = "\n".join(
            f"  {algoritmo}: GPU {valores['GPU']} · CPU {valores['CPU']}"
            for algoritmo, valores in stats["tiempos"].items()
        )

        if stats["patrones"]:
            patrones_txt = "\n".join(f"  {p}" for p in stats["patrones"])
        else:
            patrones_txt = "  ✅ No se detectaron patrones débiles evidentes"

        if stats["leaks"] is None:
            leaks_txt = "  (No se encontró leaks_hashes.txt, verificación omitida)"
        elif stats["leaks"] > 0:
            leaks_txt = f"  ⚠️ Encontrada en {stats['leaks']} leak(s)"
        else:
            leaks_txt = "  ✅ No encontrada en leaks"

        contenido = f"""========================================
    Pypher - Estadísticas Avanzadas
========================================

📅 Fecha: {fecha}
🔐 Contraseña analizada: {contrasena}

🧮 Entropía estimada: {stats['entropia']:.1f} bits

⏱ Tiempo estimado de crackeo (promedio):
{tiempos_txt}

🧩 Patrones detectados:
{patrones_txt}

🕵 Frecuencia en leaks:
{leaks_txt}

========================================
    Generado con Pypher
    https://github.com/tu-usuario/pypher
========================================
"""

        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'

        if subcarpeta:
            ruta_carpeta = os.path.join(self.documentos_path, subcarpeta)
            if not os.path.exists(ruta_carpeta):
                os.makedirs(ruta_carpeta)
        else:
            ruta_carpeta = self.documentos_path

        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)

        try:
            with open(ruta_completa, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print(f"{self.colores['verde']}│ ✓ Análisis guardado en: {self.colores['blanco']}{ruta_completa}{self.colores['reset']}")
            return True
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al guardar: {str(e)}{self.colores['reset']}")
            return False

    # -----------------------------------------------------------------
    # === Flujo interactivo (menú) ===
    # -----------------------------------------------------------------
    def analizar_avanzado_interactivo(self) -> None:
        """Flujo interactivo del menú 'Estadísticas avanzadas': permite
        analizar una sola contraseña (oculta al escribirla) o un archivo
        de wordlist completo, y ofrece guardar el resultado."""
        print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}ESTADÍSTICAS AVANZADAS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[1]{self.colores['blanco']}  Analizar una contraseña")
        print(f"{self.colores['morado']}│ {self.colores['cyan']}[2]{self.colores['blanco']}  Analizar un archivo de wordlist")

        modo = input(f"{self.colores['morado']}│ {self.colores['verde']}➤ {self.colores['reset']}").strip()

        if modo == "1":
            contrasena = getpass.getpass(f"{self.colores['morado']}│ {self.colores['azul']}Contraseña a analizar (oculta): {self.colores['reset']}")
            if not contrasena:
                print(f"{self.colores['rojo']}│ ✗ Ingresa una contraseña para analizar{self.colores['reset']}")
                return

            # Mostrar estadísticas
            stats = self.mostrar_estadisticas_avanzadas(contrasena)

            # ======== OPCIÓN DE GUARDAR ========
            guardar = input(f"\n{self.colores['morado']}│ {self.colores['azul']}¿Guardar este análisis en un archivo? (s/n): {self.colores['reset']}").strip().lower()
            if guardar == 's':
                nombre = input(f"{self.colores['morado']}│ {self.colores['azul']}Nombre del archivo: {self.colores['reset']}").strip()
                if nombre:
                    subcarpeta = input(f"{self.colores['morado']}│ {self.colores['azul']}Subcarpeta (opcional, Enter para omitir): {self.colores['reset']}").strip()
                    self.guardar_analisis_avanzado(contrasena, stats, nombre, subcarpeta=subcarpeta if subcarpeta else None)
                else:
                    print(f"{self.colores['rojo']}│ ✗ El nombre no puede estar vacío{self.colores['reset']}")

        elif modo == "2":
            ruta = input(f"{self.colores['morado']}│ {self.colores['azul']}Ruta del archivo (relativa a ~/pypher o absoluta): {self.colores['reset']}").strip()
            if not ruta:
                print(f"{self.colores['rojo']}│ ✗ Debes indicar una ruta{self.colores['reset']}")
                return
            if not os.path.isabs(ruta):
                ruta = os.path.join(self.documentos_path, ruta)
            self.analizar_wordlist_archivo(ruta)

        else:
            print(f"{self.colores['rojo']}│ ✗ Opción no válida{self.colores['reset']}")


def mostrar_info_proyecto(colores: dict) -> None:
    """Muestra la sección 'Acerca de Pypher': qué es el proyecto, su
    licencia, el repositorio y cómo contribuir o reportar bugs.

    Args:
        colores: Diccionario de códigos ANSI de color usado por el resto
            del programa (``GeneradorContrasenasCLI.colores``).
    """
    c = colores
    print(f"\n{c['morado']}╔{'═' * 60}╗{c['reset']}")
    print(f"{c['morado']}│{c['reset']} {c['negrita']}{c['blanco']}📖 ACERCA DE PYPHER{c['reset']}")
    print(f"{c['morado']}╚{'═' * 60}╝{c['reset']}")
    print(f"\n{c['morado']}│ {c['verde']}Proyecto: {c['blanco']}Pypher — Generador y Analizador de Contraseñas{c['reset']}")
    print(f"{c['morado']}│ {c['azul']}Versión: {c['blanco']}{__version__}{c['reset']}")
    print(f"{c['morado']}│ {c['cyan']}Repositorio: {c['blanco']}https://github.com/leoXxit0/pypher-password{c['reset']}")
    print(f"{c['morado']}│ {c['amarillo']}Licencia: {c['blanco']}GNU GPLv3{c['reset']}")
    print(f"{c['morado']}│{c['reset']}")
    print(f"{c['morado']}│ {c['gris']}Pypher es software libre: puedes usarlo, estudiarlo, modificarlo{c['reset']}")
    print(f"{c['morado']}│ {c['gris']}y redistribuirlo bajo los términos de la GPLv3.{c['reset']}")
    print(f"{c['morado']}│{c['reset']}")
    print(f"{c['morado']}│ {c['verde']}🐛 Reportar bugs: {c['blanco']}https://github.com/tu-usuario/pypher/issues{c['reset']}")
    print(f"{c['morado']}│ {c['verde']}🤝 Contribuir: {c['blanco']}abre un Pull Request en el repositorio{c['reset']}")
    print(f"{c['morado']}│{c['reset']}")
    print(f"{c['morado']}│ {c['gris']}Si te resultó útil, considera dejar una ⭐ en el repositorio.{c['reset']}")


def crear_parser_argumentos() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de línea de comandos de Pypher.

    Returns:
        argparse.ArgumentParser: Parser configurado con todas las
        opciones del modo no interactivo (``-g``, ``-a``, ``-w``, ``-s``,
        ``-v``). ``-h/--help`` la añade automáticamente ``argparse``.
    """
    parser = argparse.ArgumentParser(
        prog="pypher",
        description="Pypher — Generador y Analizador de Contraseñas (GPLv3).",
        epilog="Sin argumentos, Pypher se abre en modo interactivo (menú).",
    )
    parser.add_argument(
        "-g", "--generate",
        metavar="LONGITUD",
        type=int,
        help="Generar una contraseña de la longitud especificada (8-20) y salir.",
    )
    parser.add_argument(
        "-a", "--analyze",
        metavar="CONTRASEÑA",
        type=str,
        help="Analizar la fortaleza de una contraseña específica y salir.",
    )
    parser.add_argument(
        "-w", "--wordlist",
        action="store_true",
        help="Abrir directamente el generador de wordlists interactivo.",
    )
    parser.add_argument(
        "-s", "--stats",
        metavar="CONTRASEÑA",
        type=str,
        help="Mostrar estadísticas avanzadas (entropía, tiempo de crackeo, patrones) de una contraseña y salir.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Pypher {__version__}",
    )
    return parser


def ejecutar_modo_no_interactivo(args: argparse.Namespace) -> int:
    """Ejecuta la acción solicitada por línea de comandos y termina.

    Se usa cuando el usuario invoca Pypher con al menos un argumento
    (``-g``, ``-a``, ``-w`` o ``-s``), por ejemplo desde otro script.

    Args:
        args: Namespace devuelto por ``argparse`` con las opciones
            elegidas por el usuario.

    Returns:
        int: Código de salida del proceso (0 = éxito, 1 = error de uso).
    """
    generador = GeneradorContrasenasCLI()

    if args.generate is not None:
        longitud = args.generate
        if not (8 <= longitud <= 20):
            print(f"{generador.colores['rojo']}✗ La longitud debe estar entre 8 y 20{generador.colores['reset']}")
            return 1
        contrasena = generador.generar_contrasena(longitud)
        print(f"{generador.colores['verde']}🔑 {generador.colores['negrita']}{contrasena}{generador.colores['reset']}")
        generador.mostrar_estadisticas(contrasena)
        return 0

    if args.analyze is not None:
        generador.mostrar_analisis_detallado(args.analyze)
        return 0

    if args.stats is not None:
        stats_avanzadas = AdvancedAnalyzer(generador.colores, generador.documentos_path)
        stats_avanzadas.mostrar_estadisticas_avanzadas(args.stats)
        return 0

    if args.wordlist:
        wordlist_gen = WordlistGenerator(generador.colores, generador.documentos_path)
        wordlist_gen.generar_wordlist_interactivo()
        return 0

    return 1


def menu_interactivo() -> None:
    """Muestra el banner y el menú principal, y gestiona el bucle
    interactivo de Pypher hasta que el usuario elige salir."""
    generador = GeneradorContrasenasCLI()
    wordlist_gen = WordlistGenerator(generador.colores, generador.documentos_path)
    stats_avanzadas = AdvancedAnalyzer(generador.colores, generador.documentos_path)

    # Banner
    print(f"""
{generador.colores['cyan']}╔═══════════════════════════════════════════════════════════════════════╗
║ {generador.colores['rosa']}██████╗ {generador.colores['morado']}██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ {generador.colores['cyan']}║
║ {generador.colores['rosa']}██╔══██╗{generador.colores['morado']}╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗{generador.colores['cyan']}║
║ {generador.colores['rosa']}██████╔╝{generador.colores['morado']} ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝{generador.colores['cyan']}║
║ {generador.colores['rosa']}██╔═══╝ {generador.colores['morado']}  ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗{generador.colores['cyan']}║
║ {generador.colores['rosa']}██║     {generador.colores['morado']}   ██║   ██║     ██║  ██║███████╗██║  ██║{generador.colores['cyan']}║
║ {generador.colores['rosa']}╚═╝     {generador.colores['morado']}   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{generador.colores['cyan']}║
║     {generador.colores['verde']}★ GENERADOR Y ANALIZADOR DE CONTRASEÑAS ★{generador.colores['cyan']}     ║
║  {generador.colores['amarillo']}⚡ ¡La seguridad en la era digital empieza aquí! ⚡{generador.colores['cyan']}  ║
║  {generador.colores['azul']}📁 Archivos guardados en: {generador.documentos_path}{generador.colores['cyan']:<22} ║
╚═══════════════════════════════════════════════════════════════════════╝
{generador.colores['reset']}""")

    while True:
        print(f"\n{generador.colores['morado']}│ {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█ {generador.colores['blanco']}MENÚ PRINCIPAL {generador.colores['verde']}█{generador.colores['rosa']}█{generador.colores['verde']}█{generador.colores['reset']}")
        print(f"{generador.colores['morado']}│{generador.colores['reset']}")
        print(f"{generador.colores['morado']}│ {generador.colores['verde']}[1]{generador.colores['blanco']}  ⚡ Generar nueva contraseña")
        print(f"{generador.colores['morado']}│ {generador.colores['cyan']}[2]{generador.colores['blanco']}  🔍 Analizar contraseña")
        print(f"{generador.colores['morado']}│ {generador.colores['naranja']}[3]{generador.colores['blanco']}  📊 Estadísticas avanzadas")
        print(f"{generador.colores['morado']}│ {generador.colores['amarillo']}[4]{generador.colores['blanco']}  💾 Guardar contraseña en archivo")
        print(f"{generador.colores['morado']}│ {generador.colores['azul']}[5]{generador.colores['blanco']}  📜 Ver historial")
        print(f"{generador.colores['morado']}│ {generador.colores['cyan']}[6]{generador.colores['blanco']}  📚 Generar wordlist")
        print(f"{generador.colores['morado']}│ {generador.colores['morado']}[7]{generador.colores['blanco']}  📖 Acerca de Pypher")
        print(f"{generador.colores['morado']}│ {generador.colores['rojo']}[8]{generador.colores['blanco']}  🚪 Salir")
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

                    if copiar_portapapeles(contrasena):
                        print(f"{generador.colores['verde']}│ ✓ Copiada al portapapeles{generador.colores['reset']}")
                    else:
                        print(
                            f"{generador.colores['gris']}│ ⚠ No se pudo copiar al portapapeles "
                            f"(instala 'pyperclip' o 'xclip'/'wl-clipboard'){generador.colores['reset']}"
                        )

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
            generador.analizar_contrasena_interactivo()

        elif opcion == "3":
            stats_avanzadas.analizar_avanzado_interactivo()

        elif opcion == "4":
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

        elif opcion == "5":
            subcarpeta = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Subcarpeta del historial (opcional, Enter para omitir): {generador.colores['reset']}").strip()
            generador.mostrar_historial(subcarpeta=subcarpeta if subcarpeta else None)

        elif opcion == "6":
            wordlist_gen.generar_wordlist_interactivo()

        elif opcion == "7":
            mostrar_info_proyecto(generador.colores)

        elif opcion == "8":
            print(f"\n{generador.colores['verde']}│ 👋 ¡Hasta luego! Mantén tus contraseñas seguras 🔒{generador.colores['reset']}")
            break

        else:
            print(f"{generador.colores['rojo']}│ ✗ Opción no válida{generador.colores['reset']}")


def main() -> int:
    """Punto de entrada del programa.

    Verifica primero si se pasaron argumentos de línea de comandos:

    * Si hay argumentos -> modo no interactivo (ejecuta la acción y sale).
    * Si no hay argumentos -> modo interactivo (menú clásico).

    También asegura que exista la configuración de usuario en
    ``~/.config/pypher/config.json`` desde la primera ejecución.

    Returns:
        int: Código de salida del proceso.
    """
    cargar_configuracion()  # crea ~/.config/pypher/config.json si no existe

    parser = crear_parser_argumentos()
    args = parser.parse_args()

    modo_no_interactivo = any([
        args.generate is not None,
        args.analyze is not None,
        args.stats is not None,
        args.wordlist,
    ])

    if modo_no_interactivo:
        return ejecutar_modo_no_interactivo(args)

    menu_interactivo()
    return 0


if __name__ == "__main__":
    sys.exit(main())
