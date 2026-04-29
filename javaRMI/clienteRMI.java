import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.Socket;

public class clienteRMI {
    static final String HOST = "localhost"; // Cambia a tu IP si es necesario
    static final int PORT = 55555;

    JFrame frame;
    JLabel lblEstado, lblTurno;
    JButton[] botones = new JButton[9];
    JButton btnStart;
    Socket socket;
    BufferedReader in;
    PrintWriter out;

    public clienteRMI() {
        crearInterfaz();
        conectar();
    }

    void crearInterfaz() {
        frame = new JFrame("Tres en Raya vs Servidor");
        frame.setSize(350, 500);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new FlowLayout());

        lblEstado = new JLabel("Desconectado");
        frame.add(lblEstado);

        lblTurno = new JLabel("Pulsa START para jugar");
        lblTurno.setPreferredSize(new Dimension(300, 40));
        lblTurno.setHorizontalAlignment(SwingConstants.CENTER);
        lblTurno.setOpaque(true);
        lblTurno.setBackground(Color.LIGHT_GRAY);
        frame.add(lblTurno);

        JPanel tableroPanel = new JPanel(new GridLayout(3, 3));
        tableroPanel.setPreferredSize(new Dimension(300, 300));
        for (int i = 0; i < 9; i++) {
            int idx = i;
            botones[i] = new JButton(" ");
            botones[i].setFont(new Font("Arial", Font.BOLD, 24));
            botones[i].setEnabled(false);
            botones[i].addActionListener(e -> out.println("MOVE " + idx));
            tableroPanel.add(botones[i]);
        }
        frame.add(tableroPanel);

        btnStart = new JButton("START");
        btnStart.addActionListener(e -> {
            if (out != null) {
                out.println("START");
                btnStart.setEnabled(false);
            }
        });
        frame.add(btnStart);
        frame.setVisible(true);
    }

    void conectar() {
        new Thread(() -> {
            try {
                socket = new Socket(HOST, PORT);
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                out = new PrintWriter(socket.getOutputStream(), true);

                SwingUtilities.invokeLater(() -> {
                    lblEstado.setText("CONECTADO");
                    lblEstado.setForeground(new Color(0, 150, 0));
                });

                String respuesta;
                while ((respuesta = in.readLine()) != null) {
                    final String msg = respuesta;
                    SwingUtilities.invokeLater(() -> manejarRespuesta(msg));
                }
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    lblEstado.setText("ERROR DE CONEXIÓN");
                    lblEstado.setForeground(Color.RED);
                });
            }
        }).start();
    }

    void manejarRespuesta(String msg) {
        String[] partes = msg.split(" ");
        if (partes.length < 2) return;
        String cmd = partes[0];

        if (cmd.equals("STATE")) {
            String[] valores = partes[1].split(",");
            for (int i = 0; i < 9; i++) {
                // CAMBIO: Convertimos el "_" de la red en " " para el botón
                String texto = valores[i].equals("_") ? " " : valores[i];
                botones[i].setText(texto);
                botones[i].setEnabled(texto.equals(" "));
                
                if(texto.equals("X")) {
                    botones[i].setBackground(Color.CYAN);
                } else if(texto.equals("O")) {
                    botones[i].setBackground(Color.ORANGE);
                } else {
                    botones[i].setBackground(null);
                }
            }
            lblTurno.setText("Tu turno (X)");
        } 
        else if (cmd.equals("RESULT")) {
            String res = partes[1];
            String mensaje = res.equals("X") ? "¡GANASTE!" : res.equals("O") ? "PERDISTE" : "EMPATE";
            JOptionPane.showMessageDialog(frame, mensaje);
            btnStart.setEnabled(true);
            for (JButton b : botones) b.setEnabled(false);
        }
    }

    public static void main(String[] args) {
        new clienteRMI();
    }
}