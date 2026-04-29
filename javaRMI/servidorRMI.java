import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.*;

public class servidorRMI extends UnicastRemoteObject implements interfaz {
    private String[] tablero = new String[9];
    private boolean juegoActivo = false;

    protected servidorRMI() throws RemoteException {
        super();
        Arrays.fill(tablero, "_");
    }

    @Override
    public synchronized String iniciarJuego() throws RemoteException {
        Arrays.fill(tablero, "_");
        juegoActivo = true;
        System.out.println("Partida iniciada.");
        return String.join(",", tablero);
    }

    @Override
    public synchronized String realizarMovimiento(int pos) throws RemoteException {
        if (!juegoActivo || !tablero[pos].equals("_")) return "ERROR";

        tablero[pos] = "X"; // Jugador
        
        String res = comprobarEstado();
        if (res == null) {
            movimientoIA();
            res = comprobarEstado();
        }

        String estadoStr = String.join(",", tablero);
        if (res != null) {
            juegoActivo = false;
            return "RESULT:" + res + "|" + estadoStr;
        }
        return "STATE:" + estadoStr;
    }

    private void movimientoIA() {
        List<Integer> libres = new ArrayList<>();
        for (int i = 0; i < 9; i++) if (tablero[i].equals("_")) libres.add(i);
        if (!libres.isEmpty()) {
            tablero[libres.get(new Random().nextInt(libres.size()))] = "O";
        }
    }

    private String comprobarEstado() {
        int[][] combos = {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8},{0,4,8},{2,4,6}};
        for (int[] c : combos) {
            if (!tablero[c[0]].equals("_") && tablero[c[0]].equals(tablero[c[1]]) && tablero[c[1]].equals(tablero[c[2]]))
                return tablero[c[0]];
        }
        if (!Arrays.asList(tablero).contains("_")) return "EMPATE";
        return null;
    }

    public static void main(String[] args) {
        try {
            // System.setProperty("java.rmi.server.hostname", "172.17.97.155");
            servidorRMI obj = new servidorRMI();
            Registry registry = LocateRegistry.createRegistry(55555);
            registry.rebind("TresEnRaya", obj);
            System.out.println("servidorRMI listo.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}