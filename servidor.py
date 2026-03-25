import socket
import threading

# Configuración para VirtualBox (Red Interna)
HOST = '0.0.0.0'  # Escucha en todas las interfaces de la VM
PORT = 55555

class Partida:
    def __init__(self, jugadores):
        self.jugadores = jugadores  # [conn_x, conn_o]
        self.tablero = [" "] * 9
        self.turno = 0  # 0 para X, 1 para O

    def hay_ganador(self):
        v_ganadoras = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in v_ganadoras:
            if self.tablero[a] == self.tablero[b] == self.tablero[c] != " ":
                return self.tablero[a]
        if " " not in self.tablero:
            return "EMPATE"
        return None

# Globales para gestionar el estado
esperando_jugador = None
partidas = {}  # {socket_cliente: Partida}
lock = threading.Lock()

def manejar_cliente(conn, addr):
    global esperando_jugador
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data: break

            for linea in data.split("\r\n"):
                comando = linea.strip().split()
                if not comando: continue

                cmd = comando[0].upper()

                # --- LÓGICA DE UNIRSE ---
                if cmd == "JOIN":
                    with lock:
                        if esperando_jugador is None:
                            esperando_jugador = conn
                            conn.send("WAITING\r\n".encode())
                        else:
                            # Creamos la partida con el que esperaba y el nuevo
                            rival = esperando_jugador
                            nueva_partida = Partida([rival, conn])
                            partidas[rival] = nueva_partida
                            partidas[conn] = nueva_partida
                            esperando_jugador = None
                            
                            # Notificamos inicio: Rival es X, el actual es O
                            rival.send("START PARTIDA X\r\n".encode())
                            conn.send("START PARTIDA O\r\n".encode())
                            print(f"[PARTIDA] Iniciada entre {rival.getpeername()} y {addr}")

                # --- LÓGICA DE MOVIMIENTO ---
                elif cmd == "MOVE":
                    if conn not in partidas:
                        conn.send("ERROR No estás en una partida\r\n".encode())
                        continue
                    
                    p = partidas[conn]
                    idx_jugador = p.jugadores.index(conn)
                    
                    if p.turno != idx_jugador:
                        conn.send("ERROR No es tu turno\r\n".encode())
                        continue

                    pos = int(comando[1])
                    if p.tablero[pos] == " ":
                        simbolo = "X" if idx_jugador == 0 else "O"
                        p.tablero[pos] = simbolo
                        
                        # Notificar UPDATE a ambos
                        msg_update = f"UPDATE {pos} {simbolo}\r\n"
                        for j in p.jugadores:
                            j.send(msg_update.encode())
                        
                        # Verificar si terminó
                        resultado = p.hay_ganador()
                        if resultado:
                            final = f"GAMEOVER {resultado}\r\n"
                            for j in p.jugadores:
                                j.send(final.encode())
                                if j in partidas: del partidas[j]
                        else:
                            p.turno = 1 - p.turno # Cambio de turno
                    else:
                        conn.send("ERROR Casilla ocupada\r\n".encode())

    except Exception as e:
        print(f"[ERROR] Con {addr}: {e}")
    finally:
        with lock:
            if esperando_jugador == conn: esperando_jugador = None
            if conn in partidas:
                # Si uno se desconecta, avisar al otro y cerrar partida
                p = partidas[conn]
                for j in p.jugadores:
                    if j != conn:
                        try: j.send("GAMEOVER DESCONEXIÓN\r\n".encode())
                        except: pass
                        if j in partidas: del partidas[j]
                del partidas[conn]
        conn.close()
        print(f"[DESCONEXIÓN] {addr} se ha ido.")

def iniciar_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTO] Servidor escuchando en {HOST}:{PORT}")
    except Exception as e:
        print(f"[ERROR BIND] {e}")
        return

    while True:
        conn, addr = s.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()