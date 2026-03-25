import socket
import threading
import tkinter as tk
from tkinter import messagebox
import queue

HOST, PORT = '192.168.1.1', 55555

class ClienteGrafico:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tres en Raya Red")
        self.root.geometry("350x550")
        
        self.cola = queue.Queue()
        self.botones = []
        self.mi_simbolo = ""
        self.sock = None
        
        self.crear_interfaz()
        self.conectar_red()

    def crear_interfaz(self):
        self.lbl_estado = tk.Label(self.root, text="Buscando servidor...", font=('Arial', 9))
        self.lbl_estado.pack(pady=5)

        self.lbl_turno = tk.Label(self.root, text="CONÉCTATE", font=('Arial', 14, 'bold'), 
                                 bg="#f0f0f0", width=25, height=2)
        self.lbl_turno.pack(pady=10)

        self.frame_tablero = tk.Frame(self.root)
        self.frame_tablero.pack(pady=10)
        for i in range(9):
            btn = tk.Button(self.frame_tablero, text=" ", font=('Arial', 18, 'bold'), 
                            width=5, height=2, bg="#f0f0f0",
                            command=lambda i=i: self.enviar_movimiento(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            btn.config(state="disabled")
            self.botones.append(btn)
        
        self.btn_join = tk.Button(self.root, text="BUSCAR PARTIDA", font=('Arial', 12, 'bold'),
                                  bg="#4caf50", fg="white", height=2, width=20,
                                  command=self.solicitar_join)
        self.btn_join.pack(pady=20)

    def conectar_red(self):
        def tarea():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((HOST, PORT))
                self.root.after(0, lambda: self.btn_join.config(state="normal"))
                self.root.after(0, lambda: self.lbl_estado.config(text="ONLINE", fg="blue"))
                threading.Thread(target=self.hilo_recibir, daemon=True).start()
            except:
                self.root.after(0, lambda: self.lbl_estado.config(text="OFFLINE", fg="red"))
        threading.Thread(target=tarea, daemon=True).start()
        self.root.after(100, self.revisar_cola)

    def solicitar_join(self):
        try:
            self.sock.send("JOIN\r\n".encode())
            self.btn_join.config(state="disabled", text="EN COLA...")
            self.lbl_turno.config(text="ESPERANDO RIVAL...", bg="#ffcc00", fg="black")
            for b in self.botones: b.config(text=" ", bg="#f0f0f0", state="disabled")
        except: pass

    def enviar_movimiento(self, i):
        try:
            self.sock.send(f"MOVE {i}\r\n".encode())
            self.lbl_turno.config(text="ESPERA AL RIVAL", bg="#e0e0e0", fg="black")
            for b in self.botones: b.config(state="disabled")
        except: pass

    def hilo_recibir(self):
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data: break
                for linea in data.split("\r\n"):
                    if linea.strip(): self.cola.put(linea.strip())
            except: break

    def revisar_cola(self):
        while not self.cola.empty():
            msg = self.cola.get()
            partes = msg.split()
            if not partes: continue
            cmd = partes[0]

            if cmd == "START":
                self.mi_simbolo = partes[2]
                turno = (self.mi_simbolo == "X")
                self.lbl_turno.config(text="¡ES TU TURNO!" if turno else "ESPERA AL RIVAL", 
                                     bg="#4caf50" if turno else "#e0e0e0", fg="white" if turno else "black")
                for b in self.botones:
                    if turno: b.config(state="normal")

            elif cmd == "UPDATE":
                pos, sym = int(partes[1]), partes[2]
                color = "#f44336" if sym == "X" else "#2196f3"
                self.botones[pos].config(text=sym, bg=color, fg="white", state="disabled")
                mi_turno = (sym != self.mi_simbolo)
                self.lbl_turno.config(text="¡TU TURNO!" if mi_turno else "ESPERA AL RIVAL",
                                     bg="#4caf50" if mi_turno else "#e0e0e0", fg="white" if mi_turno else "black")
                if mi_turno:
                    for b in self.botones:
                        if b['text'] == " ": b.config(state="normal")

            elif cmd == "GAMEOVER":
                res = partes[1]
                self.lbl_turno.config(text="FIN DE PARTIDA", bg="#f0f0f0", fg="black")
                if res == "DESCONEXION":
                    messagebox.showwarning("Aviso", "El rival se ha desconectado.")
                else:
                    messagebox.showinfo("Fin", f"Resultado: {res}")
                self.btn_join.config(state="normal", text="BUSCAR PARTIDA")
                for b in self.botones: b.config(state="disabled")

        self.root.after(100, self.revisar_cola)

if __name__ == "__main__":
    ClienteGrafico().root.mainloop()