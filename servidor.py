import socket
import threading

HOST, PORT = '0.0.0.0', 55555
cola_espera = [] 
partidas = {} 
lock = threading.Lock()

class Partida:
    def __init__(self, jugadores):
        self.jugadores = jugadores 
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
    buffer = ""
    print(f"[CONEXIÓN] {addr[0]} conectado.")
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data: break
            buffer += data

            while "\r\n" in buffer:
                linea, buffer = buffer.split("\r\n", 1)
                partes = linea.strip().split()
                if not partes: continue
                
                comando = partes[0].upper()

                if comando == "JOIN":
                    with lock:
                        encontrado = False
                        for i, (esp_conn, esp_addr) in enumerate(cola_espera):
                            if esp_addr[0] != addr[0]:
                                rival_conn, _ = cola_espera.pop(i)
                                p = Partida([rival_conn, conn])
                                partidas[rival_conn] = partidas[conn] = p
                                rival_conn.send("START PARTIDA X\r\n".encode())
                                conn.send("START PARTIDA O\r\n".encode())
                                encontrado = True
                                break
                        if not encontrado and (conn, addr) not in cola_espera:
                            cola_espera.append((conn, addr))
                            conn.send("WAITING\r\n".encode())

                elif comando == "MOVE":
                    if conn not in partidas:
                        conn.send("ERROR No estas en una partida\r\n".encode())
                        continue
                    
                    try:
                        pos = int(partes[1])
                        p = partidas[conn]
                        idx = p.jugadores.index(conn)
                        
                        if p.turno != idx:
                            conn.send("ERROR No es tu turno\r\n".encode())
                        elif not (0 <= pos <= 8) or p.tablero[pos] != " ":
                            conn.send("ERROR Movimiento invalido\r\n".encode())
                        else:
                            sym = "X" if idx == 0 else "O"
                            p.tablero[pos] = sym
                            p.turno = 1 - p.turno
                            msg = f"UPDATE {pos} {sym}\r\n".encode()
                            for j in p.jugadores: j.send(msg)
                            
                            res = p.hay_ganador()
                            if res:
                                # Enviamos el resultado (X, O o EMPATE)
                                for j in p.jugadores: j.send(f"GAMEOVER {res}\r\n".encode())
                                # Limpieza de partida
                                p_jugadores = p.jugadores[:]
                                for j in p_jugadores:
                                    if j in partidas: del partidas[j]
                    except (ValueError, IndexError):
                        conn.send("ERROR Formato MOVE <0-8>\r\n".encode())
                else:
                    conn.send("ERROR Comando desconocido\r\n".encode())

    except Exception:
        pass
    finally:
        with lock:
            if conn in partidas:
                p = partidas[conn]
                for j in p.jugadores:
                    if j != conn:
                        try: j.send("GAMEOVER DESCONEXION\r\n".encode())
                        except: pass
                        if j in partidas: del partidas[j]
            if (conn, addr) in cola_espera: cola_espera.remove((conn, addr))
        conn.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"SERVIDOR DAR ONLINE EN PUERTO {PORT}")
    while True:
        c, a = s.accept()
        threading.Thread(target=manejar_cliente, args=(c, a), daemon=True).start()