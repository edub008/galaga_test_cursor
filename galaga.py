import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class Star:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(1, 2)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

class Bullet:
    def __init__(self, x, y, speed, direction=1):
        self.x = x
        self.y = y
        self.speed = speed * direction
        self.width = 3
        self.height = 10
        self.active = True
    
    def update(self):
        self.y -= self.speed
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyBullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 4
        self.height = 8
        self.active = True
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 30
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 5
        self.bullets = []
        self.shoot_cooldown = 0
        self.lives = 3
        self.invulnerable = 0
        self.invulnerable_time = 120  # frames
    
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        
        # Shooting
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.shoot_cooldown == 0:
            self.shoot()
            self.shoot_cooldown = 10
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # Update invulnerability
        if self.invulnerable > 0:
            self.invulnerable -= 1
    
    def shoot(self):
        bullet_x = self.x + self.width // 2 - 1
        bullet_y = self.y
        self.bullets.append(Bullet(bullet_x, bullet_y, 10))
    
    def draw(self, screen):
        if self.invulnerable > 0 and self.invulnerable % 10 < 5:
            return  # Flash effect when invulnerable
        
        # Draw player ship (triangle shape)
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, CYAN, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def hit(self):
        if self.invulnerable == 0:
            self.lives -= 1
            self.invulnerable = self.invulnerable_time
            return True
        return False

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.enemy_type = enemy_type  # 0 = normal, 1 = boss
        self.width = 30 if enemy_type == 0 else 40
        self.height = 30 if enemy_type == 0 else 35
        self.speed = 1
        self.direction = 1
        self.active = True
        self.shoot_timer = random.randint(60, 180)
        self.formation_x = x
        self.formation_y = y
        self.attack_mode = False
        self.attack_speed = 3
        self.attack_direction = random.choice([-1, 1])
        self.returning = False
        self.return_x = x
        self.return_y = y
    
    def update(self, formation_offset_x=0, formation_offset_y=0):
        if not self.active:
            return
        
        if self.attack_mode:
            # Attack pattern - dive down
            self.x += self.attack_direction * self.attack_speed
            self.y += self.attack_speed
            
            if self.y > SCREEN_HEIGHT + 50:
                self.active = False
            if self.x < -50 or self.x > SCREEN_WIDTH + 50:
                self.active = False
        else:
            # Formation movement
            self.formation_x = self.start_x + formation_offset_x
            self.formation_y = self.start_y + formation_offset_y
            
            # Move towards formation position
            dx = self.formation_x - self.x
            dy = self.formation_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 2:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.x = self.formation_x
                self.y = self.formation_y
        
        # Shooting
        if not self.attack_mode:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = random.randint(120, 300)
                return True  # Signal to shoot
        return False
    
    def start_attack(self):
        if not self.attack_mode:
            self.attack_mode = True
            self.return_x = self.start_x
            self.return_y = self.start_y
    
    def draw(self, screen):
        if not self.active:
            return
        
        # Draw enemy ship
        if self.enemy_type == 0:
            # Normal enemy - bee-like shape
            pygame.draw.ellipse(screen, YELLOW, (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, RED, (self.x, self.y, self.width, self.height), 2)
            # Wings
            pygame.draw.ellipse(screen, YELLOW, (self.x - 5, self.y + 5, 15, 20))
            pygame.draw.ellipse(screen, YELLOW, (self.x + self.width - 10, self.y + 5, 15, 20))
        else:
            # Boss enemy - larger
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height), 2)
            # Details
            pygame.draw.circle(screen, YELLOW, (self.x + self.width // 2, self.y + self.height // 2), 8)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyFormation:
    def __init__(self):
        self.enemies = []
        self.formation_offset_x = 0
        self.formation_offset_y = 0
        self.formation_direction = 1
        self.formation_speed = 1
        self.attack_timer = 0
        self.create_formation()
    
    def create_formation(self):
        self.enemies = []
        rows = 5
        cols = 10
        start_x = 100
        start_y = 50
        spacing_x = 60
        spacing_y = 50
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                enemy_type = 1 if row == 0 else 0  # Top row is bosses
                self.enemies.append(Enemy(x, y, enemy_type))
    
    def update(self):
        # Formation movement (side to side)
        self.formation_offset_x += self.formation_direction * self.formation_speed
        
        if self.formation_offset_x > 200 or self.formation_offset_x < -200:
            self.formation_direction *= -1
            self.formation_offset_y += 20  # Move down when hitting edge
        
        # Update enemies
        enemy_bullets_to_create = []
        for enemy in self.enemies[:]:
            should_shoot = enemy.update(self.formation_offset_x, self.formation_offset_y)
            if should_shoot and random.random() < 0.3:  # 30% chance to shoot
                enemy_bullets_to_create.append(enemy)
            if not enemy.active:
                self.enemies.remove(enemy)
        
        # Attack pattern - random enemies dive
        self.attack_timer += 1
        if self.attack_timer > 180 and len(self.enemies) > 0:
            self.attack_timer = 0
            # Select random enemy to attack
            if random.random() < 0.3:  # 30% chance
                attacking_enemies = [e for e in self.enemies if not e.attack_mode]
                if attacking_enemies:
                    random.choice(attacking_enemies).start_attack()
        
        return enemy_bullets_to_create
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def check_collisions(self, bullets):
        score = 0
        for bullet in bullets[:]:
            if not bullet.active:
                continue
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                if enemy.active and bullet_rect.colliderect(enemy.get_rect()):
                    enemy.active = False
                    bullet.active = False
                    score += 100 if enemy.enemy_type == 0 else 200
                    break
        return score
    
    def check_player_collision(self, player_rect):
        for enemy in self.enemies:
            if enemy.active and enemy.get_rect().colliderect(player_rect):
                return True
        return False
    
    def is_empty(self):
        return len(self.enemies) == 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Galaga Clone")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.player = None
        self.formation = None
        self.stars = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.enemy_bullets = []
        
        # Create starfield
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.5, 2)
            self.stars.append(Star(x, y, speed))
    
    def handle_menu(self, keys):
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            self.start_game()
    
    def start_game(self):
        self.state = GameState.PLAYING
        self.player = Player()
        self.formation = EnemyFormation()
        self.score = 0
        self.enemy_bullets = []
    
    def update(self, keys):
        if self.state == GameState.MENU:
            self.handle_menu(keys)
        elif self.state == GameState.PLAYING:
            # Update stars
            for star in self.stars:
                star.update()
            
            # Update player
            self.player.update(keys)
            
            # Update formation and get enemies that want to shoot
            shooting_enemies = self.formation.update()
            for enemy in shooting_enemies:
                bullet_x = enemy.x + enemy.width // 2
                bullet_y = enemy.y + enemy.height
                self.enemy_bullets.append(EnemyBullet(bullet_x, bullet_y, 4))
            
            # Update enemy bullets
            for bullet in self.enemy_bullets[:]:
                bullet.update()
                if not bullet.active:
                    self.enemy_bullets.remove(bullet)
            
            # Check collisions
            # Player bullets vs enemies
            player_bullets = [b for b in self.player.bullets if b.active]
            score_gain = self.formation.check_collisions(player_bullets)
            self.score += score_gain
            
            # Enemy bullets vs player
            player_rect = self.player.get_rect()
            for bullet in self.enemy_bullets[:]:
                if bullet.active and bullet.get_rect().colliderect(player_rect):
                    if self.player.hit():
                        bullet.active = False
                        if self.player.lives <= 0:
                            self.state = GameState.GAME_OVER
            
            # Enemy vs player collision
            if self.formation.check_player_collision(player_rect):
                if self.player.hit():
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
            
            # Check if formation is empty (new wave)
            if self.formation.is_empty():
                self.formation = EnemyFormation()
                self.player.invulnerable = 120  # Brief invulnerability between waves
            
        elif self.state == GameState.GAME_OVER:
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.state = GameState.MENU
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        if self.state == GameState.MENU:
            title = self.font.render("GALAGA CLONE", True, YELLOW)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(title, title_rect)
            
            instruction = self.small_font.render("Press SPACE or ENTER to start", True, WHITE)
            inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(instruction, inst_rect)
            
            controls = [
                "Controls:",
                "Arrow Keys or WASD - Move",
                "Space/Up - Shoot"
            ]
            y_offset = SCREEN_HEIGHT // 2 + 80
            for i, text in enumerate(controls):
                ctrl_text = self.small_font.render(text, True, WHITE)
                ctrl_rect = ctrl_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 25))
                self.screen.blit(ctrl_text, ctrl_rect)
        
        elif self.state == GameState.PLAYING:
            # Draw game elements
            self.player.draw(self.screen)
            self.formation.draw(self.screen)
            
            # Draw enemy bullets
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
            
            # Draw UI
            score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, WHITE)
            self.screen.blit(lives_text, (10, 35))
        
        elif self.state == GameState.GAME_OVER:
            game_over = self.font.render("GAME OVER", True, RED)
            go_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over, go_rect)
            
            final_score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
            fs_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(final_score, fs_rect)
            
            restart = self.small_font.render("Press SPACE or ENTER to return to menu", True, WHITE)
            restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            self.update(keys)
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

