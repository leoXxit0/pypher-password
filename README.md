# 🐍 Pypher — Generador y Analizador de Contraseñas

Herramienta de línea de comandos, con estética *Cyberpunk*, para generar
contraseñas seguras, analizar su fortaleza (con estadísticas avanzadas:
entropía, tiempo estimado de crackeo, patrones inseguros) y generar
wordlists con fines educativos y de auditoría de seguridad.

Licencia: **GNU GPLv3**. Ver [LICENSE](LICENSE.txt).

## ✨ Características

- Generación de contraseñas aleatorias seguras.
- Análisis de fortaleza con un sistema unificado de puntuación.
- Estadísticas avanzadas: entropía, tiempo estimado de crackeo, detección
  de patrones comunes.
- Generador de wordlists (inteligente, diccionario personalizado,
  mutaciones, combinaciones, fuerza bruta con patrones realistas).
- Modo interactivo (menú) **y** modo no interactivo (línea de comandos),
  útil para integrarse en scripts.
- Configuración persistente en `~/.config/pypher/config.json`.
- Solo depende de la biblioteca estándar de Python (`pyperclip` es
  opcional, para copiar al portapapeles).

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/pypher.git
cd pypher
```

### 2. Crear un acceso directo (`pypher`)

Tienes tres formas de hacerlo, elige la que prefieras:

#### Opción A — Instalador interactivo (recomendado)

```bash
./install.sh
```

El script detecta tu shell automáticamente y te deja elegir entre crear
un alias, un comando global del sistema, o solo mostrar las
instrucciones.

#### Opción B — Comando global del sistema (recomendado como alternativa)

Funciona igual sin importar el shell que uses:

```bash
sudo ln -s "$(pwd)/pypher_linux.py" /usr/local/bin/pypher
chmod +x pypher_linux.py
```

A partir de ahí, `pypher` queda disponible como comando en todo el sistema.

#### Opción C — Alias manual, según tu shell

**Bash**

```bash
echo "alias pypher=\"python3 $(pwd)/pypher_linux.py\"" >> ~/.bashrc
source ~/.bashrc
```

**Zsh**

```bash
echo "alias pypher=\"python3 $(pwd)/pypher_linux.py\"" >> ~/.zshrc
source ~/.zshrc
```

**Fish**

```fish
echo "alias pypher \"python3 $(pwd)/pypher_linux.py\"" >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

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
~/.config/pypher/config.json
```

Este archivo se crea automáticamente en la primera ejecución.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Abre un *issue* para reportar bugs o
proponer mejoras, o envía un *Pull Request* directamente.

## 🐛 Reportar bugs

Usa la sección de [Issues](https://github.com/tu-usuario/pypher/issues)
del repositorio.

## 📄 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0**.
Consulta el archivo [LICENSE](LICENSE.txt) para más detalles.
