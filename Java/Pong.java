package Java;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;

/**
 * PONG — single-file Java game built with Swing.
 * Controls: Left = W/S   Right = UP/DOWN   Serve = ENTER
 *
 * File structure:
 *   1. Constants        – tweak these to change game feel
 *   2. State variables  – everything that changes at runtime
 *   3. Constructor      – one-time setup
 *   4. update()         – moves objects, checks collisions/scoring
 *   5. paintComponent() – draws the current frame
 *   6. Helpers          – launch, reset, physics utilities
 *   7. main()           – creates the window
 */
public class Pong extends JPanel implements ActionListener, KeyListener {

    // ── 1. CONSTANTS ─────────────────────────────────────────
    static final int W = 900, H = 600;
    static final int PADDLE_W = 14, PADDLE_H = 90, INSET = 30;
    static final int BALL_SIZE = 16;
    static final int PADDLE_SPEED = 6;
    static final int WIN_SCORE = 7;
    static final double INIT_SPEED = 5, SPEED_INC = 0.4, MAX_SPEED = 14;

    // ── 2. STATE ──────────────────────────────────────────────
    int lpY, rpY;                          // left/right paddle Y
    double bX, bY, bVX, bVY;              // ball position & velocity
    int lScore, rScore;
    boolean lUp, lDown, rUp, rDown;        // held keys
    String state = "waiting";             // waiting | playing | gameover
    Random rng = new Random();

    // ── 3. CONSTRUCTOR ────────────────────────────────────────
    public Pong() {
        setPreferredSize(new Dimension(W, H));
        setBackground(Color.BLACK);
        setFocusable(true);
        addKeyListener(this);
        resetPositions();
        new Timer(16, this).start();       // ~60 FPS game loop
    }

    // ── 4. UPDATE (game logic, runs every frame) ──────────────
    @Override
    public void actionPerformed(ActionEvent e) { update(); repaint(); }

    void update() {
        // Move paddles
        if (lUp   && lpY > 0)            lpY -= PADDLE_SPEED;
        if (lDown && lpY < H - PADDLE_H) lpY += PADDLE_SPEED;
        if (rUp   && rpY > 0)            rpY -= PADDLE_SPEED;
        if (rDown && rpY < H - PADDLE_H) rpY += PADDLE_SPEED;

        if (!state.equals("playing")) return;

        bX += bVX;
        bY += bVY;

        // Top / bottom wall bounce
        if (bY - BALL_SIZE / 2.0 <= 0)  { bY = BALL_SIZE / 2.0;      bVY =  Math.abs(bVY); }
        if (bY + BALL_SIZE / 2.0 >= H)  { bY = H - BALL_SIZE / 2.0;  bVY = -Math.abs(bVY); }

        // Left paddle collision
        double lFace = INSET + PADDLE_W;
        if (bVX < 0 && bX - BALL_SIZE/2.0 <= lFace && bX + BALL_SIZE/2.0 >= INSET
                && bY >= lpY && bY <= lpY + PADDLE_H) {
            bX = lFace + BALL_SIZE / 2.0;
            bVX = Math.abs(bVX);
            bVY += english(bY, lpY);
            speedUp();
        }

        // Right paddle collision
        double rFace = W - INSET - PADDLE_W;
        if (bVX > 0 && bX + BALL_SIZE/2.0 >= rFace && bX - BALL_SIZE/2.0 <= W - INSET
                && bY >= rpY && bY <= rpY + PADDLE_H) {
            bX = rFace - BALL_SIZE / 2.0;
            bVX = -Math.abs(bVX);
            bVY += english(bY, rpY);
            speedUp();
        }

        // Scoring
        if (bX + BALL_SIZE / 2.0 < 0)  { rScore++; nextPoint(); }
        if (bX - BALL_SIZE / 2.0 > W)  { lScore++; nextPoint(); }
    }

    // ── 5. RENDERING ─────────────────────────────────────────
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Center dashed line
        g2.setColor(new Color(255, 255, 255, 50));
        g2.setStroke(new BasicStroke(2, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 0, new float[]{12, 12}, 0));
        g2.drawLine(W / 2, 0, W / 2, H);
        g2.setStroke(new BasicStroke(1));

        // Scores
        g2.setColor(Color.WHITE);
        g2.setFont(new Font("Monospaced", Font.BOLD, 64));
        FontMetrics fm = g2.getFontMetrics();
        g2.drawString(String.valueOf(lScore), W/2 - fm.stringWidth(String.valueOf(lScore)) - 40, 80);
        g2.drawString(String.valueOf(rScore), W/2 + 40, 80);

