import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json
from datetime import datetime


# Archivo de reservas persistente
archivo_reservas = "reservas.json"

# Funciones para persistencia
def cargar_reservas():
    if os.path.exists(archivo_reservas):
        with open(archivo_reservas, "r") as f:
            return json.load(f)
    return []

def guardar_reservas():
    with open(archivo_reservas, "w") as f:
        json.dump(reservas, f, indent=4)

# Horarios de 06:00 a 22:00
def generar_horarios():
    return [f"{h:02d}:00 - {h+1:02d}:00" for h in range(6, 22)]

# Canchas con nombres reales
canchas = [
    {"id": 1, "nombre": "Parque de San Isidro", "horarios": generar_horarios()},
    {"id": 2, "nombre": "Parque Bosques del Norte", "horarios": generar_horarios()},
    {"id": 3, "nombre": "Parque Sagrado Corazón", "horarios": generar_horarios()},
    {"id": 4, "nombre": "Parque Las Mercedes", "horarios": generar_horarios()},
    {"id": 5, "nombre": "Parque de Los Andes", "horarios": generar_horarios()}
]

# Cargar reservas existentes al iniciar
reservas = cargar_reservas()

# Función para recomendar horarios menos reservados
def obtener_horarios_menos_reservados():
    conteo = {h: 0 for h in generar_horarios()}
    for r in reservas:
        hora = r["hora"]
        if hora in conteo:
            conteo[hora] += 1
    horarios_ordenados = sorted(conteo.items(), key=lambda x: x[1])
    return horarios_ordenados

        

