import socket
import threading
import tkinter as tk
from tkinter import messagebox
import queue

# Configuración - Asegúrate de que coincida con el servidor
HOST, PORT = '192.168.1.1', 55555

class ClienteGrafico:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tres en Raya Online")
        self.root.geometry("350x450") # Tamaño fijo para que se vea ordenado
        
        self.cola = queue.Queue() # Nuestra "caja de correos" para los mensajes del servidor
        self.botones = []
        self.mi_simbolo = ""
        
        self.crear_interfaz()
        self.conectar_red()

    def crear_interfaz(self):
        """Crea la parte visual: Tablero, Botón y Mensajes."""
        # 1. Título y Estado
        self.lbl_estado = tk.Label(self.root, text="Conectando al servidor...", font=('Arial', 10, 'italic'), fg="gray")
        self.lbl_estado.pack(pady=10)

        # 2. El Tablero (Marco contenedor)
        self.frame_tablero = tk.Frame(self.root)
        self.frame_tablero.pack(pady=5)

        for i in range(9):
            btn = tk.Button(self.frame_tablero, text=" ", font=('Arial', 20, 'bold'), 
                            width=5, height=2, bg="#f0f0f0",
                            command=lambda i=i: self.enviar_movimiento(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            btn.config(state="disabled") # Bloqueados hasta que empiece la partida
            self.botones.append(btn)
        
        # 3. Botón de Join (Verde y llamativo)
        self.btn_join = tk.Button(self.root, text="BUSCAR PARTIDA", font=('Arial', 12, 'bold'),
                                  bg="#4caf50", fg="white", activebackground="#45a049",
                                  command=self.solicitar_join, height=2)
        self.btn_join.pack(fill="x", padx=40, pady=20)

    def conectar_red(self):
        """Inicializa la conexión y el hilo de escucha."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
            self.lbl_estado.config(text="Conectado. ¡Pulsa Buscar Partida!", fg="blue")
            
            # Lanzamos el hilo que recibe datos (corre por detrás)
            threading.Thread(target=self.hilo_recibir, daemon=True).start()
            
            # Iniciamos el vigilante de la cola (revisa la caja cada 100ms)
            self.revisar_cola_periodicamente()
        except:
            self.lbl_estado.config(text="Error: Servidor no encontrado", fg="red")
            messagebox.showerror("Error", "No se pudo conectar con el servidor.")

    def solicitar_join(self):
        """Envía el comando JOIN y actualiza la UI."""
        try:
            self.sock.send("JOIN\r\n".encode())
            self.btn_join.config(state="disabled", text="BUSCANDO RIVAL...", bg="#9e9e9e")
            self.lbl_estado.config(text="Buscando a alguien con quien jugar...", fg="orange")
        except:
            messagebox.showerror("Error", "Se perdió la conexión.")

    def enviar_movimiento(self, i):
        """Envía MOVE al servidor y bloquea botones para evitar doble clic."""
        try:
            self.sock.send(f"MOVE {i}\r\n".encode())
            self.gestionar_bloqueo_botones(False) # Bloqueamos mientras el servidor responde
        except:
            pass

    def hilo_recibir(self):
        """Este método SOLO recibe datos y los mete en la cola."""
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
        """Extrae mensajes de la cola y los procesa en el hilo principal (UI)."""
        while not self.cola.empty():
            mensaje = self.cola.get()
            self.procesar_logica_servidor(mensaje)
        # Se vuelve a llamar a sí mismo en 100 milisegundos
        self.root.after(100, self.revisar_cola_periodicamente)

    def procesar_logica_servidor(self, msg):
        """Aquí es donde ocurre la magia de la UI según el protocolo ABNF."""
        print(f"Recibido: {msg}") # Útil para depurar en consola
        partes = msg.split()
        cmd = partes[0]

        if cmd == "START":
            self.mi_simbolo = partes[2]
            self.lbl_estado.config(text=f"¡PARTIDA COMENZADA! Eres la '{self.mi_simbolo}'", fg="green")
            self.limpiar_tablero_grafico()
            # Si soy X, empiezo yo
            self.gestionar_bloqueo_botones(self.mi_simbolo == "X")

        elif cmd == "UPDATE":
            pos, sym = int(partes[1]), partes[2]
            self.dibujar_marca(pos, sym)
            # Si el último que movió NO soy yo, ahora me toca
            if sym != self.mi_simbolo:
                self.gestionar_bloqueo_botones(True)
                self.lbl_estado.config(text="¡Es tu turno!", fg="green")
            else:
                self.gestionar_bloqueo_botones(False)
                self.lbl_estado.config(text="Esperando movimiento del rival...", fg="gray")

        elif cmd == "GAMEOVER":
            res = partes[1]
            messagebox.showinfo("Fin de Partida", f"El ganador es: {res}")
            self.btn_join.config(state="normal", text="BUSCAR PARTIDA", bg="#4caf50")
            self.lbl_estado.config(text="Partida finalizada.", fg="blue")
            self.gestionar_bloqueo_botones(False)

        elif cmd == "WAITING":
            self.lbl_estado.config(text="Siguiente en la lista. Esperando rival...", fg="orange")

    def dibujar_marca(self, pos, sym):
        """Pinta la X o la O con colores."""
        color_texto = "white"
        color_fondo = "#f44336" if sym == "X" else "#2196f3" # Rojo para X, Azul para O
        self.botones[pos].config(text=sym, state="disabled", bg=color_fondo, disabledforeground=color_texto)

    def gestionar_bloqueo_botones(self, habilitar):
        """Activa o desactiva las casillas vacías."""
        for b in self.botones:
            if b['text'] == " ":
                b.config(state="normal" if habilitar else "disabled")

    def limpiar_tablero_grafico(self):
        """Reinicia los botones a su estado original."""
        for b in self.botones:
            b.config(text=" ", bg="#f0f0f0")

if __name__ == "__main__":
    ClienteGrafico().root.mainloop()