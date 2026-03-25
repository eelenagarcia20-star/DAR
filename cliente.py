import socket
import threading
import tkinter as tk
from tkinter import messagebox
import queue

# --- CONFIGURACIÓN ---
# Asegúrate de que esta IP sea la de tu VM Servidor
HOST = '192.168.1.1' 
PORT = 55555

class ClienteGrafico:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tres en Raya Online")
        self.root.geometry("350x450")
        
        self.cola = queue.Queue()
        self.botones = []
        self.mi_simbolo = ""
        self.sock = None
        
        self.crear_interfaz()
        self.conectar_red_async()

    def crear_interfaz(self):
        """Crea la interfaz gráfica."""
        self.lbl_estado = tk.Label(self.root, text="Iniciando...", font=('Arial', 10, 'italic'), fg="gray")
        self.lbl_estado.pack(pady=10)

        self.frame_tablero = tk.Frame(self.root)
        self.frame_tablero.pack(pady=5)

        for i in range(9):
            btn = tk.Button(self.frame_tablero, text=" ", font=('Arial', 20, 'bold'), 
                            width=5, height=2, bg="#f0f0f0",
                            command=lambda i=i: self.enviar_movimiento(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            btn.config(state="disabled")
            self.botones.append(btn)
        
        self.btn_join = tk.Button(self.root, text="BUSCAR PARTIDA", font=('Arial', 12, 'bold'),
                                  bg="#4caf50", fg="white", activebackground="#45a049",
                                  command=self.solicitar_join, height=2)
        self.btn_join.pack(fill="x", padx=40, pady=20)
        self.btn_join.config(state="disabled") # Desactivado hasta conectar

    def conectar_red_async(self):
        """Intenta conectar al servidor sin bloquear la ventana."""
        self.lbl_estado.config(text=f"Conectando a {HOST}...")
        
        def tarea_conexion():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5) # 5 segundos de margen
                self.sock.connect((HOST, PORT))
                self.sock.settimeout(None) # Quitar timeout para el juego
                
                # Éxito: Actualizamos UI y lanzamos receptor
                self.root.after(0, lambda: self.lbl_estado.config(text="¡Conectado!", fg="blue"))
                self.root.after(0, lambda: self.btn_join.config(state="normal"))
                
                threading.Thread(target=self.hilo_recibir, daemon=True).start()
            except Exception as e:
                self.root.after(0, lambda: self.lbl_estado.config(text="Error de conexión", fg="red"))
                print(f"DEBUG: No se pudo conectar: {e}")

        threading.Thread(target=tarea_conexion, daemon=True).start()
        self.revisar_cola_periodicamente()

    def solicitar_join(self):
        try:
            self.sock.send("JOIN\r\n".encode())
            self.btn_join.config(state="disabled", text="BUSCANDO...", bg="#9e9e9e")
            self.lbl_estado.config(text="Esperando rival...", fg="orange")
            self.limpiar_tablero_grafico()
        except:
            messagebox.showerror("Error", "Conexión perdida con el servidor.")

    def enviar_movimiento(self, i):
        try:
            self.sock.send(f"MOVE {i}\r\n".encode())
            self.gestionar_bloqueo_botones(False)
        except:
            pass

    def hilo_recibir(self):
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data: break
                for linea in data.split("\r\n"):
                    if linea.strip():
                        self.cola.put(linea.strip())
            except:
                break

    def revisar_cola_periodicamente(self):
        while not self.cola.empty():
            mensaje = self.cola.get()
            self.procesar_logica_servidor(mensaje)
        self.root.after(100, self.revisar_cola_periodicamente)

    def procesar_logica_servidor(self, msg):
        partes = msg.split()
        if not partes: return
        cmd = partes[0]

        if cmd == "START":
            self.mi_simbolo = partes[2]
            self.lbl_estado.config(text=f"¡PARTIDA! Eres la '{self.mi_simbolo}'", fg="green")
            self.limpiar_tablero_grafico()
            self.gestionar_bloqueo_botones(self.mi_simbolo == "X")

        elif cmd == "UPDATE":
            pos, sym = int(partes[1]), partes[2]
            self.dibujar_marca(pos, sym)
            if sym != self.mi_simbolo:
                self.gestionar_bloqueo_botones(True)
                self.lbl_estado.config(text="¡Tu turno!", fg="green")
            else:
                self.gestionar_bloqueo_botones(False)
                self.lbl_estado.config(text="Turno del rival...", fg="gray")

        elif cmd == "GAMEOVER":
            motivo = partes[1]
            if motivo == "DESCONEXIÓN":
                messagebox.showwarning("Fin de Partida", "El rival se ha desconectado.")
            elif motivo == "EMPATE":
                messagebox.showinfo("Fin de Partida", "¡Empate!")
            else:
                messagebox.showinfo("Fin de Partida", f"Ganador: {motivo}")
            
            self.btn_join.config(state="normal", text="BUSCAR PARTIDA", bg="#4caf50")
            self.lbl_estado.config(text="Partida finalizada.", fg="blue")
            self.gestionar_bloqueo_botones(False)

        elif cmd == "WAITING":
            self.lbl_estado.config(text="En cola de espera...", fg="orange")

    def dibujar_marca(self, pos, sym):
        color_fondo = "#f44336" if sym == "X" else "#2196f3"
        self.botones[pos].config(text=sym, state="disabled", bg=color_fondo, fg="white")

    def gestionar_bloqueo_botones(self, habilitar):
        for b in self.botones:
            if b['text'] == " ":
                b.config(state="normal" if habilitar else "disabled")

    def limpiar_tablero_grafico(self):
        for b in self.botones:
            b.config(text=" ", bg="#f0f0f0", state="disabled")

if __name__ == "__main__":
    ClienteGrafico().root.mainloop()