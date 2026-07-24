// Arkanoid3D.java — Арканоид 3D на Java (Swing)

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;

public class Arkanoid3D extends JPanel implements ActionListener, KeyListener {
    private static final int W = 10, H = 8, D = 5;
    private static final int PADDLE_W = 5;
    private static final int CELL = 25;
    private int[][][] blocks;
    private int paddleX, paddleZ;
    private int ballX, ballY, ballZ;
    private int ballDX, ballDY, ballDZ;
    private int score, lives, level, highScore;
    private boolean gameOver, paused, ballLaunched;
    private Timer timer;
    private Random rand = new Random();

    public Arkanoid3D() {
        setPreferredSize(new Dimension(W*CELL, (H+D)*CELL));
        setBackground(Color.BLACK);
        setFocusable(true);
        addKeyListener(this);
        loadHighScore();
        resetGame();
        timer = new Timer(50, this);
        timer.start();
    }

    private void loadHighScore() { highScore = 0; }
    private void saveHighScore() {}

    private void resetGame() {
        blocks = new int[W][H][D];
        generateBlocks();
        paddleX = W/2;
        paddleZ = D/2;
        ballX = paddleX;
        ballY = H-2;
        ballZ = paddleZ;
        ballDX = 1;
        ballDY = -1;
        ballDZ = 0;
        score = 0;
        lives = 3;
        level = 1;
        gameOver = false;
        paused = false;
        ballLaunched = false;
    }

    private void generateBlocks() {
        for (int x=0; x<W; x++) for (int y=0; y<H-1; y++) for (int z=0; z<D; z++)
            blocks[x][y][z] = ((x+y+z)%2==0) ? rand.nextInt(2)+1 : 0;
    }

    private void resetBall() {
        ballX = paddleX;
        ballY = H-2;
        ballZ = paddleZ;
        ballDX = 1;
        ballDY = -1;
        ballDZ = 0;
        ballLaunched = false;
    }

    private void launchBall() {
        if (!ballLaunched) ballLaunched = true;
    }

