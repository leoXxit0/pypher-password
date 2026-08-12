import random
import string
import re
import getpass
from datetime import datetime
import os
import subprocess
import math
import hashlib
import itertools
import gzip

# =====================================================================
# === RESTRICCIÓN CRÍTICA DEL MÓDULO 3 ===
# El generador de wordlists NUNCA debe superar este número total de
# variantes por ejecución, sin importar el modo usado, para evitar un
# consumo excesivo de RAM/disco.
# =====================================================================
MAX_VARIANTES = 50000 # 50 mil variantes

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
                contrasena = subprocess.run(
                    ['xclip', '-selection', 'clipboard', '-o'],
                    capture_output=True, text=True, check=True
                ).stdout
                print(f"{self.colores['verde']}│ ✓ Contenido pegado desde el portapapeles{self.colores['reset']}")
            except Exception:
                print(f"{self.colores['rojo']}│ ✗ No se pudo acceder al portapapeles (¿xclip instalado?){self.colores['reset']}")
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
    https://github.com/leoXxit0
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
    RESTRICCIÓN CRÍTICA: nunca genera más de MAX_VARIANTES (250) contraseñas
    en una sola ejecución, sin importar el modo usado, para evitar un
    consumo excesivo de RAM/disco. El corte se aplica con un contador
    dentro de cada generador (yield), así que nunca se materializa en
    memoria más de lo permitido.
    """

    SIMBOLOS_FINALES = ["!", "@", "#", "$", "*", "?", "01", "123"]
    ANIOS = [str(a) for a in range(1990, 2027)]
    SUSTITUCIONES = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "5"}

    def __init__(self, colores, documentos_path):
        self.colores = colores
        self.documentos_path = documentos_path

    # -----------------------------------------------------------------
    # === Barra de progreso en tiempo real ===
    # -----------------------------------------------------------------
    def _mostrar_progreso(self, actual, total_referencia):
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

    def _advertir_si_excede(self, total_posible):
        if total_posible > MAX_VARIANTES:
            print(
                f"{self.colores['naranja']}│ ⚠ Se solicitaron/son posibles {total_posible} variantes, "
                f"pero el límite de seguridad es de {MAX_VARIANTES}. Se truncará automáticamente."
                f"{self.colores['reset']}"
            )

    # -----------------------------------------------------------------
    # a) Fuerza bruta: caracteres personalizados + rango de longitudes
    # -----------------------------------------------------------------
    def generar_fuerza_bruta(self, caracteres, longitud_min, longitud_max):
        """Genera combinaciones por fuerza bruta a partir de un conjunto de
        caracteres y un rango de longitudes. Corta estrictamente en
        MAX_VARIANTES gracias al contador interno (yield)."""
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
    # b) Mutaciones a partir de una palabra base
    # -----------------------------------------------------------------
    def generar_mutaciones(self, palabra_base):
        """Genera variantes de una palabra base combinando: sustituciones
        tipo leetspeak (a→@, e→3, i→1, o→0, s→5), mayúsculas/minúsculas/
        capitalizado, años (1990-2026) y símbolos finales. Corta en
        MAX_VARIANTES."""
        palabra_sub = "".join(self.SUSTITUCIONES.get(c.lower(), c) for c in palabra_base)

        formas_base = list(dict.fromkeys([
            palabra_base.lower(),
            palabra_base.upper(),
            palabra_base.capitalize(),
            palabra_sub.lower(),
            palabra_sub.upper(),
            palabra_sub.capitalize(),
        ]))

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
    # c) Combinaciones de dos listas (ej. nombres + apellidos)
    # -----------------------------------------------------------------
    def generar_combinaciones(self, lista1, lista2, separador=""):
        """Une dos listas de palabras mediante producto cartesiano. Si el
        producto supera MAX_VARIANTES, trunca y avisa."""
        total_posible = len(lista1) * len(lista2)
        self._advertir_si_excede(total_posible)

        contador = 0
        for palabra1 in lista1:
            for palabra2 in lista2:
                if contador >= MAX_VARIANTES:
                    return
                contador += 1
                yield f"{palabra1}{separador}{palabra2}"

    # -----------------------------------------------------------------
    # === Persistencia en archivo (.txt o .gz) dentro de ~/pypher ===
    # -----------------------------------------------------------------
    def guardar_wordlist(self, generador, nombre_archivo, comprimir=False, subcarpeta=None):
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
                    archivo.write(palabra + "\n")
                    contador += 1
                    self._mostrar_progreso(contador, MAX_VARIANTES)

            if contador == 0:
                print(f"{self.colores['rojo']}│ ✗ No se generó ninguna contraseña{self.colores['reset']}")
                return None, 0
            if contador < MAX_VARIANTES:
                # Cierra la barra de progreso en el 100% relativo a lo realmente generado
                self._mostrar_progreso(contador, contador)

            print(f"{self.colores['verde']}│ ✓ Wordlist generada: {self.colores['blanco']}{contador} contraseñas{self.colores['reset']}")
            print(f"{self.colores['verde']}│ ✓ Guardada en: {self.colores['blanco']}{ruta_completa}{self.colores['reset']}")
            return ruta_completa, contador
        except Exception as e:
            print(f"{self.colores['rojo']}│ ✗ Error al guardar wordlist: {str(e)}{self.colores['reset']}")
            return None, 0

    # -----------------------------------------------------------------
    # === Flujo interactivo (menú) ===
    # -----------------------------------------------------------------
    def generar_wordlist_interactivo(self):
        print(f"\n{self.colores['morado']}│ {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█ {self.colores['blanco']}GENERADOR DE WORDLISTS {self.colores['verde']}█{self.colores['rosa']}█{self.colores['verde']}█{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['gris']}Límite de seguridad: {MAX_VARIANTES} variantes por ejecución{self.colores['reset']}")
        print(f"{self.colores['morado']}│{self.colores['reset']}")
        print(f"{self.colores['morado']}│ {self.colores['verde']}[1]{self.colores['blanco']}  Fuerza bruta (caracteres + rango de longitud)")
        print(f"{self.colores['morado']}│ {self.colores['cyan']}[2]{self.colores['blanco']}  Mutaciones (palabra base)")
        print(f"{self.colores['morado']}│ {self.colores['amarillo']}[3]{self.colores['blanco']}  Combinaciones (dos listas de palabras)")

        modo = input(f"{self.colores['morado']}│ {self.colores['verde']}➤ {self.colores['reset']}").strip()

        generador = None
        if modo == "1":
            caracteres = input(f"{self.colores['morado']}│ {self.colores['azul']}Caracteres a usar (ej. abc123): {self.colores['reset']}").strip()
            if not caracteres:
                print(f"{self.colores['rojo']}│ ✗ Debes indicar al menos un carácter{self.colores['reset']}")
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
            generador = self.generar_fuerza_bruta(caracteres, longitud_min, longitud_max)

        elif modo == "2":
            palabra_base = input(f"{self.colores['morado']}│ {self.colores['azul']}Palabra base: {self.colores['reset']}").strip()
            if not palabra_base:
                print(f"{self.colores['rojo']}│ ✗ Debes indicar una palabra base{self.colores['reset']}")
                return
            generador = self.generar_mutaciones(palabra_base)

        elif modo == "3":
            entrada1 = input(f"{self.colores['morado']}│ {self.colores['azul']}Primera lista, separada por comas (ej. Juan,Ana): {self.colores['reset']}").strip()
            entrada2 = input(f"{self.colores['morado']}│ {self.colores['azul']}Segunda lista, separada por comas (ej. Perez,Lopez): {self.colores['reset']}").strip()
            if not entrada1 or not entrada2:
                print(f"{self.colores['rojo']}│ ✗ Ambas listas son obligatorias{self.colores['reset']}")
                return
            separador = input(f"{self.colores['morado']}│ {self.colores['azul']}Separador (opcional, Enter para ninguno): {self.colores['reset']}")
            lista1 = [p.strip() for p in entrada1.split(",") if p.strip()]
            lista2 = [p.strip() for p in entrada2.split(",") if p.strip()]
            generador = self.generar_combinaciones(lista1, lista2, separador=separador)

        else:
            print(f"{self.colores['rojo']}│ ✗ Opción no válida{self.colores['reset']}")
            return

        nombre = input(f"{self.colores['morado']}│ {self.colores['azul']}Nombre del archivo: {self.colores['reset']}").strip()
        if not nombre:
            print(f"{self.colores['rojo']}│ ✗ El nombre no puede estar vacío{self.colores['reset']}")
            return

        comprimir = input(f"{self.colores['morado']}│ {self.colores['azul']}¿Comprimir en .gz? (s/n): {self.colores['reset']}").strip().lower() == 's'
        subcarpeta = input(f"{self.colores['morado']}│ {self.colores['azul']}Subcarpeta (opcional, Enter para omitir): {self.colores['reset']}").strip()

        self.guardar_wordlist(generador, nombre, comprimir=comprimir, subcarpeta=subcarpeta if subcarpeta else None)


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

    def __init__(self, colores, documentos_path):
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
    def _formatear_tiempo(self, segundos):
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

    def detectar_patrones(self, contrasena):
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
    def mostrar_estadisticas_avanzadas(self, contrasena):
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
    # === Flujo interactivo (menú) ===
    # -----------------------------------------------------------------
    def analizar_avanzado_interactivo(self):
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
            self.mostrar_estadisticas_avanzadas(contrasena)

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


def mostrar_info_autor(colores):
    """Muestra la sección 'Sobre el autor' con los datos de contacto/GitHub"""
    print(f"\n{colores['morado']}╔{'═' * 60}╗{colores['reset']}")
    print(f"{colores['morado']}│{colores['reset']} {colores['negrita']}{colores['blanco']}👤 SOBRE EL AUTOR{colores['reset']}")
    print(f"{colores['morado']}╚{'═' * 60}╝{colores['reset']}")
    print(f"\n{colores['morado']}│ {colores['azul']}Autor: {colores['blanco']}leoXxit0{colores['reset']}")
    print(f"{colores['morado']}│ {colores['cyan']}GitHub: {colores['blanco']}https://github.com/leoXxit0{colores['reset']}")
    print(f"{colores['morado']}│ {colores['verde']}Proyecto: {colores['blanco']}Pypher — Generador y Analizador de Contraseñas{colores['reset']}")
    print(f"{colores['morado']}│{colores['reset']}")
    print(f"{colores['morado']}│ {colores['gris']}Si te resultó útil, considera dejar una ⭐ en el repositorio.{colores['reset']}")


def main():
    """Función principal del programa"""
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
        print(f"{generador.colores['morado']}│ {generador.colores['morado']}[7]{generador.colores['blanco']}  👤 Sobre el autor")
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

                    try:
                        subprocess.run(['xclip', '-selection', 'clipboard'], input=contrasena.encode(), check=True)
                        print(f"{generador.colores['verde']}│ ✓ Copiada al portapapeles{generador.colores['reset']}")
                    except Exception:
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
            mostrar_info_autor(generador.colores)

        elif opcion == "8":
            print(f"\n{generador.colores['verde']}│ 👋 ¡Hasta luego! Mantén tus contraseñas seguras 🔒{generador.colores['reset']}")
            break

        else:
            print(f"{generador.colores['rojo']}│ ✗ Opción no válida{generador.colores['reset']}")


if __name__ == "__main__":
    main()
