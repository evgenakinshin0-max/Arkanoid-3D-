// Arkanoid3D.cs — Арканоид 3D на C#

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

class Arkanoid3D
{
    const int W = 10, H = 8, D = 5;
    const int PADDLE_W = 5;
    const char BALL = 'o', BLOCK = '#', PADDLE = '=';

    static int[,,] blocks;
    static int paddleX, paddleZ;
    static int ballX, ballY, ballZ;
    static int ballDX, ballDY, ballDZ;
    static int score, lives, level, highScore;
    static bool gameOver, paused, ballLaunched;
    static Random rand = new Random();
    static DateTime lastUpdate = DateTime.Now;
    static bool quit = false;

    static void LoadHighScore() { highScore = 0; }
    static void SaveHighScore() {}

    static void GenerateBlocks()
    {
        blocks = new int[W, H, D];
        for (int x=0; x<W; x++) for (int y=0; y<H-1; y++) for (int z=0; z<D; z++)
            blocks[x,y,z] = ((x+y+z)%2==0) ? rand.Next(1,3) : 0;
    }

    static void ResetBall()
    {
        ballX = paddleX;
        ballY = H-2;
        ballZ = paddleZ;
        ballDX = 1;
        ballDY = -1;
        ballDZ = 0;
        ballLaunched = false;
    }

    static void LaunchBall() { if (!ballLaunched) ballLaunched = true; }

    static void MovePaddle(int dx, int dz)
    {
        int nx = paddleX+dx, nz = paddleZ+dz;
        if (nx>=0 && nx<W && nz>=0 && nz<D) {
            paddleX = nx;
            paddleZ = nz;
            if (!ballLaunched) { ballX = paddleX; ballZ = paddleZ; }
        }
    }

    static void Update()
    {
        if (gameOver || paused || !ballLaunched) return;
        ballX += ballDX; ballY += ballDY; ballZ += ballDZ;

        if (ballX<=0 || ballX>=W-1) { ballDX *= -1; ballX += ballDX*2; }
        if (ballZ<=0 || ballZ>=D-1) { ballDZ *= -1; ballZ += ballDZ*2; }
        if (ballY<=0) { ballDY *= -1; ballY += ballDY*2; }

        if (ballY>=H-1) {
            if (ballX>=paddleX-PADDLE_W/2 && ballX<=paddleX+PADDLE_W/2 && ballZ==paddleZ) {
                ballDY *= -1;
                ballY = H-2;
                int dx = ballX - paddleX;
                ballDX = (dx==0) ? 1 : dx;
                ballDZ = rand.Next(-1,2);
            } else {
                lives--;
                if (lives<=0) { gameOver=true; if(score>highScore) highScore=score; }
                else ResetBall();
            }
        }

        if (ballX>=0 && ballX<W && ballY>=0 && ballY<H && ballZ>=0 && ballZ<D) {
            if (blocks[ballX,ballY,ballZ] > 0) {
                blocks[ballX,ballY,ballZ]--;
                if (blocks[ballX,ballY,ballZ]==0) score += 10*level;
                if (ballX>0 && blocks[ballX-1,ballY,ballZ]>0) ballDX *= -1;
                else if (ballX<W-1 && blocks[ballX+1,ballY,ballZ]>0) ballDX *= -1;
                else if (ballY>0 && blocks[ballX,ballY-1,ballZ]>0) ballDY *= -1;
                else if (ballY<H-1 && blocks[ballX,ballY+1,ballZ]>0) ballDY *= -1;
                else if (ballZ>0 && blocks[ballX,ballY,ballZ-1]>0) ballDZ *= -1;
                else if (ballZ<D-1 && blocks[ballX,ballY,ballZ+1]>0) ballDZ *= -1;
                else ballDY *= -1;
                ballX += ballDX;
                ballY += ballDY;
                ballZ += ballDZ;
            }
        }

        bool blocksLeft = false;
        for (int x=0; x<W; x++) for (int y=0; y<H-1; y++) for (int z=0; z<D; z++)
            if (blocks[x,y,z]>0) blocksLeft=true;
        if (!blocksLeft) {
            level++;
            GenerateBlocks();
            ResetBall();
        }
    }

    static void Draw()
    {
        Console.Clear();
        Console.WriteLine($"🧱 ARKANOID 3D  |  Счёт: {score}  |  Уровень: {level}  |  Жизни: {lives}  |  Рекорд: {highScore}");
        if (paused) Console.WriteLine("⏸ ПАУЗА");
        for (int z=D-1; z>=0; z--) {
            Console.WriteLine($"\nСлой {z} (z={z}):");
            Console.WriteLine("+" + new string('-', W*2) + "+");
            for (int y=0; y<H; y++) {
                Console.Write("|");
                for (int x=0; x<W; x++) {
                    if (blocks[x,y,z] > 0) Console.Write(BLOCK+""+BLOCK);
                    else if (x==ballX && y==ballY && z==ballZ) Console.Write(BALL+""+BALL);
                    else Console.Write("  ");
                }
                Console.WriteLine("|");
            }
            Console.WriteLine("+" + new string('-', W*2) + "+");
        }
        Console.WriteLine("\nПлатформа (вид сверху):");
        Console.Write("  ");
        for (int x=0; x<W; x++) {
            if (x>=paddleX-PADDLE_W/2 && x<=paddleX+PADDLE_W/2 && z==paddleZ)
                Console.Write(PADDLE);
            else Console.Write(" ");
        }
        Console.WriteLine("\nУправление: WASD - движение, Пробел - запуск/пауза, Q - выход");
    }

    static int GetInput()
    {
        if (Console.KeyAvailable) {
            var key = Console.ReadKey(true).Key;
            if (key == ConsoleKey.Q) return -1;
            if (key == ConsoleKey.P) return -2;
            if (key == ConsoleKey.W) return 1;
            if (key == ConsoleKey.S) return 2;
            if (key == ConsoleKey.A) return 3;
            if (key == ConsoleKey.D) return 4;
            if (key == ConsoleKey.Spacebar) return 5;
        }
        return 0;
    }

    public static async Task Main()
    {
        LoadHighScore();
        GenerateBlocks();
        paddleX = W/2; paddleZ = D/2;
        ResetBall();
        score=0; lives=3; level=1; gameOver=false; paused=false;
        while (!quit && !gameOver) {
            Draw();
            int inp = GetInput();
            if (inp == -1) { quit=true; break; }
            if (inp == -2) { paused = !paused; continue; }
            if (!paused) {
                if (inp == 1) MovePaddle(0, -1);
                else if (inp == 2) MovePaddle(0, 1);
                else if (inp == 3) MovePaddle(-1, 0);
                else if (inp == 4) MovePaddle(1, 0);
                else if (inp == 5) {
                    if (!ballLaunched) LaunchBall();
                    else paused = !paused;
                }
                if ((DateTime.Now - lastUpdate).TotalSeconds > 0.05) {
                    Update();
                    lastUpdate = DateTime.Now;
                }
            }
            await Task.Delay(20);
        }
        Console.WriteLine($"ИГРА ОКОНЧЕНА! Счет: {score}");
        SaveHighScore();
    }
}
