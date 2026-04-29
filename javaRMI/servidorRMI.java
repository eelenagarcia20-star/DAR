import java.io.*;
import java.net.*;
import java.util.*;

public class servidorRMI {

    static final int PORT = 55555;

    static List<ClienteInfo> colaEspera = new ArrayList<>();
    static Map<Socket, Partida> partidas = new HashMap<>();

    static final Object lock = new Object();

    static class ClienteInfo {
        Socket socket;
        String ip;

        ClienteInfo(Socket socket, String ip) {
            this.socket = socket;
            this.ip = ip;
        }
    }

    static class Partida {
        Socket[] jugadores;
        String[] tablero = new String[9];
        int turno = 0;

        Partida(Socket j1, Socket j2) {
            jugadores = new Socket[]{j1, j2};
            Arrays.fill(tablero, " ");
        }

        String hayGanador() {
            int[][] comb = {
                {0,1,2},{3,4,5},{6,7,8},
                {0,3,6},{1,4,7},{2,5,8},
                {0,4,8},{2,4,6}
            };

            for (int[] c : comb) {
                if (!tablero[c[0]].equals(" ") &&
                    tablero[c[0]].equals(tablero[c[1]]) &&
                    tablero[c[1]].equals(tablero[c[2]])) {
                    return tablero[c[0]];
                }
            }

            for (String s : tablero) {
                if (s.equals(" ")) return null;
            }

            return "EMPATE";
        }
    }

    static class ClienteHandler extends Thread {
        Socket socket;
        BufferedReader in;
        BufferedWriter out;
        String ip;

        ClienteHandler(Socket socket) throws IOException {
            this.socket = socket;
            this.ip = socket.getInetAddress().getHostAddress();
            this.in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            this.out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
        }

        void enviar(String msg) {
            try {
                out.write(msg);
                out.flush();
            } catch (IOException ignored) {}
        }

        public void run() {
            System.out.println("[CONEXIÓN] " + ip + " conectado.");

            try {
                String linea;
                while ((linea = in.readLine()) != null) {
                    String[] partes = linea.trim().split(" ");
                    if (partes.length == 0) continue;

                    String comando = partes[0].toUpperCase();

                    if (comando.equals("JOIN")) {
                        manejarJoin();
                    } else if (comando.equals("MOVE")) {
                        manejarMove(partes);
                    } else {
                        enviar("ERROR Comando desconocido\r\n");
                    }
                }
            } catch (Exception ignored) {
            } finally {
                desconectar();
            }
        }

        void manejarJoin() {
            synchronized (lock) {
                boolean encontrado = false;

                for (int i = 0; i < colaEspera.size(); i++) {
                    ClienteInfo c = colaEspera.get(i);
                    if (!c.ip.equals(ip)) {
                        colaEspera.remove(i);

                        Partida p = new Partida(c.socket, socket);
                        partidas.put(c.socket, p);
                        partidas.put(socket, p);

                        enviarA(c.socket, "START PARTIDA X\r\n");
                        enviar("START PARTIDA O\r\n");

                        encontrado = true;
                        break;
                    }
                }

                if (!encontrado) {
                    colaEspera.add(new ClienteInfo(socket, ip));
                    enviar("WAITING\r\n");
                }
            }
        }

        void manejarMove(String[] partes) {
            synchronized (lock) {
                if (!partidas.containsKey(socket)) {
                    enviar("ERROR No estas en una partida\r\n");
                    return;
                }

                try {
                    int pos = Integer.parseInt(partes[1]);
                    Partida p = partidas.get(socket);

                    int idx = (p.jugadores[0] == socket) ? 0 : 1;

                    if (p.turno != idx) {
                        enviar("ERROR No es tu turno\r\n");
                        return;
                    }

                    if (pos < 0 || pos > 8 || !p.tablero[pos].equals(" ")) {
                        enviar("ERROR Movimiento invalido\r\n");
                        return;
                    }

                    String sym = (idx == 0) ? "X" : "O";
                    p.tablero[pos] = sym;
                    p.turno = 1 - p.turno;

                    String msg = "UPDATE " + pos + " " + sym + "\r\n";
                    for (Socket j : p.jugadores) enviarA(j, msg);

                    String res = p.hayGanador();
                    if (res != null) {
                        for (Socket j : p.jugadores)
                            enviarA(j, "GAMEOVER " + res + "\r\n");

                        partidas.remove(p.jugadores[0]);
                        partidas.remove(p.jugadores[1]);
                    }

                } catch (Exception e) {
                    enviar("ERROR Formato MOVE <0-8>\r\n");
                }
            }
        }

        void desconectar() {
            synchronized (lock) {
                if (partidas.containsKey(socket)) {
                    Partida p = partidas.get(socket);

                    for (Socket j : p.jugadores) {
                        if (j != socket) {
                            enviarA(j, "GAMEOVER DESCONEXION\r\n");
                        }
                        partidas.remove(j);
                    }
                }

                colaEspera.removeIf(c -> c.socket == socket);

                try { socket.close(); } catch (IOException ignored) {}
            }
        }

        void enviarA(Socket s, String msg) {
            try {
                BufferedWriter w = new BufferedWriter(
                        new OutputStreamWriter(s.getOutputStream()));
                w.write(msg);
                w.flush();
            } catch (IOException ignored) {}
        }
    }

    public static void main(String[] args) throws Exception {
        ServerSocket server = new ServerSocket(PORT);
        System.out.println("SERVIDOR ONLINE EN PUERTO " + PORT);

        while (true) {
            Socket cliente = server.accept();
            new ClienteHandler(cliente).start();
        }
    }
}