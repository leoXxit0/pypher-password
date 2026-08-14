# 🐍 Pypher — Generador y Analizador de Contraseñas

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/License-GPLv3-green" alt="License: GPL v3">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey" alt="Platform">
</p>

Herramienta de línea de comandos, con estética *Cyberpunk*, para generar
contraseñas seguras, analizar su fortaleza (con estadísticas avanzadas:
entropía, tiempo estimado de crackeo, patrones inseguros) y generar
wordlists con fines educativos y de auditoría de seguridad.

Licencia: **GNU GPLv3**. Ver [LICENSE](LICENSE.md).

## ✨ Características

- Generación de contraseñas aleatorias seguras.
- Análisis de fortaleza con un sistema unificado de puntuación.
- Estadísticas avanzadas: entropía, tiempo estimado de crackeo, detección
  de patrones comunes.
- Generador de wordlists (inteligente, diccionario personalizado,
  mutaciones, combinaciones, fuerza bruta con patrones realistas).
- Modo interactivo (menú) **y** modo no interactivo (línea de comandos),
  útil para integrarse en scripts.
- Configuración persistente en `~/.config/pypher-password/config.json`.
- Solo depende de la biblioteca estándar de Python (`pyperclip` es
  opcional, para copiar al portapapeles).

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/leoXxit0/pypher-password.git
cd pypher-password
```

### 2. Crear un acceso directo (`pypher`)

Tienes tres formas de hacerlo, elige la que prefieras:

#### Opción A — Instalador interactivo (recomendado)

```bash
chmod +x install.sh
./install.sh
```

El script detecta tu shell automáticamente y te deja elegir entre crear
un alias, un comando global del sistema, o solo mostrar las
instrucciones.

#### Opción B — Comando global del sistema (recomendado como alternativa)

Funciona igual sin importar el shell que uses:

```bash
sudo ln -s "$(pwd)/pypher_linux.py" /usr/local/bin/pypher-password
chmod +x pypher_linux.py
```

A partir de ahí, `pypher` queda disponible como comando en todo el sistema.

> 💡 La ruta se calcula con `$(pwd)`, así que funciona sin importar en
> qué carpeta hayas descargado el proyecto.

## 🚀 Uso

### Modo interactivo

```bash
pypher
```

Abre el menú principal clásico.

### Modo no interactivo

```bash
pypher -g 16          # Generar una contraseña de 16 caracteres
pypher -a "MiClave123" # Analizar una contraseña
pypher -s "MiClave123" # Estadísticas avanzadas de una contraseña
pypher -w              # Abrir el generador de wordlists directamente
pypher -v              # Ver la versión instalada
pypher -h              # Ver la ayuda completa
```

## ⚙️ Configuración

Pypher guarda tus preferencias en:

```
~/.config/pypher-password/config.json
```

Este archivo se crea automáticamente en la primera ejecución.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Abre un *issue* para reportar bugs o
proponer mejoras, o envía un *Pull Request* directamente.

## 🐛 Reportar bugs

Usa la sección de [Issues](https://github.com/leoXxit0/pypher-password/issues)
del repositorio.

## 📄 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0**.

>Cualquiera puede usar, modificar y compartir Pypher. Pero si alguien lo mejora y lo distribuye, debe compartir sus mejoras bajo la misma licencia. Nadie puede convertirlo en un producto privado y cerrado.

Consulta el archivo [LICENSE](LICENSE.md) para más detalles.

