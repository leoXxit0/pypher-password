#!/usr/bin/env bash
#
# install.sh - Instalador interactivo de Pypher
#
# Detecta el shell del usuario y ofrece crear un alias, un comando
# global del sistema, o simplemente mostrar las instrucciones.
#
# Licencia: GNU GPLv3 (ver LICENSE)

set -euo pipefail

# --- Colores -----------------------------------------------------------
VERDE='\033[0;32m'
CYAN='\033[0;36m'
AMARILLO='\033[1;33m'
ROJO='\033[0;31m'
RESET='\033[0m'

# --- Comprobar que pypher_linux.py existe en el directorio actual ------
if [ ! -f "$(pwd)/pypher_linux.py" ]; then
    echo -e "${ROJO}✗ No se encontró 'pypher_linux.py' en el directorio actual.${RESET}"
    echo -e "${AMARILLO}  Ejecuta este script desde la raíz del proyecto Pypher.${RESET}"
    exit 1
fi

RUTA_SCRIPT="$(pwd)/pypher_linux.py"
chmod +x "$RUTA_SCRIPT" 2>/dev/null || true

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║           🐍  Instalador de Pypher  🐍                     ║${RESET}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${VERDE}✓ Script encontrado en:${RESET} $RUTA_SCRIPT"
echo ""

# --- Detectar shell ------------------------------------------------------
SHELL_NOMBRE="$(basename "${SHELL:-}")"
echo -e "${VERDE}✓ Shell detectado:${RESET} ${SHELL_NOMBRE:-desconocido}"
echo ""

# --- Menú ------------------------------------------------------------
echo "¿Qué método de acceso rápido quieres configurar?"
echo ""
echo -e "  ${VERDE}[1]${RESET} Crear alias para mi shell actual (recomendado)"
echo -e "  ${CYAN}[2]${RESET} Crear comando global del sistema (sudo ln -s -> /usr/local/bin/pypher)"
echo -e "  ${AMARILLO}[3]${RESET} Solo mostrar las instrucciones (no cambiar nada)"
echo ""
read -rp "➤ Elige una opción [1-3]: " OPCION

crear_alias() {
    local archivo_rc="$1"
    local linea_alias="$2"

    if [ -f "$archivo_rc" ] && grep -qF "alias pypher=" "$archivo_rc" 2>/dev/null; then
        echo -e "${AMARILLO}⚠ Ya existe un alias 'pypher' en $archivo_rc. No se modificó.${RESET}"
        return
    fi

    echo "$linea_alias" >> "$archivo_rc"
    echo -e "${VERDE}✓ Alias añadido a $archivo_rc${RESET}"
    echo -e "${CYAN}  Ejecuta 'source $archivo_rc' o abre una nueva terminal para usarlo.${RESET}"
}

case "$OPCION" in
    1)
        case "$SHELL_NOMBRE" in
            bash)
                crear_alias "$HOME/.bashrc" "alias pypher=\"python3 $RUTA_SCRIPT\""
                ;;
            zsh)
                crear_alias "$HOME/.zshrc" "alias pypher=\"python3 $RUTA_SCRIPT\""
                ;;
            fish)
                mkdir -p "$HOME/.config/fish"
                crear_alias "$HOME/.config/fish/config.fish" "alias pypher \"python3 $RUTA_SCRIPT\""
                ;;
            *)
                echo -e "${AMARILLO}⚠ No se pudo detectar automáticamente tu shell (${SHELL_NOMBRE:-desconocido}).${RESET}"
                echo -e "${CYAN}  Añade manualmente esta línea a la configuración de tu shell:${RESET}"
                echo -e "  alias pypher=\"python3 $RUTA_SCRIPT\""
                ;;
        esac
        ;;
    2)
        echo -e "${CYAN}Se creará un enlace simbólico en /usr/local/bin/pypher (requiere sudo):${RESET}"
        if sudo ln -sf "$RUTA_SCRIPT" /usr/local/bin/pypher; then
            echo -e "${VERDE}✓ Comando global creado: pypher${RESET}"
        else
            echo -e "${ROJO}✗ No se pudo crear el enlace simbólico.${RESET}"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo -e "${CYAN}Bash/Zsh:${RESET}"
        echo "  echo 'alias pypher=\"python3 $RUTA_SCRIPT\"' >> ~/.bashrc && source ~/.bashrc"
        echo ""
        echo -e "${CYAN}Fish:${RESET}"
        echo "  echo 'alias pypher \"python3 $RUTA_SCRIPT\"' >> ~/.config/fish/config.fish"
        echo ""
        echo -e "${CYAN}Comando global (cualquier shell):${RESET}"
        echo "  sudo ln -s $RUTA_SCRIPT /usr/local/bin/pypher"
        ;;
    *)
        echo -e "${ROJO}✗ Opción no válida.${RESET}"
        exit 1
        ;;
esac

echo ""
echo -e "${VERDE}🎉 Listo. Escribe 'pypher' para ejecutar el programa.${RESET}"
