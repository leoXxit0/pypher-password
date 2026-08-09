# 🐍 Pypher - Generador de Contraseñas Seguras

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Completado-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

---

## 📌 Descripción

**Pypher** es un generador de contraseñas seguras con interfaz gráfica moderna y oscura. Diseñado para crear contraseñas robustas de **8 a 20 caracteres** utilizando **caracteres especiales seguros**, compatibles con la mayoría de sistemas (bancos, correos electrónicos, redes sociales, servidores, etc.).

El proyecto fue desarrollado con **Python y Tkinter**, integrando buenas prácticas de seguridad informática y una experiencia de usuario fluida. Incluye **copia automática al portapapeles**, análisis de fortaleza en tiempo real y guardado de contraseñas en archivos `.txt` con formato estructurado.

---

## 🎯 Características Principales

| Característica | Descripción |
|:---|:---|
| ✅ **Longitud ajustable** | De 8 a 20 caracteres (spinbox interactivo) |
| ✅ **Caracteres seguros** | Solo símbolos compatibles con todos los sistemas |
| ✅ **Copia automática** | La contraseña se copia al portapapeles al generarla |
| ✅ **Copia manual** | Botón "Copiar" para re-copiar si es necesario |
| ✅ **Análisis de fortaleza** | Barra visual y etiqueta (DÉBIL / MEDIA / FUERTE) |
| ✅ **Estadísticas detalladas** | Muestra Mayúsculas, Minúsculas, Números, Símbolos y Longitud |
| ✅ **Interfaz oscura 2026** | Diseño moderno con tarjetas y colores neón |
| ✅ **Guardado en .txt** | Con selector de ubicación y formato estructurado |
| ✅ **Fecha automática** | Se registra la fecha y hora de creación |
| ✅ **Validaciones** | No permite guardar sin contraseña o sin nombre |

---
## 🚀 Instalación y Ejecución

Sigue estos pasos para ejecutar Pypher en tu computadora:

### 1. Clonar el repositorio

git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password

---

## 🔒 Filtro de Símbolos: ¿Por qué estos caracteres y no otros?

Pypher utiliza un **subconjunto cuidadosamente seleccionado** de caracteres especiales para garantizar la máxima compatibilidad con todo tipo de sistemas.

### ✅ Caracteres que SÍ usamos

| Carácter | ¿Por qué es seguro? |
|:---|:---|
| `! @ # $ % & ( ) - _ = + [ ] { } ?` | Son **compatibles con el 99% de los sistemas**: bancos, correos, redes sociales, servidores Linux/Windows, bases de datos, APIs, etc. |

### ❌ Caracteres que NO usamos

| Carácter | ¿Por qué NO se usan? |
|:---|:---|
| `'` (comilla simple) | Puede romper consultas SQL o comandos en shell |
| `"` (comilla doble) | Problemática en JSON, CSV y comandos |
| `\` (barra invertida) | Carácter de escape en muchos lenguajes |
| `/` (barra inclinada) | Conflictos con rutas de archivos |
| `< >` (mayor/menor) | Interpretados como HTML/XML |
| `|` (pipe) | Ejecuta comandos en terminal |
| `*` (asterisco) | Comodín en sistemas de archivos |
| `` ` `` (acento grave) | Ejecuta comandos en Bash |
| `~` (tilde) | Directorio home en Linux/Unix |

### 📊 Resumen visual

| Tipo de sistema | Problema con caracteres problemáticos |
|:---|:---|
| **Bases de datos** | `'` y `"` rompen consultas SQL |
| **Sistemas Linux** | `|`, `<`, `>`, `` ` `` ejecutan comandos no deseados |
| **Archivos/URLs** | `/`, `\`, `~` confunden las rutas |
| **HTML/Web** | `<`, `>` interpretados como etiquetas |
| **JSON/CSV** | `"` y `,` rompen la estructura |

> **Conclusión**: Pypher usa un **subconjunto seguro** de caracteres especiales para garantizar que tu contraseña funcione en **cualquier sistema**, sin importar la plataforma o tecnología.

---

## 🎨 Capturas de Pantalla

### Interfaz Principal
![Interfaz Principal](interfaz_principal.png)

### Generando una Contraseña
![Generando Contraseña](generando.png)

### Guardando Archivo
![Guardando Archivo](guardando.png)

### Ejemplo de Archivo Generado
![Archivo Generado](archivo_generado.png)

---

## ⭐ Apoya el Proyecto

Si este proyecto te ha sido útil, considera:

- Darle una ⭐ en GitHub
- Compartirlo con otros desarrolladores
- Reportar issues o sugerir mejoras
