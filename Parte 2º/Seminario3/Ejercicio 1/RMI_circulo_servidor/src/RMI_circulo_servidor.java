import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class RMI_circulo_servidor {

    @SuppressWarnings("CallToPrintStackTrace")
    public static void main(String args[]) {

        try {
            Registry registry = LocateRegistry.createRegistry(1099);
            System.out.println("Registro RMI creado en el puerto 1099");
        } catch (RemoteException ex) {
            System.out.println("Registro RMI no creado");
        }

        try {
            // se registra el objeto como stub
            CirculoInterfaz objExportado = new CirculoImplement();

            // se crea el stub dinámicamente y se asocia al puerto 0
            CirculoInterfaz stub =
                (CirculoInterfaz) UnicastRemoteObject.exportObject(objExportado, 0);

            // se registra stub en el servidor RMI
            Registry registry = LocateRegistry.getRegistry(); // puerto por defecto 1099

            // para registrarlo o sustituirlo
            registry.rebind("server", stub);

        } catch (RemoteException e) {
            e.printStackTrace();
            System.exit(0);
        }

        System.out.println("Servidor llamado *servidor_circulo* preparado.");
    }
}