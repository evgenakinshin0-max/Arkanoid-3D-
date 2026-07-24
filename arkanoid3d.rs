// arkanoid3d.rs — Арканоид 3D на Rust

use std::io::{self, Write, stdout};
use std::thread;
use std::time::{Duration, Instant};
use rand::Rng;
use termion::{clear, cursor, color, style};
use termion::input::TermRead;

const W: usize = 10;
const H: usize = 8;
const D: usize = 5;
const PADDLE_W: i32 = 5;

struct Game {
    blocks: Vec<Vec<Vec<i32>>>,
    paddle_x: i32,
    paddle_z: i32,
    ball_x: i32,
    ball_y: i32,
    ball_z: i32,
    ball_dx: i32,
    ball_dy: i32,
    ball_dz: i32,
    score: i32,
    lives: i32,
    level: i32,
    high_score: i32,
    game_over: bool,
    paused: bool,
    ball_launched: bool,
}

impl Game {
    fn new() -> Self {
        let mut game = Game {
            blocks: vec![vec![vec![0; D]; H]; W],
            paddle_x: (W/2) as i32,
            paddle_z: (D/2) as i32,
            ball_x: (W/2) as i32,
            ball_y: (H-2) as i32,
            ball_z: (D/2) as i32,
            ball_dx: 1,
            ball_dy: -1,
            ball_dz: 0,
            score: 0,
            lives: 3,
            level: 1,
            high_score: 0,
            game_over: false,
            paused: false,
            ball_launched: false,
        };
        game.load_high_score();
        game.generate_blocks();
        game
    }

    fn load_high_score(&mut self) {
        self.high_score = 0;
    }

    fn generate_blocks(&mut self) {
        let mut rng = rand::thread_rng();
        for x in 0..W {
            for y in 0..H-1 {
                for z in 0..D {
                    self.blocks[x][y][z] = if (x+y+z) % 2 == 0 { rng.gen_range(1..=2) } else { 0 };
                }
            }
        }
    }

    fn reset_ball(&mut self) {
        self.ball_x = self.paddle_x;
        self.ball_y = (H-2) as i32;
        self.ball_z = self.paddle_z;
        self.ball_dx = 1;
        self.ball_dy = -1;
        self.ball_dz = 0;
        self.ball_launched = false;
    }

    fn launch_ball(&mut self) {
        if !self.ball_launched {
            self.ball_launched = true;
        }
    }

    fn move_paddle(&mut self, dx: i32, dz: i32) {
        let nx = self.paddle_x + dx;
        let nz = self.paddle_z + dz;
        if nx >= 0 && nx < W as i32 && nz >= 0 && nz < D as i32 {
            self.paddle_x = nx;
            self.paddle_z = nz;
            if !self.ball_launched {
                self.ball_x = self.paddle_x;
                self.ball_z = self.paddle_z;
            }
        }
    }

