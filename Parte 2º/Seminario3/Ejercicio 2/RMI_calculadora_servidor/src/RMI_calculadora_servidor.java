import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class RMI_calculadora_servidor {

    public static void main(String[] args) {

        try {
            LocateRegistry.createRegistry(1099);
            System.out.println("Registro RMI creado en el puerto 1099");
        } catch (RemoteException ex) {
            System.out.println("Registro RMI ya creado o no creado");
        }

        try {
            CalculadoraInterfaz objExportado = new CalculadoraImplement();

            CalculadoraInterfaz stub =
                    (CalculadoraInterfaz) UnicastRemoteObject.exportObject(objExportado, 0);

            Registry registry = LocateRegistry.getRegistry();

            registry.rebind("calculadora", stub);

            System.out.println("Servidor de calculadora preparado.");

        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }
}
