import tkinter as tk
from tkinter import filedialog, messagebox
import random
import string
from datetime import datetime
import os
import re
import webbrowser

class GeneradorContrasenas:
    def __init__(self, root):
        self.root = root
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
        
        # === Frame principal ===
        self.main_frame = tk.Frame(
            root,
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
            btn.pack(side=side, fill="x", expand=True)
        else:
            btn.pack(side=side, padx=2)
        
        return btn
    
    # === Métodos principales ===
    def generar(self):
        """Genera una contraseña y la copia automáticamente"""
        longitud = self.longitud_var.get()
        contrasena = ''.join(random.choice(self.caracteres_completos) for _ in range(longitud))
        self.contrasena_var.set(contrasena)
        self.btn_copiar.config(state="normal")
        self.analizar_fortaleza(contrasena)
        
        mayus = sum(1 for c in contrasena if c.isupper())
        minus = sum(1 for c in contrasena if c.islower())
        digitos = sum(1 for c in contrasena if c.isdigit())
        simbolos = len(contrasena) - mayus - minus - digitos
        
        self.stat_mayus.config(text=f"{mayus} May")
        self.stat_minus.config(text=f"{minus} Min")
        self.stat_numeros.config(text=f"{digitos} Núm")
        self.stat_simbolos.config(text=f"{simbolos} Sím")
        self.stat_longitud.config(text=f"{longitud} Car")
        
        # === COPIA AUTOMÁTICA ===
        self.root.clipboard_clear()
        self.root.clipboard_append(contrasena)
        self.estado_label.config(text=f"● Generada y copiada ✅ ({longitud} caracteres)", fg=self.colores["verde"])
    
    def analizar_fortaleza(self, contrasena):
        longitud = len(contrasena)
        puntaje = 0
        if longitud >= 8:
            puntaje += 1
        if longitud >= 12:
            puntaje += 1
        if longitud >= 16:
            puntaje += 1
        if re.search(r"[A-Z]", contrasena):
            puntaje += 1
        if re.search(r"[a-z]", contrasena):
            puntaje += 1
        if re.search(r"\d", contrasena):
            puntaje += 1
        if re.search(r"[!@#$%&()\-_=+[\]{}?]", contrasena):
            puntaje += 1
        
        max_puntaje = 8
        porcentaje = int((puntaje / max_puntaje) * 100)
        
        if porcentaje >= 80:
            color = self.colores["verde"]
            texto = "FUERTE"
        elif porcentaje >= 60:
            color = self.colores["naranja"]
            texto = "MEDIA"
        else:
            color = self.colores["rojo"]
            texto = "DÉBIL"
        
        self.barra_fortaleza.delete("all")
        ancho = self.barra_fortaleza.winfo_width()
        if ancho > 0:
            self.barra_fortaleza.create_rectangle(0, 0, int(ancho * porcentaje / 100), 6, fill=color, outline="")
        
        self.fortaleza_texto.config(text=f"{texto} ({porcentaje}%)", fg=color)
    
    def copiar_portapapeles(self):
        """Copia la contraseña al portapapeles (manual)"""
        contrasena = self.contrasena_var.get()
        if contrasena:
            self.root.clipboard_clear()
            self.root.clipboard_append(contrasena)
            self.estado_label.config(text="● Copiada manualmente ✅", fg=self.colores["verde"])
    
    def restaurar_fecha(self):
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.fecha_var.set(fecha_actual)
        self.estado_label.config(text="● Fecha restaurada", fg=self.colores["verde"])
    
    def guardar(self):
        contrasena = self.contrasena_var.get()
        if not contrasena:
            messagebox.showwarning("Advertencia", "Primero genera una contraseña")
            return
        
        nombre = self.nombre_archivo.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Escribe un nombre para el archivo")
            return
        
        ruta_guardar = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=f"{nombre}.txt",
            title="Guardar archivo"
        )
        
        if not ruta_guardar:
            return
        
        fecha = self.fecha_var.get()
        mayus = sum(1 for c in contrasena if c.isupper())
        minus = sum(1 for c in contrasena if c.islower())
        digitos = sum(1 for c in contrasena if c.isdigit())
        simbolos = len(contrasena) - mayus - minus - digitos
        
        contenido = f"""==================================================
              🐍 PYPHER - REGISTRO DE CONTRASEÑA
==================================================
Fecha de creación : {fecha}
Contraseña        : {contrasena}
Longitud          : {len(contrasena)} caracteres
Mayúsculas        : {mayus}
Minúsculas        : {minus}
Números           : {digitos}
Símbolos          : {simbolos}
Caracteres usados : Letras + Números + !@#$%&()-_=+[]{{}}?
==================================================
Recomendación: Guarda esta contraseña en un lugar seguro.
"""
        
        try:
            with open(ruta_guardar, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            
            messagebox.showinfo("Éxito", f"Archivo guardado correctamente\n\n{ruta_guardar}")
            self.estado_label.config(text=f"● Guardado: {os.path.basename(ruta_guardar)}", fg=self.colores["verde"])
            
            self.contrasena_var.set("")
            self.nombre_archivo.delete(0, tk.END)
            self.barra_fortaleza.delete("all")
            self.fortaleza_texto.config(text="")
            self.stat_mayus.config(text="0 May")
            self.stat_minus.config(text="0 Min")
            self.stat_numeros.config(text="0 Núm")
            self.stat_simbolos.config(text="0 Sím")
            self.stat_longitud.config(text="0 Car")
            self.btn_copiar.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
            self.estado_label.config(text="● Error al guardar", fg="#ff4444")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorContrasenas(root)
    root.mainloop()