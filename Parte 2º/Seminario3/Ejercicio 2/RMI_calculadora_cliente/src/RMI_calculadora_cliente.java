import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.util.Scanner;

public class RMI_calculadora_cliente {

    public static void main(String[] args) {

        Scanner teclado = new Scanner(System.in);

        try {
            String registroURL = "rmi://localhost:1099/calculadora";

            CalculadoraInterfaz calculadora =
                    (CalculadoraInterfaz) Naming.lookup(registroURL);

            System.out.print("Introduce el primer numero: ");
            double num1 = teclado.nextDouble();

            System.out.print("Introduce el segundo numero: ");
            double num2 = teclado.nextDouble();

            System.out.println("Suma: " + calculadora.add(num1, num2));
            System.out.println("Resta: " + calculadora.sub(num1, num2));
            System.out.println("Multiplicacion: " + calculadora.mul(num1, num2));
            System.out.println("Division: " + calculadora.div(num1, num2));
            System.out.println("Cuadrado del primer numero: " + calculadora.square(num1));

        } catch (RemoteException | MalformedURLException | NotBoundException e) {
            e.printStackTrace();
        }
    }
}