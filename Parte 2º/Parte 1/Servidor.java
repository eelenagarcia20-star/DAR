import java.io.*;
import java.net.*;

public class Servidor{
    public static void main(String[] args) {
        int puerto = 5000;

        try (ServerSocket serverSocket = new ServerSocket(puerto)) {
            System.out.println("Servidor iniciado en el puerto " + puerto);

            while (true) {
                try (Socket socket = serverSocket.accept();
                     DataInputStream entrada = new DataInputStream(socket.getInputStream());
                     DataOutputStream salida = new DataOutputStream(socket.getOutputStream())) {

                    // Leer la frase enviada por el cliente
                    String fraseOriginal = entrada.readUTF();
                    System.out.println("Recibido: " + fraseOriginal);

                    // Procesar la frase (Sustitución de vocales)
                    String fraseProcesada = transformarVocales(fraseOriginal);

                    // Enviar la respuesta binaria
                    salida.writeUTF(fraseProcesada);
                    System.out.println("Enviado: " + fraseProcesada);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static String transformarVocales(String texto) {
        return texto.replace('a', '1')
                    .replace('e', '2')
                    .replace('i', '3')
                    .replace('o', '4')
                    .replace('u', '5');
    }
}