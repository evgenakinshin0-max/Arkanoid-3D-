// arkanoid3d.js — Арканоид 3D на JavaScript (Node.js)

const keypress = require('keypress');

const W = 10, H = 8, D = 5;
const PADDLE_W = 5;

let blocks = [];
let paddleX = Math.floor(W/2);
let paddleZ = Math.floor(D/2);
let ballX = paddleX, ballY = H-2, ballZ = paddleZ;
let ballDX = 1, ballDY = -1, ballDZ = 0;
let score = 0, lives = 3, level = 1, highScore = 0;
let gameOver = false, paused = false, ballLaunched = false;
let lastUpdate = Date.now();
let quit = false;

function loadHighScore() { highScore = 0; }
function saveHighScore() {}

function generateBlocks() {
    blocks = Array.from({length: W}, () =>
        Array.from({length: H}, () =>
            Array.from({length: D}, (_, z) =>
                (y < H-1 && (x+y+z)%2===0) ? Math.floor(Math.random()*2)+1 : 0
            )
        )
    );
}

function resetBall() {
    ballX = paddleX;
    ballY = H-2;
    ballZ = paddleZ;
    ballDX = 1;
    ballDY = -1;
    ballDZ = 0;
    ballLaunched = false;
}

function launchBall() {
    if (!ballLaunched) ballLaunched = true;
}

function movePaddle(dx, dz) {
    const nx = paddleX + dx, nz = paddleZ + dz;
    if (nx>=0 && nx<W && nz>=0 && nz<D) {
        paddleX = nx;
        paddleZ = nz;
        if (!ballLaunched) { ballX = paddleX; ballZ = paddleZ; }
    }
}

function update() {
    if (gameOver || paused || !ballLaunched) return;
    ballX += ballDX;
    ballY += ballDY;
    ballZ += ballDZ;

    if (ballX<=0 || ballX>=W-1) { ballDX *= -1; ballX += ballDX*2; }
    if (ballZ<=0 || ballZ>=D-1) { ballDZ *= -1; ballZ += ballDZ*2; }
    if (ballY<=0) { ballDY *= -1; ballY += ballDY*2; }

    if (ballY>=H-1) {
        if (ballX>=paddleX-PADDLE_W/2 && ballX<=paddleX+PADDLE_W/2 && ballZ===paddleZ) {
            ballDY *= -1;
            ballY = H-2;
            const dx = ballX - paddleX;
            ballDX = (dx===0) ? 1 : dx;
            ballDZ = Math.floor(Math.random()*3)-1;
        } else {
            lives--;
            if (lives<=0) { gameOver=true; if(score>highScore) highScore=score; }
            else resetBall();
        }
    }

    if (ballX>=0 && ballX<W && ballY>=0 && ballY<H && ballZ>=0 && ballZ<D) {
        const bx = Math.floor(ballX), by = Math.floor(ballY), bz = Math.floor(ballZ);
        if (blocks[bx][by][bz] > 0) {
            blocks[bx][by][bz]--;
            if (blocks[bx][by][bz]==0) score += 10*level;
            // отражение
            if (bx>0 && blocks[bx-1][by][bz]>0) ballDX *= -1;
            else if (bx<W-1 && blocks[bx+1][by][bz]>0) ballDX *= -1;
            else if (by>0 && blocks[bx][by-1][bz]>0) ballDY *= -1;
            else if (by<H-1 && blocks[bx][by+1][bz]>0) ballDY *= -1;
            else if (bz>0 && blocks[bx][by][bz-1]>0) ballDZ *= -1;
            else if (bz<D-1 && blocks[bx][by][bz+1]>0) ballDZ *= -1;
            else ballDY *= -1;
            ballX += ballDX;
            ballY += ballDY;
            ballZ += ballDZ;
        }
    }

    let blocksLeft = false;
    for (let x=0; x<W; x++) for (let y=0; y<H-1; y++) for (let z=0; z<D; z++) {
        if (blocks[x][y][z]>0) blocksLeft=true;
    }
    if (!blocksLeft) {
        level++;
        generateBlocks();
        resetBall();
    }
}

function draw() {
    console.clear();
    console.log(`🧱 ARKANOID 3D  |  Счёт: ${score}  |  Уровень: ${level}  |  Жизни: ${lives}  |  Рекорд: ${highScore}`);
    if (paused) console.log("⏸ ПАУЗА");
    for (let z=D-1; z>=0; z--) {
        console.log(`\nСлой ${z} (z=${z}):`);
        let top = '+' + '-'.repeat(W*2) + '+';
        console.log(top);
        for (let y=0; y<H; y++) {
            let line = '|';
            for (let x=0; x<W; x++) {
                if (blocks[x][y][z] > 0) line += '██';
                else if (x===ballX && y===ballY && z===ballZ) line += '● ';
                else line += '  ';
            }
            line += '|';
            console.log(line);
        }
        console.log(top);
    }
    console.log('\nПлатформа (вид сверху):');
    let line = '  ';
    for (let x=0; x<W; x++) {
        if (x>=paddleX-PADDLE_W/2 && x<=paddleX+PADDLE_W/2) line += '=';
        else line += ' ';
    }
    console.log(line);
    console.log('Управление: WASD - движение, Пробел - запуск/пауза, Q - выход');
}

function setupInput() {
    keypress(process.stdin);
    process.stdin.on('keypress', (ch, key) => {
        if (key && key.ctrl && key.name === 'c') { quit = true; process.exit(); }
        if (key && key.name === 'q') { quit = true; }
        if (key && key.name === 'p') { paused = !paused; return; }
        if (gameOver || paused) return;
        if (key && key.name === 'w') movePaddle(0, -1);
        if (key && key.name === 's') movePaddle(0, 1);
        if (key && key.name === 'a') movePaddle(-1, 0);
        if (key && key.name === 'd') movePaddle(1, 0);
        if (key && key.name === 'space') {
            if (!ballLaunched) launchBall();
            else paused = !paused;
        }
    });
    process.stdin.setRawMode(true);
    process.stdin.resume();
}

function gameLoop() {
    if (gameOver) {
        draw();
        console.log(`ИГРА ОКОНЧЕНА! Счёт: ${score}`);
        saveHighScore();
        process.exit(0);
    }
    const now = Date.now();
    if ((now - lastUpdate) > 50) {
        update();
        lastUpdate = now;
    }
    draw();
    setTimeout(gameLoop, 20);
}

loadHighScore();
generateBlocks();
resetBall();
setupInput();
lastUpdate = Date.now();
gameLoop();
