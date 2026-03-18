import socket
import threading

class Partida:
    def __init__(self, s1, s2):
        self.jugadores = [s1, s2]
        self.tablero = [" "] * 9
        self.simbolos = ["X", "O"]
        self.turno = 0

    def mover(self, pos, sym):
        if self.tablero[pos] == " ":
            self.tablero[pos] = sym
            return True
        return False

    def check_ganador(self):
        v = self.tablero
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a,b,c in wins:
            if v[a] == v[b] == v[c] != " ": return v[a]
        return "EMPATE" if " " not in v else None

# USAMOS UN PUERTO DIFERENTE PARA EVITAR EL ERROR 10013
HOST, PORT = '127.0.0.1', 55555 
partidas, jug_a_partida = {}, {}
esperando, lock = None, threading.Lock()
cont = 0

def handle(conn, addr):
    global esperando, cont
    try:
        # DESACTIVA EL RETRASO DE RED (Algoritmo de Nagle)
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        while True:
            raw = conn.recv(1024).decode()
            if not raw: break
            for line in raw.split("\r\n"):
                if not line: continue
                cmd = line.split()
                if cmd[0] == "JOIN":
                    with lock:
                        if esperando is None:
                            esperando = conn
                            conn.send("WAITING\r\n".encode())
                        else:
                            p1, p2 = esperando, conn
                            esperando = None
                            cont += 1
                            partidas[cont] = Partida(p1, p2)
                            jug_a_partida[p1] = jug_a_partida[p2] = cont
                            p1.send(f"START {cont} X\r\n".encode())
                            p2.send(f"START {cont} O\r\n".encode())
                
                elif cmd[0] == "MOVE":
                    pid = jug_a_partida.get(conn)
                    if pid in partidas:
                        p = partidas[pid]
                        idx = p.jugadores.index(conn)
                        if idx == p.turno:
                            pos = int(cmd[1])
                            sym = p.simbolos[idx]
                            if p.mover(pos, sym):
                                msg = f"UPDATE {pos} {sym}\r\n"
                                # Enviamos a ambos
                                p.jugadores[0].send(msg.encode())
                                p.jugadores[1].send(msg.encode())
                                res = p.check_ganador()
                                if res:
                                    final = f"GAMEOVER {res}\r\n"
                                    p.jugadores[0].send(final.encode())
                                    p.jugadores[1].send(final.encode())
                                    del partidas[pid]
                                else:
                                    p.turno = 1 - p.turno
    except: pass
    finally: conn.close()

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor listo en el puerto {PORT}...")
except Exception as e:
    print(f"ERROR AL INICIAR: {e}")

while True:
    c, a = s.accept()
    threading.Thread(target=handle, args=(c,a), daemon=True).start()