        // Paddles & ball
        g2.fillRoundRect(INSET, lpY, PADDLE_W, PADDLE_H, 6, 6);
        g2.fillRoundRect(W - INSET - PADDLE_W, rpY, PADDLE_W, PADDLE_H, 6, 6);
        g2.fillOval((int)(bX - BALL_SIZE/2.0), (int)(bY - BALL_SIZE/2.0), BALL_SIZE, BALL_SIZE);

        // Overlay messages
        if (state.equals("waiting"))
            centered(g2, "Press ENTER to serve", H/2 + 30, 22, new Color(200, 200, 200));
        if (state.equals("gameover")) {
            centered(g2, (lScore >= WIN_SCORE ? "LEFT" : "RIGHT") + " PLAYER WINS!", H/2 - 20, 40, Color.YELLOW);
            centered(g2, "Press ENTER to play again", H/2 + 35, 22, new Color(200, 200, 200));
        }

        // Control hints
        g2.setColor(new Color(100, 100, 100));
        g2.setFont(new Font("Monospaced", Font.PLAIN, 13));
        g2.drawString("Left: W/S", 20, H - 12);
        String hint = "Right: \u2191/\u2193";
        g2.drawString(hint, W - g2.getFontMetrics().stringWidth(hint) - 20, H - 12);
    }

    // ── 6. HELPERS ────────────────────────────────────────────

    void launchBall() {
        double angle = Math.toRadians(rng.nextInt(41) - 20);
        int dir = rng.nextBoolean() ? 1 : -1;
        bVX = dir * INIT_SPEED * Math.cos(angle);
        bVY =       INIT_SPEED * Math.sin(angle);
    }

    void resetPositions() {
        bX = W / 2.0;  bY = H / 2.0;  bVX = 0;  bVY = 0;
        lpY = rpY = (H - PADDLE_H) / 2;
    }

    void nextPoint() {
        resetPositions();
        state = (lScore >= WIN_SCORE || rScore >= WIN_SCORE) ? "gameover" : "waiting";
    }

    // How far from center the ball hit the paddle → steeper angle at edges
    double english(double ballCY, double paddleTopY) {
        return ((ballCY - paddleTopY) / PADDLE_H - 0.5) * 4.0;
    }

    // Increase speed after each paddle hit, capped at MAX_SPEED
    void speedUp() {
        double spd = Math.sqrt(bVX*bVX + bVY*bVY);
        double scale = Math.min(spd + SPEED_INC, MAX_SPEED) / spd;
        bVX *= scale;  bVY *= scale;
    }

    void centered(Graphics2D g2, String text, int y, int size, Color c) {
        g2.setColor(c);
        g2.setFont(new Font("Monospaced", Font.BOLD, size));
        g2.drawString(text, (W - g2.getFontMetrics().stringWidth(text)) / 2, y);
    }

    // ── 7. INPUT ─────────────────────────────────────────────
    @Override
    public void keyPressed(KeyEvent e) {
        switch (e.getKeyCode()) {
            case KeyEvent.VK_W     -> lUp    = true;
            case KeyEvent.VK_S     -> lDown  = true;
            case KeyEvent.VK_UP    -> rUp    = true;
            case KeyEvent.VK_DOWN  -> rDown  = true;
            case KeyEvent.VK_ENTER -> {
                if (state.equals("waiting"))  { launchBall(); state = "playing"; }
                if (state.equals("gameover")) { lScore = 0; rScore = 0; resetPositions(); state = "waiting"; }
            }
        }
    }
    @Override
    public void keyReleased(KeyEvent e) {
        switch (e.getKeyCode()) {
            case KeyEvent.VK_W    -> lUp    = false;
            case KeyEvent.VK_S    -> lDown  = false;
            case KeyEvent.VK_UP   -> rUp    = false;
            case KeyEvent.VK_DOWN -> rDown  = false;
        }
    }
    @Override public void keyTyped(KeyEvent e) {}

    // ── 8. MAIN ───────────────────────────────────────────────
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame f = new JFrame("Pong");
            f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            f.setResizable(false);
            Pong game = new Pong();
            f.add(game);
            f.pack();
            f.setLocationRelativeTo(null);
            f.setVisible(true);
            game.requestFocusInWindow();
        });
    }
}