    fn update(&mut self) {
        if self.game_over || self.paused || !self.ball_launched { return; }
        self.ball_x += self.ball_dx;
        self.ball_y += self.ball_dy;
        self.ball_z += self.ball_dz;

        if self.ball_x <= 0 || self.ball_x >= W as i32 -1 {
            self.ball_dx *= -1;
            self.ball_x += self.ball_dx * 2;
        }
        if self.ball_z <= 0 || self.ball_z >= D as i32 -1 {
            self.ball_dz *= -1;
            self.ball_z += self.ball_dz * 2;
        }
        if self.ball_y <= 0 {
            self.ball_dy *= -1;
            self.ball_y += self.ball_dy * 2;
        }

        if self.ball_y >= H as i32 -1 {
            let half = PADDLE_W / 2;
            if self.ball_x >= self.paddle_x - half && self.ball_x <= self.paddle_x + half && self.ball_z == self.paddle_z {
                self.ball_dy *= -1;
                self.ball_y = H as i32 - 2;
                let dx = self.ball_x - self.paddle_x;
                self.ball_dx = if dx == 0 { 1 } else { dx };
                let mut rng = rand::thread_rng();
                self.ball_dz = rng.gen_range(-1..=1);
            } else {
                self.lives -= 1;
                if self.lives <= 0 {
                    self.game_over = true;
                    if self.score > self.high_score { self.high_score = self.score; }
                } else {
                    self.reset_ball();
                }
            }
        }

        if self.ball_x >= 0 && self.ball_x < W as i32 && self.ball_y >= 0 && self.ball_y < H as i32 && self.ball_z >= 0 && self.ball_z < D as i32 {
            let bx = self.ball_x as usize;
            let by = self.ball_y as usize;
            let bz = self.ball_z as usize;
            if self.blocks[bx][by][bz] > 0 {
                self.blocks[bx][by][bz] -= 1;
                if self.blocks[bx][by][bz] == 0 {
                    self.score += 10 * self.level;
                }
                // отражение
                if bx > 0 && self.blocks[bx-1][by][bz] > 0 {
                    self.ball_dx *= -1;
                } else if bx < W-1 && self.blocks[bx+1][by][bz] > 0 {
                    self.ball_dx *= -1;
                } else if by > 0 && self.blocks[bx][by-1][bz] > 0 {
                    self.ball_dy *= -1;
                } else if by < H-1 && self.blocks[bx][by+1][bz] > 0 {
                    self.ball_dy *= -1;
                } else if bz > 0 && self.blocks[bx][by][bz-1] > 0 {
                    self.ball_dz *= -1;
                } else if bz < D-1 && self.blocks[bx][by][bz+1] > 0 {
                    self.ball_dz *= -1;
                } else {
                    self.ball_dy *= -1;
                }
                self.ball_x += self.ball_dx;
                self.ball_y += self.ball_dy;
                self.ball_z += self.ball_dz;
            }
        }

        let mut blocks_left = false;
        for x in 0..W {
            for y in 0..H-1 {
                for z in 0..D {
                    if self.blocks[x][y][z] > 0 { blocks_left = true; }
                }
            }
        }
        if !blocks_left {
            self.level += 1;
            self.generate_blocks();
            self.reset_ball();
        }
    }

    fn draw(&self) {
        print!("{}{}", clear::All, cursor::Goto(1,1));
        println!("🧱 ARKANOID 3D  |  Счёт: {}  |  Уровень: {}  |  Жизни: {}  |  Рекорд: {}", self.score, self.level, self.lives, self.high_score);
        if self.paused { println!("⏸ ПАУЗА"); }
        for z in (0..D).rev() {
            println!("\nСлой {} (z={}):", z, z);
            print!("+");
            for _ in 0..W*2 { print!("-"); }
            println!("+");
            for y in 0..H {
                print!("|");
                for x in 0..W {
                    if self.blocks[x][y][z] > 0 {
                        print!("██");
                    } else if x as i32 == self.ball_x && y as i32 == self.ball_y && z as i32 == self.ball_z {
                        print!("● ");
                    } else {
                        print!("  ");
                    }
                }
                println!("|");
            }
            print!("+");
            for _ in 0..W*2 { print!("-"); }
            println!("+");
        }
        println!("\nПлатформа (вид сверху):");
        print!("  ");
        for x in 0..W {
            let x_i = x as i32;
            if x_i >= self.paddle_x - PADDLE_W/2 && x_i <= self.paddle_x + PADDLE_W/2 && self.paddle_z == z as i32 {
                print!("=");
            } else {
                print!(" ");
            }
        }
        println!("\nУправление: WASD - движение, Пробел - запуск/пауза, Q - выход");
        stdout().flush().unwrap();
    }

    fn run(&mut self) {
        let stdin = io::stdin();
        let mut keys = stdin.keys();
        let mut last_update = Instant::now();
        while !self.game_over {
            self.draw();
            if let Some(Ok(key)) = keys.next() {
                match key {
                    termion::event::Key::Char('q') => break,
                    termion::event::Key::Char('p') => self.paused = !self.paused,
                    termion::event::Key::Char('w') => self.move_paddle(0, -1),
                    termion::event::Key::Char('s') => self.move_paddle(0, 1),
                    termion::event::Key::Char('a') => self.move_paddle(-1, 0),
                    termion::event::Key::Char('d') => self.move_paddle(1, 0),
                    termion::event::Key::Char(' ') => {
                        if !self.ball_launched {
                            self.launch_ball();
                        } else {
                            self.paused = !self.paused;
                        }
                    }
                    _ => {}
                }
            }
            if last_update.elapsed().as_secs_f64() > 0.05 {
                self.update();
                last_update = Instant::now();
            }
            thread::sleep(Duration::from_millis(20));
        }
        println!("ИГРА ОКОНЧЕНА! Счёт: {}", self.score);
    }
}

fn main() {
    let mut game = Game::new();
    game.run();
}
