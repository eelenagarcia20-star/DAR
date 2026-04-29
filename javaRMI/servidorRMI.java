import java.io.*;
import java.net.*;
import java.util.*;

public class servidorRMI {
    static final int PORT = 55555;

    static class Partida {
        String[] tablero = new String[9];
        boolean juegoActivo = true;

        Partida() { Arrays.fill(tablero, " "); }

        String hayGanador() {
            int[][] combos = {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8},{0,4,8},{2,4,6}};
            for (int[] c : combos) {
                if (!tablero[c[0]].equals(" ") && tablero[c[0]].equals(tablero[c[1]]) && tablero[c[1]].equals(tablero[c[2]]))
                    return tablero[c[0]];
            }
            if (!Arrays.asList(tablero).contains(" ")) return "EMPATE";
            return null;
        }

        void movimientoIA() {
            List<Integer> libres = new ArrayList<>();
            for (int i = 0; i < 9; i++) if (tablero[i].equals(" ")) libres.add(i);
            if (!libres.isEmpty()) {
                tablero[libres.get(new Random().nextInt(libres.size()))] = "O";
            }
        }

        // CAMBIO: Usamos "_" para representar el vacío en la red
        String estado() {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 9; i++) {
                sb.append(tablero[i].equals(" ") ? "_" : tablero[i]);
                if (i < 8) sb.append(",");
            }
            return sb.toString();
        }
    }

    public static void main(String[] args) throws Exception {
        ServerSocket server = new ServerSocket(PORT);
        System.out.println("Servidor de Tres en Raya listo...");

        while (true) {
            Socket cliente = server.accept();
            new Thread(() -> manejar(cliente)).start();
        }
    }

    static void manejar(Socket socket) {
        try (
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true)
        ) {
            Partida partida = new Partida();
            String linea;

            while ((linea = in.readLine()) != null) {
                String[] p = linea.split(" ");
                if (p.length == 0) continue;
                String cmd = p[0].toUpperCase();

                if (cmd.equals("START")) {
                    partida = new Partida();
                    out.println("STATE " + partida.estado());
                } 
                else if (cmd.equals("MOVE") && partida.juegoActivo) {
                    int pos = Integer.parseInt(p[1]);
                    if (partida.tablero[pos].equals(" ")) {
                        partida.tablero[pos] = "X";
                        String res = partida.hayGanador();
                        
                        if (res == null) { // Si X no ganó, mueve la IA
                            partida.movimientoIA();
                            res = partida.hayGanador();
                        }
                        
                        out.println("STATE " + partida.estado());
                        if (res != null) {
                            out.println("RESULT " + res);
                            partida.juegoActivo = false;
                        }
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Cliente desconectado.");
        }
    }
}