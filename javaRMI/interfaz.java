import java.rmi.Remote;
import java.rmi.RemoteException;

public interface interfaz extends Remote {
    String iniciarJuego() throws RemoteException;
    String realizarMovimiento(int posicion) throws RemoteException;
}