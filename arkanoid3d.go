// arkanoid3d.go — Арканоид 3D на Go

package main

import (
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"time"

	"github.com/eiannone/keyboard"
)

const W = 10
const H = 8
const D = 5
const PADDLE_W = 5

var blocks [][][]int
var paddleX, paddleZ int
var ballX, ballY, ballZ int
var ballDX, ballDY, ballDZ int
var score, lives, level, highScore int
var gameOver, paused, ballLaunched bool
var randSrc *rand.Rand
var lastUpdate time.Time

func clear() {
	cmd := exec.Command("clear")
	cmd.Stdout = os.Stdout
	cmd.Run()
}

func loadHighScore() { highScore = 0 }
func saveHighScore() {}

func generateBlocks() {
	blocks = make([][][]int, W)
	for x := 0; x < W; x++ {
		blocks[x] = make([][]int, H)
		for y := 0; y < H; y++ {
			blocks[x][y] = make([]int, D)
			for z := 0; z < D; z++ {
				if y < H-1 {
					blocks[x][y][z] = ((x+y+z)%2 == 0) ? randSrc.Intn(2)+1 : 0
				}
			}
		}
	}
}

func resetBall() {
	ballX = paddleX
	ballY = H - 2
	ballZ = paddleZ
	ballDX = 1
	ballDY = -1
	ballDZ = 0
	ballLaunched = false
}

func launchBall() {
	if !ballLaunched {
		ballLaunched = true
	}
}

func movePaddle(dx, dz int) {
	nx := paddleX + dx
	nz := paddleZ + dz
	if nx >= 0 && nx < W && nz >= 0 && nz < D {
		paddleX = nx
		paddleZ = nz
		if !ballLaunched {
			ballX = paddleX
			ballZ = paddleZ
		}
	}
}

func update() {
	if gameOver || paused || !ballLaunched {
		return
	}
	ballX += ballDX
	ballY += ballDY
	ballZ += ballDZ

	if ballX <= 0 || ballX >= W-1 {
		ballDX *= -1
		ballX += ballDX * 2
	}
	if ballZ <= 0 || ballZ >= D-1 {
		ballDZ *= -1
		ballZ += ballDZ * 2
	}
	if ballY <= 0 {
		ballDY *= -1
		ballY += ballDY * 2
	}

	if ballY >= H-1 {
		if ballX >= paddleX-PADDLE_W/2 && ballX <= paddleX+PADDLE_W/2 && ballZ == paddleZ {
			ballDY *= -1
			ballY = H - 2
			dx := ballX - paddleX
			if dx == 0 {
				ballDX = 1
			} else {
				ballDX = dx
			}
			ballDZ = randSrc.Intn(3) - 1
		} else {
			lives--
			if lives <= 0 {
				gameOver = true
				if score > highScore {
					highScore = score
				}
			} else {
				resetBall()
			}
		}
	}

	if ballX >= 0 && ballX < W && ballY >= 0 && ballY < H && ballZ >= 0 && ballZ < D {
		if blocks[ballX][ballY][ballZ] > 0 {
			blocks[ballX][ballY][ballZ]--
			if blocks[ballX][ballY][ballZ] == 0 {
				score += 10 * level
			}
			// отражение
			if ballX > 0 && blocks[ballX-1][ballY][ballZ] > 0 {
				ballDX *= -1
			} else if ballX < W-1 && blocks[ballX+1][ballY][ballZ] > 0 {
				ballDX *= -1
			} else if ballY > 0 && blocks[ballX][ballY-1][ballZ] > 0 {
				ballDY *= -1
			} else if ballY < H-1 && blocks[ballX][ballY+1][ballZ] > 0 {
				ballDY *= -1
			} else if ballZ > 0 && blocks[ballX][ballY][ballZ-1] > 0 {
				ballDZ *= -1
			} else if ballZ < D-1 && blocks[ballX][ballY][ballZ+1] > 0 {
				ballDZ *= -1
			} else {
				ballDY *= -1
			}
			ballX += ballDX
			ballY += ballDY
			ballZ += ballDZ
		}
	}

	blocksLeft := false
	for x := 0; x < W; x++ {
		for y := 0; y < H-1; y++ {
			for z := 0; z < D; z++ {
				if blocks[x][y][z] > 0 {
					blocksLeft = true
				}
			}
		}
	}
	if !blocksLeft {
		level++
		generateBlocks()
		resetBall()
	}
}

func draw() {
	clear()
	fmt.Printf("🧱 ARKANOID 3D  |  Счёт: %d  |  Уровень: %d  |  Жизни: %d  |  Рекорд: %d\n", score, level, lives, highScore)
	if paused {
		fmt.Println("⏸ ПАУЗА")
	}
	for z := D - 1; z >= 0; z-- {
		fmt.Printf("\nСлой %d (z=%d):\n", z, z)
		fmt.Print("+" + strings.Repeat("-", W*2) + "+\n")
		for y := 0; y < H; y++ {
			fmt.Print("|")
			for x := 0; x < W; x++ {
				if blocks[x][y][z] > 0 {
					fmt.Print("██")
				} else if x == ballX && y == ballY && z == ballZ {
					fmt.Print("● ")
				} else {
					fmt.Print("  ")
				}
			}
			fmt.Println("|")
		}
		fmt.Print("+" + strings.Repeat("-", W*2) + "+\n")
	}
	fmt.Println("\nПлатформа (вид сверху):")
	fmt.Print("  ")
	for x := 0; x < W; x++ {
		if x >= paddleX-PADDLE_W/2 && x <= paddleX+PADDLE_W/2 {
			fmt.Print("=")
		} else {
			fmt.Print(" ")
		}
	}
	fmt.Println("\nУправление: WASD - движение, Пробел - запуск/пауза, Q - выход")
}

func main() {
	randSrc = rand.New(rand.NewSource(time.Now().UnixNano()))
	loadHighScore()
	generateBlocks()
	paddleX = W / 2
	paddleZ = D / 2
	resetBall()
	score = 0
	lives = 3
	level = 1
	gameOver = false
	paused = false

	if err := keyboard.Open(); err != nil {
		panic(err)
	}
	defer keyboard.Close()

	lastUpdate = time.Now()
	for !gameOver {
		draw()
		_, key, err := keyboard.GetKey()
		if err != nil {
			continue
		}
		if key == keyboard.KeyEsc || key == 'q' || key == 'Q' {
			break
		}
		if key == 'p' || key == 'P' {
			paused = !paused
			continue
		}
		if !paused {
			switch key {
			case 'w', 'W':
				movePaddle(0, -1)
			case 's', 'S':
				movePaddle(0, 1)
			case 'a', 'A':
				movePaddle(-1, 0)
			case 'd', 'D':
				movePaddle(1, 0)
			case ' ':
				if !ballLaunched {
					launchBall()
				} else {
					paused = !paused
				}
			}
			if time.Since(lastUpdate).Seconds() > 0.05 {
				update()
				lastUpdate = time.Now()
			}
		}
		time.Sleep(20 * time.Millisecond)
	}
	fmt.Printf("ИГРА ОКОНЧЕНА! Счёт: %d\n", score)
	saveHighScore()
}
