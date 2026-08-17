# 🐍 Pypher - Generador y Analizador de Contraseñas Seguras

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#)
[![Status](https://img.shields.io/badge/Status-Activo-brightgreen)](#)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange)](#)

---

## 📌 Descripción

**Pypher** es una herramienta de escritorio con interfaz gráfica moderna y oscura, pensada para **generar** y **analizar** contraseñas seguras. Nació como un simple generador de contraseñas y evolucionó a una suite unificada que incluye:

- 🔐 **Generador de Contraseñas**: crea contraseñas robustas de 8 a 20 caracteres combinando mayúsculas, minúsculas, números y símbolos seguros.
- 🔍 **Analizador de Contraseñas**: evalúa cualquier contraseña que ingreses (propia o generada por otra herramienta) y te dice qué tan segura es realmente.
- 📚 **Generador de Wordlist** *(próximamente)*: espacio reservado para una futura herramienta de generación de listas de palabras, pensado como campo abierto para la comunidad.

El proyecto está desarrollado en **Python y Tkinter**, integrando buenas prácticas de seguridad informática y una experiencia de usuario fluida. Incluye copia automática al portapapeles, análisis de fortaleza en tiempo real y guardado de contraseñas en archivos `.txt` con formato estructurado.

> ⚠️ **Nota importante:** por ahora, esta actualización de Pypher solo está disponible en **modo interfaz gráfica (GUI)**. No existe todavía una versión de línea de comandos (CLI).

---

## 📊 ¿Cómo se mide la fortaleza de una contraseña?

Tanto el **Generador** como el **Analizador** usan exactamente el **mismo sistema de puntuación**, para que el nivel de seguridad que veas sea siempre consistente sin importar desde qué módulo lo consultes.

El sistema evalúa hasta un máximo de **8 puntos**, repartidos en las siguientes métricas:

| Criterio | Puntos | Descripción |
|---|---|---|
| Longitud ≥ 8 caracteres | +1 | Longitud mínima aceptable |
| Longitud ≥ 12 caracteres | +1 | Longitud recomendada |
| Longitud ≥ 16 caracteres | +1 | Longitud óptima |
| Mayúsculas (A-Z) | +1 | Presencia de al menos una letra mayúscula |
| Minúsculas (a-z) | +1 | Presencia de al menos una letra minúscula |
| Números (0-9) | +1 | Presencia de al menos un dígito |
| Símbolos (`!@#$%&()-_=+[]{}?`) | +1 | Presencia de al menos un carácter especial |
| Variedad (≥ 3 tipos de caracteres distintos) | +1 | Combinación real entre mayúsculas, minúsculas, números y símbolos |

Además, el Analizador te advierte si tu contraseña contiene **patrones comunes** (`123456`, `qwerty`, `password`, `admin`, etc.), aunque esto no resta puntos, solo se muestra como advertencia informativa.

Con base en el puntaje obtenido (`puntaje / 8`), la contraseña se clasifica en:

| Porcentaje | Nivel |
|---|---|
| ≥ 80% | 🔒 **FUERTE** |
| ≥ 60% y < 80% | ⚡ **MEDIA** |
| < 60% | ⚠️ **DÉBIL** |

Este criterio busca ser **estricto y realista**: por ejemplo, una contraseña de 8 caracteres que solo combine letras y números (sin símbolos ni mayúsculas) no debería —y no será— calificada como FUERTE.

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para ejecutar Pypher en tu computadora:

### 1. Clonar el repositorio

```bash
git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Ejecutar la aplicación

```bash
python pypher_full.py
```

Esto abrirá el **Menú Principal**, desde donde puedes acceder al Generador, al Analizador, o ver el placeholder del futuro Generador de Wordlist.

> 💡 Pypher no requiere librerías externas: solo usa la librería estándar de Python (`tkinter`, `random`, `string`, `re`, `datetime`, `os`, `webbrowser`).

---

### 🔒 Filtro de Símbolos: Seguridad y Compatibilidad

Pypher elige cuidadosamente los caracteres especiales para que tu contraseña sea fuerte y funcione en cualquier sistema (bancos, redes sociales, servidores, etc.).

**Caracteres seguros (los que usamos):**

```
! @ # $ % & ( ) - _ = + [ ] { } ?
```

**¿Por qué?** Son compatibles con el 99% de los sistemas, desde bases de datos hasta comandos en terminal.

---

## 🧩 Generador de Wordlist (Próximamente)

En el Menú Principal encontrarás un botón **"📚 Generador de Wordlist (Próximamente)"**. Es un espacio reservado intencionalmente para una futura funcionalidad de generación de listas de palabras (wordlists), útil para pruebas de seguridad, auditorías y análisis de contraseñas.

**Este módulo está abierto a colaboraciones.** Si te interesa aportar:

- Puedes proponer la lógica de generación (por reglas, por diccionario, combinatoria, etc.)
- Puedes sugerir opciones de personalización (longitud, patrones, mutaciones tipo leetspeak, fechas, etc.)
- Puedes abrir un *issue* o un *pull request* con tu propuesta

Cualquier contribución, por pequeña que sea, es bienvenida. 🙌

---

## 🎨 Capturas de Pantalla

### Interfaz Principal

![Interfaz Principal](https://github.com/leoXxit0/pypher-password/raw/main/interfaz_principal.png)

### Generando una Contraseña

![Generando Contraseña](https://github.com/leoXxit0/pypher-password/raw/main/generando.png)

### Guardando Archivo

![Guardando Archivo](https://github.com/leoXxit0/pypher-password/raw/main/guardando.png)

### Ejemplo de Archivo Generado

![Archivo Generado](https://github.com/leoXxit0/pypher-password/raw/main/archivo_generado.png)

---

## 🗺️ Roadmap

- [x] Generador de contraseñas con GUI
- [x] Analizador de contraseñas con sistema de puntuación unificado
- [ ] Generador de Wordlist *(abierto a colaboraciones)*
- [ ] Versión de línea de comandos (CLI)
- [ ] Empaquetado como ejecutable (.exe / binario)

---

## ⭐ Apoya el Proyecto

Si este proyecto te ha sido útil, considera:

- Darle una ⭐ en GitHub
- Compartirlo con otros desarrolladores
- Reportar issues o sugerir mejoras
- Contribuir con código, especialmente en el módulo de Wordlist

---

## 👤 Autor

Desarrollado por **[leoXxit0](https://github.com/leoXxit0)**
