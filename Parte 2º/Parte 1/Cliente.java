import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Cliente {
    public static void main(String[] args) {
        String host = "localhost";
        int puerto = 5000;
        Scanner sc = new Scanner(System.in);

        try (Socket socket = new Socket(host, puerto);
             DataOutputStream salida = new DataOutputStream(socket.getOutputStream());
             DataInputStream entrada = new DataInputStream(socket.getInputStream())) {

            System.out.print("Introduce una frase en minúsculas: ");
            String fraseEnviada = sc.nextLine().toLowerCase();

            // Enviar la frase al servidor
            salida.writeUTF(fraseEnviada);

            // Leer la respuesta binaria
            String respuesta = entrada.readUTF();
            System.out.println("Respuesta del servidor: " + respuesta);

        } catch (IOException e) {
            System.err.println("Error en el cliente: " + e.getMessage());
        }
    }
}