import javax.swing.*;
import java.awt.*;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class clienteRMI {
    private interfaz stub; 
    private JFrame frame;
    private JButton[] botones = new JButton[9];
    private JLabel lblTurno;

    public clienteRMI() {
        gui();
        conectar();
    }

    private void gui() {
        frame = new JFrame("clienteRMI - Tres en Raya");
        frame.setSize(350, 450);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        lblTurno = new JLabel("Conectando...", SwingConstants.CENTER);
        frame.add(lblTurno, BorderLayout.NORTH);

        JPanel p = new JPanel(new GridLayout(3, 3));
        for (int i = 0; i < 9; i++) {
            int idx = i;
            botones[i] = new JButton(" ");
            botones[i].setFont(new Font("Arial", Font.BOLD, 40));
            botones[i].setEnabled(false);
            botones[i].addActionListener(e -> jugar(idx));
            p.add(botones[i]);
        }
        frame.add(p, BorderLayout.CENTER);

        JButton btnStart = new JButton("START");
        btnStart.addActionListener(e -> {
            try {
                dibujar(stub.iniciarJuego());
            } catch (Exception ex) { ex.printStackTrace(); }
        });
        frame.add(btnStart, BorderLayout.SOUTH);
        frame.setVisible(true);
    }

    private void conectar() {
        try {
            Registry reg = LocateRegistry.getRegistry("localhost", 55555);
            stub = (interfaz) reg.lookup("TresEnRaya");
            lblTurno.setText("Conectado.");
        } catch (Exception e) {
            lblTurno.setText("Error conexión.");
        }
    }

    private void jugar(int celda) {
        try {
            String res = stub.realizarMovimiento(celda);
            if (res.startsWith("RESULT")) {
                String[] partes = res.split("\\|");
                dibujar(partes[1]);
                JOptionPane.showMessageDialog(frame, "Resultado: " + partes[0].split(":")[1]);
            } else if (!res.equals("ERROR")) {
                dibujar(res.split(":")[1]);
            }
        } catch (Exception e) { e.printStackTrace(); }
    }

    private void dibujar(String datos) {
        String[] celdas = datos.split(",");
        for (int i = 0; i < 9; i++) {
            botones[i].setText(celdas[i].equals("_") ? "" : celdas[i]);
            botones[i].setEnabled(celdas[i].equals("_"));
            if (celdas[i].equals("X")) botones[i].setBackground(Color.CYAN);
            if (celdas[i].equals("O")) botones[i].setBackground(Color.ORANGE);
        }
    }

    public static void main(String[] args) {
        new clienteRMI();
    }
}