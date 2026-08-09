# 🐍 Pypher - Generador de Contraseñas Seguras

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Completado-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

![Banner](Banner.png)
---

## 📌 Descripción

**Pypher** es un generador de contraseñas seguras con interfaz gráfica moderna y oscura. Diseñado para crear contraseñas robustas de **8 a 20 caracteres** utilizando **caracteres especiales seguros**, compatibles con la mayoría de sistemas (bancos, correos electrónicos, redes sociales, servidores, etc.).

El proyecto fue desarrollado con **Python y Tkinter**, integrando buenas prácticas de seguridad informática y una experiencia de usuario fluida. Incluye **copia automática al portapapeles**, análisis de fortaleza en tiempo real y guardado de contraseñas en archivos `.txt` con formato estructurado.

---
### 🖥️ Dos formas de usar Pypher

| Versión | Descripción |
|---------|-------------|
| `pypher.py` | Interfaz gráfica (GUI) con Tkinter. Ideal para uso diario. |
| `pypher_linux.py` | **Modo terminal (sin GUI)**. Perfecto para servidores, SSH o sistemas sin entorno gráfico. |

---
## 🚀 Instalación y Ejecución (Versión sin Interfaz)

Sigue estos pasos para ejecutar Pypher en tu teminal:

### 1. Clonar el repositorio

```bash
git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password
```
### 2. Ejecutar
```bash
python3 pypher_linux.py
```
### Tutorial 
![pypher en linux](tutorial.gif)

---
### Filtro de Símbolos: Seguridad y Compatibilidad
Pypher elige cuidadosamente los caracteres especiales para que tu contraseña sea fuerte y funcione en cualquier sistema (bancos, redes sociales, servidores, etc.).

### Caracteres Seguros (Los que usamos)
Usamos un conjunto de símbolos universalmente aceptados:
! @ # $ % & ( ) - _ = + [ ] { } ?

### ¿Por qué? 
Son compatibles con el 99% de los sistemas, desde bases de datos hasta comandos en terminal.

---

## 🚀 Instalación y Ejecución (Versión con Interfaz)

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
python3 pypher_linux.py
```
![Generando Contraseña](generando.png)

---

## ⭐ Apoya el Proyecto

Si este proyecto te ha sido útil, considera:

- Darle una ⭐ en GitHub
- Compartirlo con otros desarrolladores
- Reportar issues o sugerir mejoras
