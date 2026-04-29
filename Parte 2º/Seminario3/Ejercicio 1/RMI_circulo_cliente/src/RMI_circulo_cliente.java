import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.util.Scanner;

public class RMI_circulo_cliente {

    @SuppressWarnings("CallToPrintStackTrace")
    public static void main(String[] args) {

        Scanner lecturaTeclado = new Scanner(System.in);
        System.out.print("Introduzca el radio del circulo: ");
        double radio = lecturaTeclado.nextDouble();

        try {
            String registroURL = "rmi://localhost:1099/server";

            CirculoInterfaz circulo =
                (CirculoInterfaz) Naming.lookup(registroURL);

            // invocar ahora los métodos remotos
            circulo.setRadio(radio);
            double area = circulo.getArea();

            System.out.println("El area es: " + area);

        } catch (RemoteException | MalformedURLException | NotBoundException e) {
            e.printStackTrace();
        }
    }
}