    private void movePaddle(int dx, int dz) {
        int nx = paddleX+dx, nz = paddleZ+dz;
        if (nx>=0 && nx<W && nz>=0 && nz<D) {
            paddleX = nx;
            paddleZ = nz;
            if (!ballLaunched) { ballX = paddleX; ballZ = paddleZ; }
        }
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if (gameOver || paused || !ballLaunched) return;
        ballX += ballDX;
        ballY += ballDY;
        ballZ += ballDZ;

        if (ballX<=0 || ballX>=W-1) { ballDX *= -1; ballX += ballDX*2; }
        if (ballZ<=0 || ballZ>=D-1) { ballDZ *= -1; ballZ += ballDZ*2; }
        if (ballY<=0) { ballDY *= -1; ballY += ballDY*2; }

        if (ballY>=H-1) {
            if (ballX>=paddleX-PADDLE_W/2 && ballX<=paddleX+PADDLE_W/2 && ballZ==paddleZ) {
                ballDY *= -1;
                ballY = H-2;
                int dx = ballX - paddleX;
                ballDX = (dx==0) ? 1 : dx;
                ballDZ = rand.nextInt(3)-1;
            } else {
                lives--;
                if (lives<=0) { gameOver=true; if(score>highScore) highScore=score; }
                else resetBall();
            }
        }

        if (ballX>=0 && ballX<W && ballY>=0 && ballY<H && ballZ>=0 && ballZ<D) {
            if (blocks[ballX][ballY][ballZ] > 0) {
                blocks[ballX][ballY][ballZ]--;
                if (blocks[ballX][ballY][ballZ]==0) score += 10*level;
                // отражение
                if (ballX>0 && blocks[ballX-1][ballY][ballZ]>0) ballDX *= -1;
                else if (ballX<W-1 && blocks[ballX+1][ballY][ballZ]>0) ballDX *= -1;
                else if (ballY>0 && blocks[ballX][ballY-1][ballZ]>0) ballDY *= -1;
                else if (ballY<H-1 && blocks[ballX][ballY+1][ballZ]>0) ballDY *= -1;
                else if (ballZ>0 && blocks[ballX][ballY][ballZ-1]>0) ballDZ *= -1;
                else if (ballZ<D-1 && blocks[ballX][ballY][ballZ+1]>0) ballDZ *= -1;
                else ballDY *= -1;
                ballX += ballDX;
                ballY += ballDY;
                ballZ += ballDZ;
            }
        }

        boolean blocksLeft = false;
        for (int x=0; x<W; x++) for (int y=0; y<H-1; y++) for (int z=0; z<D; z++)
            if (blocks[x][y][z]>0) blocksLeft=true;
        if (!blocksLeft) {
            level++;
            generateBlocks();
            resetBall();
        }
        repaint();
    }

    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        // отрисовка слоёв
        int offsetY = 20;
        for (int z=D-1; z>=0; z--) {
            int yOff = offsetY + (D-1-z) * 20;
            g2.setColor(Color.WHITE);
            g2.drawString("Слой " + z, 10, yOff);
            for (int y=0; y<H; y++) {
                for (int x=0; x<W; x++) {
                    int xPos = 50 + x*CELL;
                    int yPos = yOff + 20 + y*CELL;
                    Color col = Color.DARK_GRAY;
                    if (blocks[x][y][z] > 0) col = new Color(blocks[x][y][z]*100, 0, 0);
                    else if (x==ballX && y==ballY && z==ballZ) col = Color.YELLOW;
                    else col = Color.BLACK;
                    g2.setColor(col);
                    g2.fillRect(xPos, yPos, CELL, CELL);
                    if (blocks[x][y][z] > 0) {
                        g2.setColor(Color.WHITE);
                        g2.drawRect(xPos, yPos, CELL, CELL);
                    }
                }
            }
        }
        // платформа
        g2.setColor(Color.GREEN);
        int px = 50 + paddleX*CELL - PADDLE_W*CELL/2;
        int pzOff = 20 + (D-1-paddleZ)*20 + 20 + (H-1)*CELL + 10;
        g2.fillRect(px, pzOff, PADDLE_W*CELL, 10);
        // информация
        g2.setColor(Color.WHITE);
        g2.drawString("Счёт: "+score+"  Уровень: "+level+"  Жизни: "+lives+"  Рекорд: "+highScore, 10, 20);
        if (paused) g2.drawString("ПАУЗА", W*CELL/2, H*CELL/2);
        if (gameOver) g2.drawString("ИГРА ОКОНЧЕНА! R для рестарта", 50, H*CELL/2);
    }

    @Override
    public void keyPressed(KeyEvent e) {
        int key = e.getKeyCode();
        if (key == KeyEvent.VK_R && gameOver) { resetGame(); return; }
        if (key == KeyEvent.VK_ESCAPE) System.exit(0);
        if (key == KeyEvent.VK_P) { paused = !paused; return; }
        if (paused) return;
        if (key == KeyEvent.VK_W) movePaddle(0, -1);
        else if (key == KeyEvent.VK_S) movePaddle(0, 1);
        else if (key == KeyEvent.VK_A) movePaddle(-1, 0);
        else if (key == KeyEvent.VK_D) movePaddle(1, 0);
        else if (key == KeyEvent.VK_SPACE) {
            if (!ballLaunched) launchBall();
            else paused = !paused;
        }
    }
    @Override public void keyReleased(KeyEvent e) {}
    @Override public void keyTyped(KeyEvent e) {}

    public static void main(String[] args) {
        JFrame frame = new JFrame("🧱 Arkanoid 3D");
        Arkanoid3D game = new Arkanoid3D();
        frame.add(game);
        frame.pack();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
        frame.setLocationRelativeTo(null);
    }
}
