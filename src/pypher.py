import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import string
from datetime import datetime
import os
import re
import webbrowser


# === Patrones comunes a evitar (usado solo como advertencia informativa) ===
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
    Sistema ÚNICO y riguroso de evaluación de contraseñas (máx. 8 puntos),
    usado tanto por el Generador como por el Analizador para que ambos
    módulos evalúen con el mismo estándar.

    Criterios (igual que pypher.py original + variedad):
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


class AnalizadorContrasenas:
    """Clase para analizar la fortaleza de contraseñas"""
    
    def __init__(self, root, volver_callback):
        self.root = root
        self.volver_callback = volver_callback
        self.colores = {
            "bg_principal": "#0a0a0f",
            "bg_frame": "#14141e",
            "bg_card": "#1c1c2e",
            "bg_entry": "#252540",
            "bg_hover": "#2a2a4a",
            "fg_texto": "#e8e8f0",
            "fg_secundario": "#8888aa",
            "fg_titulo": "#ffffff",
            "verde": "#00d4aa",
            "verde_oscuro": "#00b894",
            "rojo": "#ff6b6b",
            "rojo_oscuro": "#e74c4c",
            "azul": "#4facfe",
            "azul_oscuro": "#2d7dd2",
            "naranja": "#ff9f43",
            "morado": "#a66cff",
            "rosa": "#ff6b9d",
            "cyan": "#00d2ff",
            "gris_borde": "#2a2a3e",
            "amarillo": "#feca57"
        }
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("Pypher - Analizador de Contraseñas")
        self.root.geometry("550x700")
        self.root.resizable(False, False)
        
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.colores["bg_principal"])
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.container = tk.Frame(self.main_frame, bg="#14141e")
        self.container.pack(fill="both", expand=True)
        
        # Título
        titulo_frame = tk.Frame(self.container, bg="#14141e")
        titulo_frame.pack(pady=(10, 2), fill="x")
        
        titulo = tk.Label(
            titulo_frame,
            text="🔍 Analizador",
            bg="#14141e",
            fg=self.colores["fg_titulo"],
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack()
        
        subtitulo = tk.Label(
            titulo_frame,
            text="Verifica la seguridad de tus contraseñas",
            bg="#14141e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 10)
        )
        subtitulo.pack(pady=(0, 5))
        
        # Línea decorativa
        linea = tk.Frame(self.container, bg="#2a2a3e", height=1)
        linea.pack(fill="x", padx=20, pady=(0, 8))
        
        # Tarjeta de análisis
        card_analisis = tk.Frame(
            self.container,
            bg="#1c1c2e",
            relief="flat",
            bd=0
        )
        card_analisis.pack(pady=3, padx=15, fill="x")
        
        tk.Label(
            card_analisis,
            text="ANALIZAR CONTRASEÑA",
            bg="#1c1c2e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(8, 4), padx=15)
        
        # Campo de texto para la contraseña
        frame_pass = tk.Frame(card_analisis, bg="#1c1c2e")
        frame_pass.pack(pady=2, padx=15, fill="x")
        
        tk.Label(
            frame_pass,
            text="Contraseña a analizar",
            bg="#1c1c2e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        self.entry_contrasena = tk.Entry(
            frame_pass,
            font=("Consolas", 12),
            bg="#0d0d1a",
            fg="#ffffff",
            relief="flat",
            bd=0,
            insertbackground="white",
            highlightthickness=1,
            highlightcolor="#2a2a3e",
            highlightbackground="#2a2a3e",
            show="•"
        )
        self.entry_contrasena.pack(pady=(4, 6), fill="x", ipady=5)
        
        # Botones: Mostrar, Pegar, Analizar
        frame_botones_accion = tk.Frame(card_analisis, bg="#1c1c2e")
        frame_botones_accion.pack(pady=2, padx=15, fill="x")
        
        # Botón Mostrar/Ocultar
        self.mostrar_var = tk.BooleanVar(value=False)
        self.btn_mostrar = tk.Button(
            frame_botones_accion,
            text="👁️ Mostrar",
            command=self.toggle_mostrar,
            bg="#252540",
            fg="#ffffff",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.btn_mostrar.pack(side="left", padx=2)
        
        # Botón Pegar - NUEVO
        self.btn_pegar = tk.Button(
            frame_botones_accion,
            text="📋 Pegar",
            command=self.pegar_portapapeles,
            bg="#2a2a4a",
            fg="#ffffff",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.btn_pegar.pack(side="left", padx=2)
        self.btn_pegar.bind("<Enter>", lambda e: self.btn_pegar.config(bg="#3a3a5a"))
        self.btn_pegar.bind("<Leave>", lambda e: self.btn_pegar.config(bg="#2a2a4a"))
        
        # Botón Analizar
        self.btn_analizar = tk.Button(
            frame_botones_accion,
            text="🔍 Analizar",
            command=self.analizar,
            bg=self.colores["azul"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=4,
            cursor="hand2"
        )
        self.btn_analizar.pack(side="right")
        
        # Resultados del análisis
        frame_resultados = tk.Frame(self.container, bg="#14141e")
        frame_resultados.pack(pady=10, padx=15, fill="x")
        
        self.resultados_texto = tk.Text(
            frame_resultados,
            height=12,
            bg="#0d0d1a",
            fg="#e8e8f0",
            font=("Consolas", 10),
            relief="flat",
            bd=0,
            wrap="word",
            highlightthickness=1,
            highlightcolor="#2a2a3e",
            highlightbackground="#2a2a3e"
        )
        self.resultados_texto.pack(fill="both", expand=True, ipady=8)
        
        # Barra de fortaleza
        frame_fortaleza = tk.Frame(self.container, bg="#14141e")
        frame_fortaleza.pack(pady=5, padx=15, fill="x")
        
        self.barra_fortaleza = tk.Canvas(
            frame_fortaleza,
            height=10,
            bg="#1a1a2e",
            highlightthickness=0,
            relief="flat"
        )
        self.barra_fortaleza.pack(fill="x")
        
        self.fortaleza_texto = tk.Label(
            frame_fortaleza,
            text="",
            bg="#14141e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 12, "bold")
        )
        self.fortaleza_texto.pack(pady=(5, 0))
        
        # Botón Volver
        frame_volver = tk.Frame(self.container, bg="#14141e")
        frame_volver.pack(pady=(10, 6), padx=15, fill="x")
        
        self.btn_volver = tk.Button(
            frame_volver,
            text="← Volver al Menú",
            command=self.volver_callback,
            bg="#2a2a4a",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_volver.pack(fill="x")
        
        # Estado
        self.estado_label = tk.Label(
            self.container,
            text="● Ingresa una contraseña para analizar",
            bg="#14141e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 8),
            anchor="w"
        )
        self.estado_label.pack(pady=(4, 8), padx=20, fill="x")
    
    def toggle_mostrar(self):
        """Muestra u oculta la contraseña"""
        if self.mostrar_var.get():
            self.entry_contrasena.config(show="")
            self.btn_mostrar.config(text="🙈 Ocultar")
            self.mostrar_var.set(False)
        else:
            self.entry_contrasena.config(show="•")
            self.btn_mostrar.config(text="👁️ Mostrar")
            self.mostrar_var.set(True)
    
    def pegar_portapapeles(self):
        """Pega el contenido del portapapeles en el campo de contraseña"""
        try:
            contenido = self.root.clipboard_get()
            self.entry_contrasena.delete(0, tk.END)
            self.entry_contrasena.insert(0, contenido)
            self.estado_label.config(text="● Contenido pegado desde el portapapeles", fg=self.colores["verde"])
        except:
            messagebox.showwarning("Advertencia", "No se pudo acceder al portapapeles o está vacío")
    
    def calcular_puntaje(self, contrasena):
        """Calcula el puntaje de fortaleza usando el sistema unificado (8 puntos)"""
        return calcular_puntaje_password(contrasena)
    
    def analizar(self):
        """Analiza la fortaleza de la contraseña"""
        contrasena = self.entry_contrasena.get()
        
        if not contrasena:
            messagebox.showwarning("Advertencia", "Ingresa una contraseña para analizar")
            return
        
        # Calcular puntaje usando el sistema unificado
        puntaje, max_puntaje, resultados, mayus, minus, digitos, simbolos, longitud = self.calcular_puntaje(contrasena)
        
        # Calcular porcentaje
        porcentaje = int((puntaje / max_puntaje) * 100)
        
        # Determinar nivel
        if porcentaje >= 80:
            nivel = "🔒 FUERTE"
            color = self.colores["verde"]
            descripcion = "¡Excelente contraseña! Es muy segura."
        elif porcentaje >= 60:
            nivel = "⚡ MEDIA"
            color = self.colores["naranja"]
            descripcion = "Contraseña aceptable, pero puede mejorar."
        else:
            nivel = "⚠️ DÉBIL"
            color = self.colores["rojo"]
            descripcion = "¡Contraseña insegura! Considera cambiarla."
        
        # Mostrar resultados
        self.resultados_texto.delete(1.0, tk.END)
        self.resultados_texto.insert(tk.END, f"ANÁLISIS DE CONTRASEÑA\n")
        self.resultados_texto.insert(tk.END, f"{'='*40}\n\n")
        self.resultados_texto.insert(tk.END, f"Nivel: {nivel}\n")
        self.resultados_texto.insert(tk.END, f"Puntuación: {puntaje}/{max_puntaje} ({porcentaje}%)\n\n")
        self.resultados_texto.insert(tk.END, "DETALLES:\n")
        self.resultados_texto.insert(tk.END, f"{'-'*30}\n")
        for resultado in resultados:
            self.resultados_texto.insert(tk.END, f"{resultado}\n")
        self.resultados_texto.insert(tk.END, f"\n{descripcion}")
        
        # Actualizar barra de fortaleza
        self.barra_fortaleza.delete("all")
        ancho = self.barra_fortaleza.winfo_width()
        if ancho > 0:
            self.barra_fortaleza.create_rectangle(
                0, 0, int(ancho * porcentaje / 100), 10, 
                fill=color, outline=""
            )
        
        self.fortaleza_texto.config(text=f"{nivel} ({porcentaje}%)", fg=color)
        self.estado_label.config(text=f"● Análisis completado: {nivel}", fg=color)


class GeneradorContrasenas:
    def __init__(self, root, volver_callback):
        self.root = root
        self.volver_callback = volver_callback
        self.root.title("Pypher - Generador de Contraseñas")
        self.root.geometry("520x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0f")
        
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # === Configuración de colores ===
        self.colores = {
            "bg_principal": "#0a0a0f",
            "bg_frame": "#14141e",
            "bg_card": "#1c1c2e",
            "bg_entry": "#252540",
            "bg_hover": "#2a2a4a",
            "fg_texto": "#e8e8f0",
            "fg_secundario": "#8888aa",
            "fg_titulo": "#ffffff",
            "verde": "#00d4aa",
            "verde_oscuro": "#00b894",
            "rojo": "#ff6b6b",
            "rojo_oscuro": "#e74c4c",
            "azul": "#4facfe",
            "azul_oscuro": "#2d7dd2",
            "naranja": "#ff9f43",
            "morado": "#a66cff",
            "rosa": "#ff6b9d",
            "cyan": "#00d2ff",
            "gris_borde": "#2a2a3e"
        }
        
        # === Caracteres seguros ===
        self.caracteres_seguros = "!@#$%&()-_=+[]{}?"
        self.caracteres_completos = string.ascii_letters + string.digits + self.caracteres_seguros
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # === Frame principal ===
        self.main_frame = tk.Frame(
            self.root,
            bg=self.colores["bg_principal"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === Contenedor principal ===
        self.container = tk.Frame(
            self.main_frame,
            bg="#14141e",
            relief="flat",
            bd=0
        )
        self.container.pack(fill="both", expand=True)
        
        # === Título ===
        titulo_frame = tk.Frame(self.container, bg="#14141e")
        titulo_frame.pack(pady=(10, 2), fill="x")
        
        titulo = tk.Label(
            titulo_frame,
            text="🐍 Pypher",
            bg="#14141e",
            fg=self.colores["fg_titulo"],
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack()
        
        subtitulo = tk.Label(
            titulo_frame,
            text="Generador de contraseñas seguras",
            bg="#14141e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 10)
        )
        subtitulo.pack(pady=(0, 5))
        
        # === Línea decorativa ===
        linea = tk.Frame(self.container, bg="#2a2a3e", height=1)
        linea.pack(fill="x", padx=20, pady=(0, 8))
        
        # === Tarjeta 1: Generar Contraseña ===
        card_gen = tk.Frame(
            self.container,
            bg="#1c1c2e",
            relief="flat",
            bd=0
        )
        card_gen.pack(pady=3, padx=15, fill="x")
        
        tk.Label(
            card_gen,
            text="GENERAR",
            bg="#1c1c2e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(8, 4), padx=15)
        
        # === Fila: Longitud + Botones ===
        frame_controles = tk.Frame(card_gen, bg="#1c1c2e")
        frame_controles.pack(pady=4, padx=15, fill="x")
        
        # Grupo Longitud
        frame_longitud = tk.Frame(frame_controles, bg="#1c1c2e")
        frame_longitud.pack(side="left")
        
        tk.Label(
            frame_longitud,
            text="Longitud",
            bg="#1c1c2e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 8))
        
        self.longitud_var = tk.IntVar(value=10)
        self.spin_longitud = tk.Spinbox(
            frame_longitud,
            from_=8,
            to=20,
            width=4,
            textvariable=self.longitud_var,
            state="readonly",
            font=("Segoe UI", 11, "bold"),
            bg="#252540",
            fg="#ffffff",
            relief="flat",
            bd=0,
            readonlybackground="#252540",
            buttonbackground="#2a2a4a"
        )
        self.spin_longitud.pack(side="left")
        
        # Grupo Botones
        frame_botones = tk.Frame(frame_controles, bg="#1c1c2e")
        frame_botones.pack(side="right")
        
        self.btn_generar = self.crear_boton_moderno(
            frame_botones,
            "✨ Generar",
            self.generar,
            self.colores["rojo"],
            self.colores["rojo_oscuro"],
            side="left",
            padx=12
        )
        
        self.btn_copiar = self.crear_boton_moderno(
            frame_botones,
            "📋 Copiar",
            self.copiar_portapapeles,
            "#2a2a4a",
            "#3a3a5a",
            side="left",
            padx=12,
            disabled=True
        )
        
        # Contraseña
        frame_pass = tk.Frame(card_gen, bg="#1c1c2e")
        frame_pass.pack(pady=2, padx=15, fill="x")
        
        tk.Label(
            frame_pass,
            text="Contraseña",
            bg="#1c1c2e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        self.contrasena_var = tk.StringVar()
        self.entry_contrasena = tk.Entry(
            frame_pass,
            textvariable=self.contrasena_var,
            font=("Consolas", 12, "bold"),
            state="readonly",
            bg="#0d0d1a",
            fg=self.colores["verde"],
            relief="flat",
            bd=0,
            readonlybackground="#0d0d1a",
            highlightthickness=1,
            highlightcolor="#2a2a3e",
            highlightbackground="#2a2a3e"
        )
        self.entry_contrasena.pack(pady=(4, 6), fill="x", ipady=5)
        
        # Barra de fortaleza
        frame_fortaleza = tk.Frame(card_gen, bg="#1c1c2e")
        frame_fortaleza.pack(pady=2, padx=15, fill="x")
        
        fortaleza_container = tk.Frame(frame_fortaleza, bg="#1c1c2e")
        fortaleza_container.pack(fill="x")
        
        self.barra_fortaleza = tk.Canvas(
            fortaleza_container,
            height=6,
            bg="#1a1a2e",
            highlightthickness=0,
            relief="flat"
        )
        self.barra_fortaleza.pack(fill="x", pady=(4, 2))
        
        self.fortaleza_texto = tk.Label(
            fortaleza_container,
            text="",
            bg="#1c1c2e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 10, "bold")
        )
        self.fortaleza_texto.pack()
        
        # Estadísticas
        frame_stats = tk.Frame(card_gen, bg="#1c1c2e")
        frame_stats.pack(pady=(4, 6), padx=15, fill="x")
        
        estilo_stat = {"bg": "#1c1c2e", "font": ("Segoe UI", 8, "bold")}
        
        stats_frame = tk.Frame(frame_stats, bg="#1c1c2e")
        stats_frame.pack()
        
        self.stat_mayus = tk.Label(stats_frame, text="0 May", fg=self.colores["rosa"], **estilo_stat)
        self.stat_mayus.pack(side="left", padx=5)
        
        self.stat_minus = tk.Label(stats_frame, text="0 Min", fg=self.colores["cyan"], **estilo_stat)
        self.stat_minus.pack(side="left", padx=5)
        
        self.stat_numeros = tk.Label(stats_frame, text="0 Núm", fg=self.colores["naranja"], **estilo_stat)
        self.stat_numeros.pack(side="left", padx=5)
        
        self.stat_simbolos = tk.Label(stats_frame, text="0 Sím", fg=self.colores["morado"], **estilo_stat)
        self.stat_simbolos.pack(side="left", padx=5)
        
        self.stat_longitud = tk.Label(stats_frame, text="0 Car", fg=self.colores["azul"], **estilo_stat)
        self.stat_longitud.pack(side="left", padx=5)
        
        # === Línea divisoria ===
        linea2 = tk.Frame(self.container, bg="#2a2a3e", height=1)
        linea2.pack(fill="x", padx=20, pady=(6, 6))
        
        # === Tarjeta 2: Datos del Archivo ===
        card_datos = tk.Frame(
            self.container,
            bg="#1c1c2e",
            relief="flat",
            bd=0
        )
        card_datos.pack(pady=3, padx=15, fill="x")
        
        tk.Label(
            card_datos,
            text="ARCHIVO",
            bg="#1c1c2e",
            fg=self.colores["fg_secundario"],
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(8, 4), padx=15)
        
        # Nombre
        frame_nombre = tk.Frame(card_datos, bg="#1c1c2e")
        frame_nombre.pack(pady=2, padx=15, fill="x")
        
        tk.Label(
            frame_nombre,
            text="Nombre",
            bg="#1c1c2e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        frame_nombre_input = tk.Frame(frame_nombre, bg="#1c1c2e")
        frame_nombre_input.pack(fill="x", pady=(2, 4))
        
        self.nombre_archivo = tk.Entry(
            frame_nombre_input,
            font=("Segoe UI", 10),
            bg="#252540",
            fg="#ffffff",
            relief="flat",
            bd=0,
            insertbackground="white",
            highlightthickness=1,
            highlightcolor="#2a2a3e",
            highlightbackground="#2a2a3e"
        )
        self.nombre_archivo.pack(side="left", fill="x", expand=True, ipady=4)
        
        tk.Label(
            frame_nombre_input,
            text=".txt",
            bg="#1c1c2e",
            fg=self.colores["verde"],
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(8, 0))
        
        # Fecha
        frame_fecha = tk.Frame(card_datos, bg="#1c1c2e")
        frame_fecha.pack(pady=2, padx=15, fill="x")
        
        tk.Label(
            frame_fecha,
            text="Fecha",
            bg="#1c1c2e",
            fg=self.colores["fg_texto"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        frame_fecha_input = tk.Frame(frame_fecha, bg="#1c1c2e")
        frame_fecha_input.pack(fill="x", pady=(2, 4))
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.fecha_var = tk.StringVar(value=fecha_actual)
        self.entry_fecha = tk.Entry(
            frame_fecha_input,
            textvariable=self.fecha_var,
            font=("Segoe UI", 10),
            bg="#252540",
            fg="#ffffff",
            relief="flat",
            bd=0,
            insertbackground="white",
            highlightthickness=1,
            highlightcolor="#2a2a3e",
            highlightbackground="#2a2a3e"
        )
        self.entry_fecha.pack(side="left", fill="x", expand=True, ipady=4)
        
        self.btn_restaurar_fecha = self.crear_boton_moderno(
            frame_fecha_input,
            "↻",
            self.restaurar_fecha,
            "#2a2a4a",
            "#3a3a5a",
            side="left",
            padx=10,
            ancho=3
        )
        
        # === Botón Guardar ===
        frame_guardar = tk.Frame(self.container, bg="#14141e")
        frame_guardar.pack(pady=(10, 6), padx=15, fill="x")
        
        self.btn_guardar = self.crear_boton_moderno(
            frame_guardar,
            "💾 Guardar Archivo",
            self.guardar,
            self.colores["azul"],
            self.colores["azul_oscuro"],
            side="top",
            padx=30,
            expand=True
        )
        
        # === Botón Volver ===
        frame_volver = tk.Frame(self.container, bg="#14141e")
        frame_volver.pack(pady=(5, 0), padx=15, fill="x")
        
        self.btn_volver = tk.Button(
            frame_volver,
            text="← Volver al Menú",
            command=self.volver_callback,
            bg="#2a2a4a",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2"
        )
        self.btn_volver.pack(fill="x")
        
        # === CRÉDITOS ===
        linea_creditos = tk.Frame(self.container, bg="#2a2a3e", height=1)
        linea_creditos.pack(fill="x", padx=20, pady=(8, 8))
        
        creditos_frame = tk.Frame(
            self.container,
            bg="#1a1a2a",
            relief="flat",
            bd=0
        )
        creditos_frame.pack(pady=(0, 5), padx=20, fill="x")
        
        creditos_inner = tk.Frame(creditos_frame, bg="#1a1a2a")
        creditos_inner.pack(pady=8)
        
        tk.Label(
            creditos_inner,
            text="🐍 Desarrollado por",
            bg="#1a1a2a",
            fg="#8888aa",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        nombre_link = tk.Label(
            creditos_inner,
            text="leoXxit0",
            bg="#1a1a2a",
            fg="#4facfe",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        )
        nombre_link.pack(side="left", padx=(5, 10))
        nombre_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/leoXxit0"))
        
        tk.Label(
            creditos_inner,
            text="|",
            bg="#1a1a2a",
            fg="#444466",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        github_link = tk.Label(
            creditos_inner,
            text="GitHub",
            bg="#1a1a2a",
            fg="#a66cff",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        github_link.pack(side="left", padx=(10, 5))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/leoXxit0"))
        
        tk.Label(
            creditos_inner,
            text="🐍",
            bg="#1a1a2a",
            fg="#555577",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(5, 0))
        
        # === Estado ===
        self.estado_label = tk.Label(
            self.container,
            text="● Listo",
            bg="#14141e",
            fg=self.colores["verde"],
            font=("Segoe UI", 8),
            anchor="w"
        )
        self.estado_label.pack(pady=(4, 8), padx=20, fill="x")
    
    # === Métodos auxiliares ===
    def crear_boton_moderno(self, parent, texto, comando, color, hover_color, side="left", padx=15, ancho=None, disabled=False, expand=False):
        btn = tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=padx,
            pady=6,
            cursor="hand2",
            width=ancho,
            state="disabled" if disabled else "normal",
            activebackground=hover_color,
            activeforeground="white"
        )
        
        if not disabled:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=hover_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=color))
        
        if expand and side == "top":
            btn.pack(fill="x", expand=True)
        elif expand:
            btn.pack(side=side, padx=2, fill="x", expand=True)
        else:
            btn.pack(side=side, padx=2)
        
        return btn
    
    def calcular_puntaje_generador(self, contrasena, longitud):
        """Calcula el puntaje de fortaleza usando el sistema unificado (8 puntos),
        el mismo que usa el Analizador (calcular_puntaje_password)."""
        puntaje, max_puntaje, _detalles, _mayus, _minus, _digitos, _simbolos, _longitud = (
            calcular_puntaje_password(contrasena)
        )
        return puntaje, max_puntaje
    
    def generar(self):
        """Genera una contraseña aleatoria segura"""
        longitud = self.longitud_var.get()
        
        # Asegurar que tenga al menos un carácter de cada tipo
        contrasena = []
        contrasena.append(random.choice(string.ascii_uppercase))  # Mayúscula
        contrasena.append(random.choice(string.ascii_lowercase))  # Minúscula
        contrasena.append(random.choice(string.digits))           # Número
        contrasena.append(random.choice(self.caracteres_seguros)) # Símbolo
        
        # Completar el resto
        for _ in range(longitud - 4):
            contrasena.append(random.choice(self.caracteres_completos))
        
        # Mezclar
        random.shuffle(contrasena)
        contrasena_final = ''.join(contrasena)
        
        # Actualizar interfaz
        self.contrasena_var.set(contrasena_final)
        self.btn_copiar.config(state="normal")
        self.btn_copiar.config(bg="#4facfe", fg="white")
        
        # Actualizar estadísticas
        mayus = sum(1 for c in contrasena_final if c.isupper())
        minus = sum(1 for c in contrasena_final if c.islower())
        digitos = sum(1 for c in contrasena_final if c.isdigit())
        simbolos = len(contrasena_final) - mayus - minus - digitos
        
        self.stat_mayus.config(text=f"{mayus} May")
        self.stat_minus.config(text=f"{minus} Min")
        self.stat_numeros.config(text=f"{digitos} Núm")
        self.stat_simbolos.config(text=f"{simbolos} Sím")
        self.stat_longitud.config(text=f"{longitud} Car")
        
        # Calcular fortaleza usando el sistema unificado
        puntaje, max_puntaje = self.calcular_puntaje_generador(contrasena_final, longitud)
        porcentaje = int((puntaje / max_puntaje) * 100)
        
        # Actualizar barra de fortaleza
        self.barra_fortaleza.delete("all")
        ancho = self.barra_fortaleza.winfo_width()
        
        if porcentaje >= 80:
            color = self.colores["verde"]
            nivel = "🔒 FUERTE"
        elif porcentaje >= 60:
            color = self.colores["naranja"]
            nivel = "⚡ MEDIA"
        else:
            color = self.colores["rojo"]
            nivel = "⚠️ DÉBIL"
        
        if ancho > 0:
            self.barra_fortaleza.create_rectangle(
                0, 0, int(ancho * porcentaje / 100), 6, 
                fill=color, outline=""
            )
        
        self.fortaleza_texto.config(text=f"{nivel} ({porcentaje}%)", fg=color)
        self.estado_label.config(text=f"● Contraseña generada - {nivel}", fg=color)
    
    def copiar_portapapeles(self):
        """Copia la contraseña al portapapeles"""
        contrasena = self.contrasena_var.get()
        if contrasena:
            self.root.clipboard_clear()
            self.root.clipboard_append(contrasena)
            self.estado_label.config(text="● ¡Copiada al portapapeles!", fg=self.colores["verde"])
            messagebox.showinfo("Éxito", "Contraseña copiada al portapapeles")
    
    def restaurar_fecha(self):
        """Restaura la fecha actual"""
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.fecha_var.set(fecha_actual)
        self.estado_label.config(text="● Fecha restaurada", fg=self.colores["verde"])
    
    def guardar(self):
        """Guarda la contraseña en un archivo .txt"""
        contrasena = self.contrasena_var.get()
        if not contrasena:
            messagebox.showwarning("Advertencia", "Primero genera una contraseña")
            return
        
        nombre = self.nombre_archivo.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingresa un nombre para el archivo")
            return
        
        fecha = self.fecha_var.get()
        
        # Crear contenido
        contenido = f"""========================================
    Pypher - Contraseña Generada
========================================

📅 Fecha: {fecha}
📝 Nombre: {nombre}
🔐 Contraseña: {contrasena}

🔒 Nivel de seguridad: {self.fortaleza_texto.cget("text")}

📊 Estadísticas:
- Longitud: {len(contrasena)} caracteres
- Mayúsculas: {self.stat_mayus.cget("text")}
- Minúsculas: {self.stat_minus.cget("text")}
- Números: {self.stat_numeros.cget("text")}
- Símbolos: {self.stat_simbolos.cget("text")}

========================================
    Generado con Pypher
    https://github.com/leoXxit0
========================================
"""
        
        # Guardar archivo
        try:
            nombre_archivo = f"{nombre}.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            self.estado_label.config(
                text=f"● Archivo guardado: {nombre_archivo}", 
                fg=self.colores["verde"]
            )
            messagebox.showinfo(
                "Éxito", 
                f"¡Archivo guardado exitosamente!\n\n📁 {nombre_archivo}\n📂 {os.path.abspath(nombre_archivo)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
            self.estado_label.config(text=f"● Error al guardar", fg=self.colores["rojo"])


class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Pypher - Menú Principal")
        self.root.geometry("500x420")
        self.root.configure(bg="#0a0a0f")
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.root, bg="#0a0a0f")
        titulo_frame.pack(pady=30)
        
        titulo = tk.Label(
            titulo_frame,
            text="🐍 Pypher",
            font=("Segoe UI", 32, "bold"),
            bg="#0a0a0f",
            fg="#00d4aa"
        )
        titulo.pack()
        
        subtitulo = tk.Label(
            titulo_frame,
            text="Gestor de Contraseñas Seguras",
            font=("Segoe UI", 13),
            bg="#0a0a0f",
            fg="#8888aa"
        )
        subtitulo.pack(pady=(5, 25))
        
        # Botones
        frame_botones = tk.Frame(self.root, bg="#0a0a0f")
        frame_botones.pack(pady=10)
        
        # Botón Generador
        btn_generador = tk.Button(
            frame_botones,
            text="🔐 Generador de Contraseñas",
            command=self.abrir_generador,
            bg="#4facfe",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            width=28,
            activebackground="#2d7dd2",
            activeforeground="white"
        )
        btn_generador.pack(pady=10)
        btn_generador.bind("<Enter>", lambda e: btn_generador.config(bg="#2d7dd2"))
        btn_generador.bind("<Leave>", lambda e: btn_generador.config(bg="#4facfe"))
        
        # Botón Analizador
        btn_analizador = tk.Button(
            frame_botones,
            text="🔍 Analizador de Contraseñas",
            command=self.abrir_analizador,
            bg="#a66cff",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            width=28,
            activebackground="#7b4cb8",
            activeforeground="white"
        )
        btn_analizador.pack(pady=10)
        btn_analizador.bind("<Enter>", lambda e: btn_analizador.config(bg="#7b4cb8"))
        btn_analizador.bind("<Leave>", lambda e: btn_analizador.config(bg="#a66cff"))
        
        # Botón Generador de Wordlist (Próximamente) - espacio abierto para futuras contribuciones
        btn_wordlist = tk.Button(
            frame_botones,
            text="Generador de Wordlist (?)",
            command=self.wordlist_proximamente,
            bg="#2a2a4a",
            fg="#8888aa",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            width=28,
            activebackground="#2a2a4a",
            activeforeground="#8888aa"
        )
        btn_wordlist.pack(pady=10)
        
        # Botón Salir
        btn_salir = tk.Button(
            frame_botones,
            text="✖ Salir",
            command=self.root.quit,
            bg="#ff6b6b",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
            padx=35,
            pady=14,
            cursor="hand2",
            width=28,
            activebackground="#e74c4c",
            activeforeground="white"
        )
        btn_salir.pack(pady=10)
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#e74c4c"))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg="#ff6b6b"))
        
        # Créditos
        creditos = tk.Label(
            self.root,
            text="🐍 Desarrollado por leoXxit0 | GitHub: @leoXxit0",
            font=("Segoe UI", 10),
            bg="#0a0a0f",
            fg="#444466"
        )
        creditos.pack(side="bottom", pady=20)
    
    def abrir_generador(self):
        """Abre el generador de contraseñas"""
        def volver_menu():
            self.crear_interfaz()
        GeneradorContrasenas(self.root, volver_menu)
    
    def abrir_analizador(self):
        """Abre el analizador de contraseñas"""
        def volver_menu():
            self.crear_interfaz()
        AnalizadorContrasenas(self.root, volver_menu)
    
    def wordlist_proximamente(self):
        """Placeholder para el futuro Generador de Wordlist (contribuciones abiertas)"""
        messagebox.showinfo(
            "Próximamente",
            "Generador de Wordlist\n\n"
            "Esta función todavía no está disponible.\n"
            "¡Es un espacio abierto para futuras contribuciones al proyecto!"
        )


# === PUNTO DE ENTRADA PRINCIPAL ===
if __name__ == "__main__":
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Iniciar con el menú principal
        app = MenuPrincipal(root)
        
        # Ejecutar la aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
