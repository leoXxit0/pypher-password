# 🐍 Pypher - Generador y Analizador de Contraseñas Seguras (Wordlist Generator)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Completado-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

![Banner](Banner.png)
---

## 📌 Descripción

**Pypher** es una herramienta de escritorio con interfaz gráfica moderna y oscura, pensada para **generar** y **analizar** contraseñas seguras. Nació como un simple generador de contraseñas y evolucionó a una suite unificada que incluye:

- 🔐 **Generador de Contraseñas**: crea contraseñas robustas de 8 a 20 caracteres combinando mayúsculas, minúsculas, números y símbolos seguros.
- 🔍 **Analizador de Contraseñas**: evalúa cualquier contraseña que ingreses (propia o generada por otra herramienta) y te dice qué tan segura es realmente.
- 📚 **Generador de Wordlist** *(próximamente)*: espacio reservado para una futura herramienta de generación de listas de palabras, pensado como campo abierto para la comunidad.

El proyecto está desarrollado en **Python y Tkinter**, integrando buenas prácticas de seguridad informática y una experiencia de usuario fluida. Incluye copia automática al portapapeles, análisis de fortaleza en tiempo real y guardado de contraseñas en archivos `.txt` con formato estructurado.

> ⚠️ **Nota importante:** por ahora, esta actualización de Pypher solo está disponible en **modo interfaz gráfica (GUI)**. No existe todavía una versión de línea de comandos (CLI).

---
### 🔒 Filtro de Símbolos: Seguridad y Compatibilidad

Pypher elige cuidadosamente los caracteres especiales para que tu contraseña sea fuerte y funcione en cualquier sistema (bancos, redes sociales, servidores, etc.).

**Caracteres seguros (los que usamos):**

```
! @ # $ % & ( ) - _ = + [ ] { } ?
```

**¿Por qué?** Son compatibles con el 99% de los sistemas, desde bases de datos hasta comandos en terminal.

---
## 🚀 Instalación y Ejecución (Versión CLI)

Sigue estos pasos para ejecutar Pypher en tu teminal:

![pypher en linux](terminal.png)

### 1. Clonar el repositorio

```bash
git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password
```
### 2. Instalar pyperclip (portapapeles OPCIONAL)
```bash
pip3 install pyperclip
```
### 3. Ejecutar
```bash
python3 pypher_linux.py
```
### Tutorial 
![pypher en linux](tutorial.gif)

---

## 🚀 Instalación y Ejecución (Versión GUI - NO ACTUALIZADO)

### 1. Instalar Tkinter (interfaz gráfica)

```bash
sudo apt install python3-tk -y
```
### 2. Instalar pyperclip (portapapeles OPCIONAL)
```bash
pip3 install pyperclip
```
### 3. Clonar el repositorio

```bash
git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password
```
### 4. Ejecutar
```bash
python3 pypher.py
```
![Generando Contraseña](generando.png)

Esto abrirá el **Menú Principal**, desde donde puedes acceder al Generador, al Analizador, o ver el placeholder del futuro Generador de Wordlist.

> 💡 Pypher no requiere librerías externas: solo usa la librería estándar de Python (`tkinter`, `random`, `string`, `re`, `datetime`, `os`, `webbrowser`).

---

## ⭐ Apoya el Proyecto

Si este proyecto te ha sido útil, considera:

- Darle una ⭐ en GitHub
- Compartirlo con otros desarrolladores
- Reportar issues o sugerir mejoras
