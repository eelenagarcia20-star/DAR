import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class clienteRMI {

    static final String HOST = "127.0.0.1";
    static final int PORT = 55555;

    JFrame frame;
    JLabel lblEstado, lblTurno;
    JButton[] botones = new JButton[9];
    JButton btnJoin;

    Socket socket;
    BufferedReader in;
    BufferedWriter out;

    BlockingQueue<String> cola = new LinkedBlockingQueue<>();
    String miSimbolo = "";

    public clienteRMI() {
        crearInterfaz();
        conectarRed();
        new Timer(100, e -> procesarCola()).start();
    }

    void crearInterfaz() {
        frame = new JFrame("DAR - Tres en Raya");
        frame.setSize(350, 550);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new FlowLayout());

        lblEstado = new JLabel("Buscando servidor...");
        frame.add(lblEstado);

        lblTurno = new JLabel("CONÉCTATE");
        lblTurno.setPreferredSize(new Dimension(300, 50));
        lblTurno.setHorizontalAlignment(SwingConstants.CENTER);
        lblTurno.setOpaque(true);
        lblTurno.setBackground(Color.LIGHT_GRAY);
        frame.add(lblTurno);

        JPanel tablero = new JPanel(new GridLayout(3, 3));
        tablero.setPreferredSize(new Dimension(300, 300));

        for (int i = 0; i < 9; i++) {
            int idx = i;
            botones[i] = new JButton(" ");
            botones[i].setFont(new Font("Arial", Font.BOLD, 24));
            botones[i].setEnabled(false);
            botones[i].addActionListener(e -> enviarMovimiento(idx));
            tablero.add(botones[i]);
        }

        frame.add(tablero);

        btnJoin = new JButton("BUSCAR PARTIDA");
        btnJoin.setEnabled(false);
        btnJoin.addActionListener(e -> solicitarJoin());
        frame.add(btnJoin);

        frame.setVisible(true);
    }

    void conectarRed() {
        new Thread(() -> {
            try {
                socket = new Socket(HOST, PORT);
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));

                SwingUtilities.invokeLater(() -> {
                    lblEstado.setText("ONLINE");
                    lblEstado.setForeground(Color.GREEN);
                    btnJoin.setEnabled(true);
                });

                new Thread(this::hiloRecibir).start();

            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    lblEstado.setText("OFFLINE");
                    lblEstado.setForeground(Color.RED);
                });
            }
        }).start();
    }

    void solicitarJoin() {
        try {
            out.write("JOIN\r\n");
            out.flush();

            btnJoin.setEnabled(false);
            btnJoin.setText("EN COLA...");
            lblTurno.setText("ESPERANDO RIVAL...");
            lblTurno.setBackground(Color.ORANGE);

            for (JButton b : botones) {
                b.setText(" ");
                b.setEnabled(false);
            }

        } catch (IOException ignored) {}
    }

    void enviarMovimiento(int i) {
        try {
            out.write("MOVE " + i + "\r\n");
            out.flush();

            lblTurno.setText("ESPERA AL RIVAL");
            lblTurno.setBackground(Color.LIGHT_GRAY);

            for (JButton b : botones) b.setEnabled(false);

        } catch (IOException ignored) {}
    }

    void hiloRecibir() {
        try {
            String linea;
            while ((linea = in.readLine()) != null) {
                cola.put(linea);
            }
        } catch (Exception ignored) {}
    }

    void procesarCola() {
        while (!cola.isEmpty()) {
            String msg = cola.poll();
            if (msg == null) return;

            String[] partes = msg.split(" ");
            String cmd = partes[0].toUpperCase();

            try {
                if (cmd.equals("START")) {
                    miSimbolo = partes[2];
                    boolean turno = miSimbolo.equals("X");

                    lblTurno.setText(turno ? "¡ES TU TURNO!" : "ESPERA AL RIVAL");
                    lblTurno.setBackground(turno ? Color.GREEN : Color.LIGHT_GRAY);

                    if (turno) {
                        for (JButton b : botones) b.setEnabled(true);
                    }
                }

                else if (cmd.equals("UPDATE")) {
                    int pos = Integer.parseInt(partes[1]);
                    String sym = partes[2];

                    botones[pos].setText(sym);
                    botones[pos].setEnabled(false);
                    botones[pos].setForeground(Color.WHITE);
                    botones[pos].setBackground(sym.equals("X") ? Color.RED : Color.BLUE);

                    boolean miTurno = !sym.equals(miSimbolo);

                    lblTurno.setText(miTurno ? "¡TU TURNO!" : "ESPERA AL RIVAL");
                    lblTurno.setBackground(miTurno ? Color.GREEN : Color.LIGHT_GRAY);

                    if (miTurno) {
                        for (JButton b : botones) {
                            if (b.getText().equals(" ")) b.setEnabled(true);
                        }
                    }
                }

                else if (cmd.equals("GAMEOVER")) {
                    String res = partes[1];

                    lblTurno.setText("FIN DE PARTIDA");
                    lblTurno.setBackground(Color.LIGHT_GRAY);

                    String mensaje;

                    if (res.equals("DESCONEXION")) {
                        mensaje = "El rival se ha desconectado.";
                    } else if (res.equals("EMPATE")) {
                        mensaje = "¡Empate!";
                    } else if (res.equals(miSimbolo)) {
                        mensaje = "¡HAS GANADO!";
                    } else {
                        mensaje = "HAS PERDIDO";
                    }

                    JOptionPane.showMessageDialog(frame, mensaje);

                    btnJoin.setEnabled(true);
                    btnJoin.setText("BUSCAR PARTIDA");

                    for (JButton b : botones) b.setEnabled(false);
                }

                else if (cmd.equals("ERROR")) {
                    JOptionPane.showMessageDialog(frame,
                            String.join(" ", partes),
                            "Error",
                            JOptionPane.ERROR_MESSAGE);
                }

            } catch (Exception ignored) {}
        }
    }

    public static void main(String[] args) {
        new clienteRMI();
    }
}