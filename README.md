PROYECTO JUEGO TRES EN RAYA ONLINE  
Este proyecto consiste en una aplicación distribuida bajo el modelo cliente-servidor que permite jugar al Tres en Raya en tiempo real a través de una red local o internet. Está desarrollado íntegramente en Python, utilizando la librería nativa de sockets para la comunicación y Tkinter para la interfaz gráfica.

1. ARQUITECTURA GENERAL DEL PROTOCOLO:
La arquitectura se basa en un modelo Cliente-Servidor Centralizado con soporte multihilo. El Servidor actúa como el nodo maestro que gestiona la lógica del juego, el estado del tablero y la sincronización entre los dos jugadores. Cada conexión de un cliente es gestionada por un hilo independiente (thread), lo que permite que el servidor atienda a múltiples parejas de forma simultánea. Se utiliza un mecanismo de exclusión mutua (Lock) para garantizar que la gestión de la cola de espera y el emparejamiento de jugadores sea segura y no presente condiciones de carrera. Por su parte, el Cliente implementa una arquitectura de separación de procesos: un hilo principal se encarga de mantener la interfaz gráfica (GUI) activa y receptiva, mientras que un hilo secundario permanece en escucha constante del socket para recibir actualizaciones del servidor sin bloquear la ventana del usuario.

2. DESCRIPCIÓN DEL PROTOCOLO IMPLEMENTADO:
El protocolo de comunicación es de nivel de aplicación, orientado a texto y basado en mensajes delimitados por el carácter de fin de línea (\r\n). Este diseño asegura que, a pesar de la naturaleza de flujo continuo de TCP, los mensajes se procesen de forma íntegra y ordenada.
El flujo comienza con el comando JOIN enviado por el cliente. El servidor responde con WAITING si el jugador debe esperar o con START PARTIDA (seguido del símbolo X u O) una vez que se encuentra un rival. Durante la partida, el cliente envía el comando MOVE seguido del índice de la casilla (0-8). El servidor valida este movimiento y, si es correcto, emite un mensaje UPDATE a ambos participantes para actualizar sus tableros sincronizadamente. Finalmente, el servidor determina el cierre de la sesión mediante el comando GAMEOVER, especificando el ganador, el empate o si hubo una desconexión abrupta de alguno de los nodos.

3. REQUISITOS DE EJECUCIÓN:
Para la correcta ejecución del sistema, es necesario contar con Python 3.6 o superior instalado en el sistema. No se requieren librerías externas de terceros, ya que el proyecto utiliza exclusivamente módulos de la biblioteca estándar de Python: socket (red), threading (concurrencia), tkinter (interfaz) y queue (gestión de mensajes internos).
En entornos Linux, es posible que se deba instalar el paquete de soporte para la interfaz gráfica mediante el comando: sudo apt-get install python3-tk. En Windows y macOS, este módulo suele estar incluido en la instalación estándar de Python.

4. INSTRUCCIONES DE LANZAMIENTO:
Para poner en marcha el sistema, se deben seguir estos pasos en orden:
Primero, iniciar el servidor ejecutando el script correspondiente en la terminal: "python servidor.py". El servidor mostrará un mensaje confirmando que está en escucha en el puerto 55555.
Segundo, iniciar los clientes. Se deben abrir dos instancias del script "python cliente.py" (preferiblemente en terminales o equipos distintos). Por defecto, el cliente está configurado para conectar a la dirección local (127.0.0.1). Si se desea jugar entre ordenadores diferentes de una misma red, se debe editar la variable HOST en el archivo del cliente, sustituyéndola por la dirección IP privada del equipo que ejecuta el servidor.

5. EJEMPLOS DE USO:
Una vez conectados, ambos usuarios verán el estado "ONLINE" en color verde. El primer paso es pulsar el botón "BUSCAR PARTIDA"; el sistema colocará al primer usuario en espera y, al conectar el segundo, la partida comenzará automáticamente asignando las "X" al primer jugador.
El jugador con el turno activo verá sus botones habilitados. Al marcar una casilla, el servidor procesará el movimiento y habilitará el turno al oponente de forma instantánea. Si un jugador intenta cerrar la ventana o pierde la conexión a internet, el servidor detectará la ruptura del socket y notificará al jugador restante la victoria por abandono mediante un cuadro de diálogo informativo, devolviendo el cliente al estado de menú principal para iniciar una nueva búsqueda.
