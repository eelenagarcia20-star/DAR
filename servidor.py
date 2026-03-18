import socket    
import threading                   #Para trabajar con varios clientes

class Partida:                     #Define la clase
    def __init__(self, s1, s2):    #Constructor que recibe los dos jugadores
        self.jugadores = [s1, s2]  #Guarda los dos jugadores en una lista
        self.tablero = [" "] * 9   #Inicializa el tablero con 9 casillas vacías
        self.simbolos = ["X", "O"] #Asigna los símbolos a los jugadores  
        self.turno = 0             #Indica que empieza el jugador 0

    def mover(self, pos, sym):           #Método para realizar una jugada
        if self.tablero[pos] == " ":     #Comprueba si la casilla está vacía
            self.tablero[pos] = sym      #Coloca el símbolo en la posición indicada 
            return True                  #Indica que la jugada es válida 
        return False                     #Indica que la jugada no es válida

    def check_ganador(self):                                                        #Método para comporobar si hay un ganador o empate
        v = self.tablero                                                            #Guarda el tablero en una variable auxiliar
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]    #Todas las combinaciones ganadores
        for a,b,c in wins:                                                          #Recorre cada combinación ganadora
            if v[a] == v[b] == v[c] != " ": return v[a]                             #Si hay 3 iguales, devuelve el ganador
        return "EMPATE" if " " not in v else None                                   #Devuelve emate si no hay hueccos o None si sigue 

# USAMOS UN PUERTO DIFERENTE PARA EVITAR EL ERROR 10013
HOST, PORT = '127.0.0.1', 55555           #Defina la IP y puerto del servidor
partidas, jug_a_partida = {}, {}          #Diccionarios para guardar partidas y relación jugador-partida
esperando, lock = None, threading.Lock()  #Variable para jugador en espera y bloqueo para concurrencia 
cont = 0                                  #Contador de partidas 

def handle(conn, addr):                                             #Función que gestiona la conexión con un cliente 
    global esperando, cont                                          #Indica que se usarán variables globales
    try:                                                            #Inicio del bloque de control de errores
        # DESACTIVA EL RETRASO DE RED (Algoritmo de Nagle)          
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  
        
        while True:                                                       #Bucle para recibir mensajes continuamente
            raw = conn.recv(1024).decode()                                #Recibe datos del cliente y los convierte a texto
            if not raw: break                                             #Si no hay datos, se cierra la conexión 
            for line in raw.split("\r\n"):                                #Divide los mensajes por líneas
                if not line: continue                                     #Ignora líneas vacías
                cmd = line.split()                                        #Divide el mensaje en partes
                if cmd[0] == "JOIN":                                      #Si el cliente quiere unirse a una partida
                    with lock:                                            #Bloquea acceso para evitar conflictos entre hilos
                        if esperando is None:                             #Si no hay nadie esperando 
                            esperando = conn                              #Guarda este cliente como esperando 
                            conn.send("WAITING\r\n".encode())             #Le indica que espere
                        else:                                             #Si ya hay alguien esperando
                            p1, p2 = esperando, conn                      #Asigna los dos jugadores 
                            esperando = None                              #Vacía la espera
                            cont += 1                                     #Incrementa el ID de partida
                            partidas[cont] = Partida(p1, p2)              #Crea una nueva partida
                            jug_a_partida[p1] = jug_a_partida[p2] = cont  #Asocia jugadores a la partida
                            p1.send(f"START {cont} X\r\n".encode())       #Envía inicia al jugador 1
                            p2.send(f"START {cont} O\r\n".encode())       #Envía inicio al jugador 2
                
                elif cmd[0] == "MOVE":                                      #Si el cliente envía una jugada 
                    pid = jug_a_partida.get(conn)                           #Obtiene la partida del jugador 
                    if pid in partidas:                                     #Comprueba que la partida existe 
                        p = partidas[pid]                                   #Obtiene la partida 
                        idx = p.jugadores.index(conn)                       #Obtiene el índice del juagdor (0 o 1)
                        if idx == p.turno:                                  #Comprueba si es su turno 
                            pos = int(cmd[1])                               #Obtiene la posición a jugar
                            sym = p.simbolos[idx]                           #Obtiene el símbolo del jugador
                            if p.mover(pos, sym):                           #Intenta realizar la jugada
                                msg = f"UPDATE {pos} {sym}\r\n"             #Mensaje de actualización
                                # Enviamos a ambos                           
                                p.jugadores[0].send(msg.encode())           #Envía actualización
                                p.jugadores[1].send(msg.encode())           #Envía actualización
                                res = p.check_ganador()                     #Comprueba si hay ganador 
                                if res:                                     #Si hay resultado final
                                    final = f"GAMEOVER {res}\r\n"           #Mensaje de fin de partida
                                    p.jugadores[0].send(final.encode())     #Envía resultado al jugador 1
                                    p.jugadores[1].send(final.encode())     #Envía resultado al jugador 2
                                    del partidas[pid]                       #Elimina la partida
                                else:                                       
                                    p.turno = 1 - p.turno                   #Cambia el turno al otro jugador
    except: pass
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