class AppCanchita:
    def __init__(self, usuario):
        self.usuario = usuario
        self.ventana = tk.Tk()
        self.ventana.iconbitmap('D:\\Downloads\\app tgs\\Balon de futbol.ico')
        self.ventana.title("Canchita - Alquiler de Canchas")
        self.ventana.geometry("900x600")
        self.ventana.configure(bg="white")


        self.sidebar = tk.Frame(self.ventana, bg="#34495e", width=200)
        self.sidebar.pack(side="left", fill="y")

        opciones = [
            ("Ver Canchas", self.ver_canchas),
            ("Reservar Cancha", self.reservar_cancha),
            ("Historial", self.ver_historial),
            ("Recomendaciones", self.recomendar_horario)
        ]

        for texto, accion in opciones:
            tk.Button(self.sidebar, text=texto, font=("Arial", 12), bg="#34495e", fg="white",
                      relief="flat", activebackground="#2c3e50", command=accion).pack(fill="x", pady=5, padx=10)

        self.area_contenido = tk.Frame(self.ventana, bg="white")
        self.area_contenido.pack(expand=True, fill="both")
        self.mostrar_mensaje("Bienvenido, " + usuario)

        self.ventana.mainloop()

    def mostrar_mensaje(self, texto):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()
        tk.Label(self.area_contenido, text=texto, font=("Arial", 18), bg="white", fg="#2c3e50").pack(pady=20)

    def ver_canchas(self):
        self.mostrar_mensaje("Canchas disponibles:")
        for cancha in canchas:
            horarios = ", ".join(cancha["horarios"])
            tk.Label(self.area_contenido, text=f'{cancha["nombre"]}\nHorarios disponibles: {horarios}',
                     bg="white", fg="black", font=("Arial", 12), justify="left", wraplength=600).pack(pady=10)

    def reservar_cancha(self):
        self.mostrar_mensaje("Reservar cancha")
        self.seleccion_cancha = tk.StringVar()
        self.seleccion_hora = tk.StringVar()

        nombres = [cancha["nombre"] for cancha in canchas]
        tk.Label(self.area_contenido, text="Selecciona una cancha:", bg="white", font=("Arial", 12)).pack(pady=5)
        tk.OptionMenu(self.area_contenido, self.seleccion_cancha, *nombres).pack(pady=5)

        tk.Label(self.area_contenido, text="Selecciona un horario:", bg="white", font=("Arial", 12)).pack(pady=5)
        tk.OptionMenu(self.area_contenido, self.seleccion_hora, *generar_horarios()).pack(pady=5)

        tk.Button(self.area_contenido, text="Reservar", bg="#27ae60", fg="white",
                  font=("Arial", 12, "bold"), padx=10, pady=5,
                  command=self.confirmar_reserva).pack(pady=15)

    def confirmar_reserva(self):
        cancha = self.seleccion_cancha.get()
        hora = self.seleccion_hora.get()

        if not cancha or not hora:
            messagebox.showwarning("Campos incompletos", "Selecciona cancha y horario.")
            return

        for r in reservas:
            if r["cancha"] == cancha and r["hora"] == hora:
                messagebox.showerror("Reservada", f"{hora} ya está reservada en {cancha}")
                return

        for c in canchas:
            if c["nombre"] == cancha:
                if hora in c["horarios"]:
                    reservas.append({
                        "usuario": self.usuario,
                        "cancha": cancha,
                        "hora": hora,
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
                    c["horarios"].remove(hora)
                    guardar_reservas()
                    messagebox.showinfo("Reserva exitosa", f"Reservaste {cancha} de {hora}")
                    self.recomendar_horario()  # Mostrar recomendaciones después de reservar
                    return

        messagebox.showerror("Error", "La cancha u hora seleccionada no es válida")

    def ver_historial(self):
        self.mostrar_mensaje("Historial de reservas:")
        historial = [r for r in reservas if r["usuario"] == self.usuario]
        if historial:
            for r in historial:
                tk.Label(self.area_contenido,
                         text=f"{r['fecha']} - {r['cancha']} - {r['hora']}",
                         bg="white", font=("Arial", 12)).pack(pady=2)
        else:
            tk.Label(self.area_contenido, text="No tienes reservas aún.", bg="white", font=("Arial", 12)).pack(pady=10)

    def recomendar_horario(self):
        self.mostrar_mensaje("Horarios menos reservados (recomendados):")
        horarios_ordenados = obtener_horarios_menos_reservados()
        mostrados = 0
        for hora, cantidad in horarios_ordenados:
            if mostrados >= 5:
                break
            for cancha in canchas:
                if hora in cancha["horarios"]:
                    tk.Label(self.area_contenido, text=f"{hora} - {cantidad} reservas", bg="white", font=("Arial", 12)).pack(pady=2)
                    mostrados += 1
                    break
        if mostrados == 0:
            tk.Label(self.area_contenido, text="No hay horarios disponibles actualmente.", bg="white", font=("Arial", 12)).pack(pady=10)

class LoginForm:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Inicio de sesión")
        self.ventana.geometry("1000x600")
        self.ventana.iconbitmap('D:\\Downloads\\app tgs\\Balon de futbol.ico')
        self.ventana.configure(bg="#f0f0f0")
        self.archivo_usuarios = "usuarios.txt"
        if not os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "w") as f:
                pass

        self.crear_interfaz()
        self.ventana.mainloop()

    def crear_interfaz(self):
        contenedor = tk.Frame(self.ventana, bg="#f0f0f0")
        contenedor.pack(fill='both', expand=True)

        marco_izquierdo = tk.Frame(contenedor, width=300, bg="#3399ff")
        marco_izquierdo.pack(side="left", fill="both")
        
        try:
            ruta_imagen = "Foto canchas de futbol"  # Cambia la ruta si usas otra carpeta o nombre
            imagen_logo = Image.open(ruta_imagen)
            imagen_logo = imagen_logo.resize((200, 200), Image.ANTIALIAS)  # Ajusta el tamaño si lo deseas
            logo = ImageTk.PhotoImage(imagen_logo)

            etiqueta_logo = tk.Label(marco_izquierdo, image=logo, bg="#3399ff")
            etiqueta_logo.image = logo  # MUY IMPORTANTE: evita que se elimine de memoria
            etiqueta_logo.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print("Error al cargar imagen:", e)
            tk.Label(marco_izquierdo, font=("Arial", 20), bg="#3399ff", fg="white").place(relx=0.5, rely=0.5, anchor="center")
            
        
        marco_derecho = tk.Frame(contenedor, bg="#f0f0f0", padx=40, pady=40)
        marco_derecho.pack(fill="both", expand=True)

        tk.Label(marco_derecho, text="Inicio de sesión", font=("Arial", 24), bg="#f0f0f0", fg="gray").pack(pady=20)
        tk.Label(marco_derecho, text="Usuario", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        self.usuario_entry = tk.Entry(marco_derecho, font=("Arial", 12), width=30)
        self.usuario_entry.pack()

        tk.Label(marco_derecho, text="Contraseña", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        self.contraseña_entry = tk.Entry(marco_derecho, show="*", font=("Arial", 12), width=30)
        self.contraseña_entry.pack()

        tk.Button(marco_derecho, text="Iniciar sesión", font=("Arial", 12, "bold"), bg="#3399ff", fg="white",
                  width=25, command=self.iniciar_sesion).pack(pady=15)
        tk.Button(marco_derecho, text="Registrar usuario", font=("Arial", 10), bg="#cccccc",
                  width=25, command=self.registrar_usuario).pack()

    def registrar_usuario(self):
        usuario = self.usuario_entry.get().strip()
        clave = self.contraseña_entry.get().strip()
        if not usuario or not clave:
            messagebox.showwarning("Advertencia", "Debes ingresar usuario y contraseña")
            return
        with open(self.archivo_usuarios, "r") as f:
            for linea in f:
                if linea.startswith(usuario + ":"):
                    messagebox.showerror("Error", "El usuario ya existe")
                    return
        with open(self.archivo_usuarios, "a") as f:
            f.write(f"{usuario}:{clave}\n")
        messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente")

    def iniciar_sesion(self):
        usuario = self.usuario_entry.get().strip()
        clave = self.contraseña_entry.get().strip()
        with open(self.archivo_usuarios, "r") as f:
            for linea in f:
                u, c = linea.strip().split(":")
                if usuario == u and clave == c:
                    self.ventana.destroy()
                    AppCanchita(usuario)
                    return
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

if __name__ == "__main__":
    LoginForm()



