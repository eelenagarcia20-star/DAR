import socket
import threading

HOST = '0.0.0.0'
PORT = 55555

cola_espera = [] # Lista de (conn, addr)
partidas = {}             
lock = threading.Lock()

class Partida:
    def __init__(self, jugadores):
        self.jugadores = jugadores # [conn_x, conn_o]
        self.tablero = [" "] * 9
        self.turno = 0 

    def hay_ganador(self):
        v = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in v:
            if self.tablero[a] == self.tablero[b] == self.tablero[c] != " ":
                return self.tablero[a]
        return "EMPATE" if " " not in self.tablero else None

def manejar_cliente(conn, addr):
    global cola_espera
    ip_actual = addr[0]
    print(f"[CONEXIÓN] {ip_actual} conectado.")
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data: break

            for linea in data.split("\r\n"):
                comando = linea.strip().split()
                if not comando: continue
                
                if comando[0].upper() == "JOIN":
                    with lock:
                        encontrado = False
                        for i, (esperando_conn, esperando_addr) in enumerate(cola_espera):
                            if esperando_addr[0] != ip_actual:
                                rival_conn, rival_addr = cola_espera.pop(i)
                                p = Partida([rival_conn, conn])
                                partidas[rival_conn] = p
                                partidas[conn] = p
                                rival_conn.send("START PARTIDA X\r\n".encode())
                                conn.send("START PARTIDA O\r\n".encode())
                                encontrado = True
                                break
                        if not encontrado:
                            if (conn, addr) not in cola_espera:
                                cola_espera.append((conn, addr))
                            conn.send("WAITING\r\n".encode())

                elif comando[0].upper() == "MOVE":
                    if conn in partidas:
                        p = partidas[conn]
                        idx = p.jugadores.index(conn)
                        if p.turno == idx:
                            pos = int(comando[1])
                            if p.tablero[pos] == " ":
                                sym = "X" if idx == 0 else "O"
                                p.tablero[pos] = sym
                                p.turno = 1 - p.turno
                                for j in p.jugadores: j.send(f"UPDATE {pos} {sym}\r\n".encode())
                                res = p.hay_ganador()
                                if res:
                                    for j in p.jugadores: j.send(f"GAMEOVER {res}\r\n".encode())
                                    del partidas[p.jugadores[0]]
                                    del partidas[p.jugadores[1]]

    except:
        pass
    finally:
        with lock:
            # GESTIÓN DE DESCONEXIÓN
            if conn in partidas:
                p = partidas[conn]
                for j in p.jugadores:
                    if j != conn:
                        try: j.send("GAMEOVER DESCONEXION\r\n".encode())
                        except: pass
                        if j in partidas: del partidas[j]
            if (conn, addr) in cola_espera:
                cola_espera.remove((conn, addr))
        conn.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("SERVIDOR ONLINE")
    while True:
        c, a = s.accept()
        threading.Thread(target=manejar_cliente, args=(c, a), daemon=True).start()