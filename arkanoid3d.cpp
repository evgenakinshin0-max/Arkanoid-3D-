// arkanoid3d.cpp — Арканоид 3D на C++ (ncurses)

#include <ncurses.h>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <algorithm>
#include <thread>
#include <chrono>

using namespace std;

const int W = 10, H = 8, D = 5;
const int PADDLE_W = 5;
const char BALL = 'o', BLOCK = '#', PADDLE = '=';

struct Game {
    vector<vector<vector<int>>> blocks;
    int paddle_x, paddle_z;
    int ball_x, ball_y, ball_z;
    int ball_dx, ball_dy, ball_dz;
    int score, lives, level, high_score;
    bool game_over, paused, ball_launched;

    Game() {
        srand(time(nullptr));
        loadHighScore();
        resetGame();
    }

    void loadHighScore() { high_score = 0; }
    void saveHighScore() {}

    void resetGame() {
        blocks.assign(W, vector<vector<int>>(H, vector<int>(D, 0)));
        generateBlocks();
        paddle_x = W/2;
        paddle_z = D/2;
        ball_x = paddle_x;
        ball_y = H-2;
        ball_z = paddle_z;
        ball_dx = 1;
        ball_dy = -1;
        ball_dz = 0;
        score = 0;
        lives = 3;
        level = 1;
        game_over = false;
        paused = false;
        ball_launched = false;
    }

    void generateBlocks() {
        for (int x=0; x<W; x++)
            for (int y=0; y<H-1; y++)
                for (int z=0; z<D; z++)
                    blocks[x][y][z] = ((x+y+z)%2==0) ? (rand()%2+1) : 0;
    }

    void draw() {
        clear();
        printw("🧱 ARKANOID 3D  |  Счёт: %d  |  Уровень: %d  |  Жизни: %d  |  Рекорд: %d\n", score, level, lives, high_score);
        if (paused) printw("⏸ ПАУЗА\n");
        for (int z=D-1; z>=0; z--) {
            printw("\nСлой %d (z=%d):\n", z, z);
            printw("+");
            for (int i=0; i<W*2; i++) printw("-");
            printw("+\n");
            for (int y=0; y<H; y++) {
                printw("|");
                for (int x=0; x<W; x++) {
                    if (blocks[x][y][z] > 0) printw("%c%c", BLOCK, BLOCK);
                    else if (x==ball_x && y==ball_y && z==ball_z) printw("%c%c", BALL, BALL);
                    else printw("  ");
                }
                printw("|\n");
            }
            printw("+");
            for (int i=0; i<W*2; i++) printw("-");
            printw("+\n");
        }
        printw("\nПлатформа (вид сверху):\n");
        printw("  ");
        for (int x=0; x<W; x++) {
            if (x >= paddle_x-PADDLE_W/2 && x <= paddle_x+PADDLE_W/2 && z==paddle_z)
                printw("%c", PADDLE);
            else
                printw(" ");
        }
        printw("\nУправление: WASD - движение, Пробел - запуск/пауза, Q - выход\n");
        refresh();
    }

    void update() {
        if (game_over || paused || !ball_launched) return;
        ball_x += ball_dx;
        ball_y += ball_dy;
        ball_z += ball_dz;

        if (ball_x <= 0 || ball_x >= W-1) { ball_dx *= -1; ball_x += ball_dx*2; }
        if (ball_z <= 0 || ball_z >= D-1) { ball_dz *= -1; ball_z += ball_dz*2; }
        if (ball_y <= 0) { ball_dy *= -1; ball_y += ball_dy*2; }

        if (ball_y >= H-1) {
            if (ball_x >= paddle_x-PADDLE_W/2 && ball_x <= paddle_x+PADDLE_W/2 && ball_z == paddle_z) {
                ball_dy *= -1;
                ball_y = H-2;
                int dx = ball_x - paddle_x;
                ball_dx = (dx==0) ? 1 : dx;
                ball_dz = (rand()%3)-1;
            } else {
                lives--;
                if (lives <= 0) { game_over = true; if(score>high_score) high_score=score; }
                else resetBall();
            }
        }

        if (ball_x>=0 && ball_x<W && ball_y>=0 && ball_y<H && ball_z>=0 && ball_z<D) {
            if (blocks[ball_x][ball_y][ball_z] > 0) {
                blocks[ball_x][ball_y][ball_z]--;
                if (blocks[ball_x][ball_y][ball_z]==0) score += 10*level;
                // отражение
                if (ball_x>0 && blocks[ball_x-1][ball_y][ball_z]>0) ball_dx *= -1;
                else if (ball_x<W-1 && blocks[ball_x+1][ball_y][ball_z]>0) ball_dx *= -1;
                else if (ball_y>0 && blocks[ball_x][ball_y-1][ball_z]>0) ball_dy *= -1;
                else if (ball_y<H-1 && blocks[ball_x][ball_y+1][ball_z]>0) ball_dy *= -1;
                else if (ball_z>0 && blocks[ball_x][ball_y][ball_z-1]>0) ball_dz *= -1;
                else if (ball_z<D-1 && blocks[ball_x][ball_y][ball_z+1]>0) ball_dz *= -1;
                else ball_dy *= -1;
                ball_x += ball_dx;
                ball_y += ball_dy;
                ball_z += ball_dz;
            }
        }

        bool blocks_left = false;
        for (int x=0; x<W; x++) for (int y=0; y<H-1; y++) for (int z=0; z<D; z++)
            if (blocks[x][y][z]>0) blocks_left=true;
        if (!blocks_left) {
            level++;
            generateBlocks();
            resetBall();
        }
    }

    void resetBall() {
        ball_x = paddle_x;
        ball_y = H-2;
        ball_z = paddle_z;
        ball_dx = 1;
        ball_dy = -1;
        ball_dz = 0;
        ball_launched = false;
    }

    void launchBall() {
        if (!ball_launched) ball_launched = true;
    }

    void movePaddle(int dx, int dz) {
        int nx = paddle_x + dx, nz = paddle_z + dz;
        if (nx>=0 && nx<W && nz>=0 && nz<D) {
            paddle_x = nx;
            paddle_z = nz;
            if (!ball_launched) { ball_x = paddle_x; ball_z = paddle_z; }
        }
    }

    void run() {
        initscr();
        cbreak();
        noecho();
        keypad(stdscr, TRUE);
        nodelay(stdscr, TRUE);
        curs_set(0);

        while (!game_over) {
            draw();
            int ch = getch();
            if (ch == 'q' || ch == 'Q') break;
            if (ch == 'p' || ch == 'P') { paused = !paused; continue; }
            if (ch == ' ') {
                if (!ball_launched) launchBall();
                else paused = !paused;
                continue;
            }
            if (!paused && !game_over) {
                if (ch == 'w' || ch == 'W') movePaddle(0, -1);
                if (ch == 's' || ch == 'S') movePaddle(0, 1);
                if (ch == 'a' || ch == 'A') movePaddle(-1, 0);
                if (ch == 'd' || ch == 'D') movePaddle(1, 0);
            }
            update();
            this_thread::sleep_for(chrono::milliseconds(50));
        }
        endwin();
        cout << "ИГРА ОКОНЧЕНА! Счёт: " << score << endl;
        saveHighScore();
    }
};

int main() {
    Game game;
    game.run();
    return 0;
}
