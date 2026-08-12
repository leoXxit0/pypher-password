import random
import string
import re
import getpass
from datetime import datetime
import os
import subprocess

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
            except Exception:
                # Si falla, usar el directorio actual
                return "."
        return ruta_es

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
    # === Persistencia en archivo (Documentos del usuario) ===
    # =================================================================
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
        archivo de texto en la carpeta Documentos (o subcarpeta indicada)."""
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
        print(f"{generador.colores['morado']}│ {generador.colores['amarillo']}[3]{generador.colores['blanco']}  💾 Guardar contraseña en archivo")
        print(f"{generador.colores['morado']}│ {generador.colores['azul']}[4]{generador.colores['blanco']}  📜 Ver historial")
        print(f"{generador.colores['morado']}│ {generador.colores['rojo']}[5]{generador.colores['blanco']}  🚪 Salir")
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

        elif opcion == "4":
            subcarpeta = input(f"{generador.colores['morado']}│ {generador.colores['azul']}Subcarpeta del historial (opcional, Enter para omitir): {generador.colores['reset']}").strip()
            generador.mostrar_historial(subcarpeta=subcarpeta if subcarpeta else None)

        elif opcion == "5":
            print(f"\n{generador.colores['verde']}│ 👋 ¡Hasta luego! Mantén tus contraseñas seguras 🔒{generador.colores['reset']}")
            break

        else:
            print(f"{generador.colores['rojo']}│ ✗ Opción no válida{generador.colores['reset']}")


if __name__ == "__main__":
    main()
