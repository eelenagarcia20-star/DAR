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

def limpiar_cliente(conn):
    global esperando
    with lock:
        if esperando == conn:
            esperando = None

        pid = jug_a_partida.get(conn)
        if pid in partidas:
            p = partidas[pid]

            for jugador in p.jugadores:
                if jugador !=conn:
                    try:
                        jugador.send("GAMEOVER DESCONECTADO\r\n".encode())
                    except:
                        pass
            for jugador in p.jugadores:
                jug_a_partida.pop(jugador, None)

            del partidas[pid]

def handle(conn, addr):                                             
    global esperando, cont                                        
    try:                                                            
        # DESACTIVA EL RETRASO DE RED (Algoritmo de Nagle)          
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  
        
        while True:                                                        
            try:
                raw = conn.recv(1024).decode()                             
                if not raw:                                                
                    limpiar_cliente(conn)
                    break

                for line in raw.split("\r\n"):                                                                                                       
                    if not line:
                        continue
                    cmd=line.split()
                    if not cmd:
                        continue                                            
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
                        if pid not in partidas:                                      
                            conn.send("ERROR sin_partida\r\n".encode())
                            continue

                        p = partidas[pid]                                 
                        idx = p.jugadores.index(conn)  

                        if idx != p.turno:                                  
                            conn.send("ERROR turno\r\n".encode())
                            continue

                        try:                                           
                            pos = int(cmd[1])                          
                            if pos < 0 or pos > 8:                      
                                raise ValueError                        
                        except(IndexError, ValueError):                             
                            conn.send("ERROR posicion\r\n".encode())    #Enviamos error al cliente 
                            continue                                    #Saltamos este mensaje y esperamos el siguiente
                        
                        sym = p.simbolos[idx]                           #Obtiene el símbolo del jugador
                        if p.mover(pos, sym):                           #Intenta realizar la jugada
                            msg = f"UPDATE {pos} {sym}\r\n"             #Mensaje de actualización
                            # Enviamos a ambos                           
                            p.jugadores[0].send(msg.encode())           #Envía actualización
                            p.jugadores[1].send(msg.encode())  
                                     
                            res = p.check_ganador()                     #Comprueba si hay ganador 
                            if res:                                     #Si hay resultado final
                                final = f"GAMEOVER {res}\r\n"           #Mensaje de fin de partida
                                p.jugadores[0].send(final.encode())     #Envía resultado al jugador 1
                                p.jugadores[1].send(final.encode())     #Envía resultado al jugador 2
                                for jugador in p.jugadores:
                                    jug_a_partida.pop(jugador,None)
                                del partidas[pid]                       #Elimina la partida
                            else:                                       
                                p.turno = 1 - p.turno                   #Cambia el turno al otro jugador
                        else:
                            conn.send("ERROR ocupada\r\n".encode())
                            continue

                    else:
                        conn.send("ERROR comando\r\n".encode())

            except Exception as e:
                print(f"ERROR en {addr}: {e}")

                if  isinstance(e,(ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
                    print(f"Cliente {addr} desconectado correctamente")
                    limpiar_cliente(conn)
                    break
                
                try:
                    conn.send("ERROR general\r\n".encode())
                except:
                    pass
                continue 

    finally: conn.close()     #Cierra la conexión del cliente

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