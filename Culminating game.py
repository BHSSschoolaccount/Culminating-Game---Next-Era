# Programmer(s): Thomas & Jayden
# Date: Last year
# Description: Game with animated player, enemy logic, and a video-based home screen.


import pygame
import sys
import cv2
import time
import numpy as np
from pygame.locals import *


# Colours
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
RED = (220, 50, 50)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)



# System constants
FPS = 60
WIDTH = 1275
HEIGHT = 750    
BGCOLOUR = BLACK


# Initialize setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("NextEra")

# sounds -------
pygame.mixer.init()
pygame.mixer.music.load("screensong.mp3")  # Replace with your actual file path
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)  # Loops indefinitely
#sound effects

#attack sound effect
attack_sound = pygame.mixer.Sound("attacksound.mp3") 
attack_sound.set_volume(2)  # Optional: set the volume

#player walk sound effect
walk_sound = pygame.mixer.Sound("playerwalk.mp3")  # Replace with your actual file
walk_sound.set_volume(0.5)

jump_sound = pygame.mixer.Sound("jumpsound.mp3")  # Replace with your actual file
jump_sound.set_volume(0.5)


#enemy walk (clubbers)
enemy_walk_sound = pygame.mixer.Sound("squirewalk.mp3")  # replace with your file
enemy_walk_sound.set_volume(0.7)
enemy_walk_channel = pygame.mixer.Channel(2)

#button sound 
hover_sound = pygame.mixer.Sound("hover.mp3")  # Replace with your actual hover sound file
hover_sound.set_volume(0.5)
# Game variables
gravity = 1
jump_power = -15
ground_level = HEIGHT - 50
person_width, person_height = 40, 60
healthWidth, healthHeight = 20, 20
personHealth = 100
maxHealth = 100
gameTimer = 0


# Enemy variables
spearThrowerWidth, spearThrowerHeight = 40, 80
spearThrower_x, spearThrower_y = 100, ground_level - 60
spearThrower_bullets = []
spearThrower_shoot_timer = 0
spearThrower_vy = 0


clubberWidth, clubberHeight = 40, 60
clubber_x, clubber_y = 100, 60
clubber_vy = 0

#- background animation
background_frames = []
num_frames = 3
for i in range(num_frames):
    frame = pygame.image.load(f'battlebg{i}.png').convert()
    background_frames.append(frame)

current_frame = 0
frame_delay = 20
frame_counter = 0


# Home screen video
cap = cv2.VideoCapture("homeScreen.mp4")


# Start button
# Buttons
start_button_img = pygame.image.load("start1.png").convert_alpha()
start_button_hover_img = pygame.image.load("start2.png").convert_alpha()
exit_button_img = pygame.image.load("exit1.png").convert_alpha()
exit_button_hover_img = pygame.image.load("exit2.png").convert_alpha()
start_button_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 190))
exit_button_rect = exit_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 290))

lives = 3
heart_img = pygame.image.load("lives.png").convert_alpha()
heart_width = heart_img.get_width()
heart_height = heart_img.get_height()
heart_spacing = 10  # space between hearts

def draw_lives(surface, lives_count):
    for i in range(lives_count):
        # Calculate x position for each heart rectangle
        x = 250 + i * (heart_width + heart_spacing)
        y = 20
        surface.blit(heart_img, (x, y))


# Health bar
def draw_health_bar(surface, x, y, health, max_health):
    BAR_WIDTH = 200
    BAR_HEIGHT = 25
    health_ratio = health / max_health
    pygame.draw.rect(surface, RED, (x, y, BAR_WIDTH, BAR_HEIGHT))
    pygame.draw.rect(surface, GREEN, (x, y, BAR_WIDTH * health_ratio, BAR_HEIGHT))
    pygame.draw.rect(surface, WHITE, (x, y, BAR_WIDTH, BAR_HEIGHT), 2)

class SpearThrower:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, spearThrowerWidth, spearThrowerHeight)
        self.vy = 0
        self.bullets = []
        self.shoot_timer = 0
        self.health = 25


    def update(self, player):
        self.vy += gravity
        self.rect.y += self.vy
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.vy = 0


        # Chase player
        stop_distance = 500
        dx = player.rect.centerx - self.rect.centerx


        if abs(dx) > stop_distance:
            if dx > 0:
                self.rect.x += 2
            else:
                self.rect.x -= 2


        if self.rect.y < player.rect.y:
            self.rect.y += 2
        elif self.rect.y > player.rect.y:
            self.rect.y -= 2


        # Jump if close
        if abs(self.rect.x - player.rect.x) < 200 and abs(self.rect.bottom - ground_level) < 2:
            self.vy = -10


        # Shoot bullet
        self.shoot_timer += 1
        if self.shoot_timer >= 180:
            direction = -1 if self.rect.x > player.rect.x else 1
            bullet_x = self.rect.centerx
            bullet_y = self.rect.centery
            self.bullets.append(spearThrowerBullet(bullet_x, bullet_y, direction))
            self.shoot_timer = 0


        # Move bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.rect.right < 0 or bullet.rect.left > WIDTH:
                self.bullets.remove(bullet)
            elif bullet.rect.colliderect(player.rect):
                player.health -= 5
                self.bullets.remove(bullet)


    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)
        for bullet in self.bullets:
            surface.blit(bullet.image, bullet.rect)


# Spear bullets
class spearThrowerBullet:
    def __init__(self, x, y, direction):
        self.image = pygame.image.load("spear1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 10))
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def move(self):
        self.rect.x += self.direction * 12


# Clubber enemy
class Clubber:
    def __init__(self, x, y):
        self.walk_frames = [pygame.image.load(f"squire{i}.png").convert_alpha() for i in range(1, 8)]
        self.attack_frames = [pygame.image.load(f"sattack{i}.png").convert_alpha() for i in range(1, 5)]

        self.image = self.walk_frames[0]
        self.current_frame = 0
        self.frame_count = 0
        self.frame_delay = 8  # Number of frames before switching image

        self.attacking = False
        self.attack_frame_index = 0
        self.attack_frame_count = 0
        self.attack_frame_delay = 5


        self.facing_right = True
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vy = 0
        self.health = 20


    def update(self, player):
        self.vy += gravity
        self.rect.y += self.vy
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.vy = 0

            # Calculate distance to player
        distance_x = player.rect.centerx - self.rect.centerx
        distance_y = player.rect.centery - self.rect.centery
        distance = abs(distance_x)

        attack_range = 50 #measured in pixels
        if self.attacking:
            self.attack_frame_count += 1
            if self.attack_frame_count >= self.attack_frame_delay:
                self.attack_frame_count = 0
                self.attack_frame_index += 1

                # When attack animation ends
                if self.attack_frame_index >= len(self.attack_frames):
                    self.attacking = False
                    self.attack_frame_index = 0

                else:
                    # Apply damage on a specific attack frame
                    if self.attack_frame_index == 3:
                        if self.rect.colliderect(player.rect):
                            player.health -= 10  # Damage player
                            # Optional knockback
                            if self.facing_right:
                                player.rect.x += 50
                            else:
                                player.rect.x -= 50

            # Set image to current attack frame
            base_image = self.attack_frames[self.attack_frame_index % len(self.attack_frames)]
            self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
            return  # Skip movement during attack

        else:
            
            # If close enough to player, start attacking
            if distance < attack_range and abs(distance_y) < 20:
                self.attacking = True
                self.attack_frame_index = 0
                self.attack_frame_count = 0
                return  # Start attack, skip movement this frame

        moving = False
        if self.rect.x < player.rect.x:
            self.rect.x += 2
            self.facing_right = True
            moving = True
        elif self.rect.x > player.rect.x:
            self.rect.x -= 2
            self.facing_right = False
            moving = True

        
        if moving:
            self.frame_count += 1
            if self.frame_count >= self.frame_delay:
                self.frame_count = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                base_image = self.walk_frames[self.current_frame]
                self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
        else:
            # Idle frame
            base_image = self.walk_frames[0]
            self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
        
        #walkingso und efect for clubbers
        any_clubber_moving = any(
            clb.health > 0 and clb.rect.bottom >= ground_level and abs(clb.rect.x - player.rect.x) > 1
            for clb in clubbers)

        if any_clubber_moving:
            if not enemy_walk_channel.get_busy():
                enemy_walk_channel.play(enemy_walk_sound, loops=-1)
        else:
            if enemy_walk_channel.get_busy():
                enemy_walk_channel.stop()
    def draw(self, surface):
        surface.blit(self.image, self.rect)



# Player
class Animatedplayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [pygame.image.load(f"idle{i}.png").convert_alpha() for i in range(1, 10)]
        self.movingframes = [pygame.image.load(f"walk{i}.png").convert_alpha() for i in range(1, 10)]
        self.jumpframes = [pygame.image.load(f"jump{i}.png").convert_alpha() for i in range(1, 4)]
        self.fallframes = [pygame.image.load(f"fall{i}.png").convert_alpha() for i in range(1, 4)]
        self.attackframes = [pygame.image.load(f"attack{i}.png").convert_alpha() for i in range(1, 7)]
        self.slash_frames = [pygame.image.load(f"slash{i}.png").convert_alpha() for i in range(1, 5)]

        self.slash_index = 0
        self.slash_frame_delay = 0.5 # ticks per frame
        self.slash_frame_count = 0
        self.slash_active = False
        self.slash_pos = None


        self.attacking = False
        self.attack_frame_duration = 1  # controls speed of attack animation
        self.attack_frame_index = 0
        self.attack_frame_count = 0


        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)


        self.vy = 0
        self.speed = 8
        self.health = maxHealth
        self.facingright = True
        self.state = "idle"


        self.frame_delay = 8
        self.current_frame = 0
        self.frame_count = 0


    def update(self, keys):
        moving = False
        if self.attacking:
            self.attack_frame_count += 1
            if self.attack_frame_count >= self.attack_frame_duration:
                self.attack_frame_count = 0
                self.attack_frame_index += 1

                if self.attack_frame_index >= len(self.attackframes):
                    self.attacking = False  # done attacking
                    self.attack_frame_index = 0

            frame = self.attackframes[self.attack_frame_index % len(self.attackframes)]
            self.image = frame if self.facingright else pygame.transform.flip(frame, True, False)
            return
        if player.slash_active:
            player.slash_frame_count += 1
            if player.slash_frame_count >= player.slash_frame_delay:
                player.slash_frame_count = 0
                player.slash_index += 1
                if player.slash_index >= len(player.slash_frames):
                    player.slash_active = False
                    player.slash_index = 0
                    player.slash_pos = None
        if keys[K_d]:
            self.rect.x += self.speed
            self.facingright = True
            moving = True
        if keys[K_a]:
            self.rect.x -= self.speed
            self.facingright = False
            moving = True
        if keys[K_w] and abs(self.rect.bottom - ground_level) < 2:
            self.vy = jump_power
            if not pygame.mixer.Channel(3).get_busy():
                pygame.mixer.Channel(3).play(jump_sound)
        if keys[K_a] and keys[K_d]:
            moving = False
        


        self.vy += gravity
        self.rect.y += self.vy


        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.vy = 0
        
        on_ground = self.rect.bottom >= ground_level
        is_moving_lr = keys[K_a] != keys[K_d]  # only one of them is pressed

        if is_moving_lr and on_ground:
            if not pygame.mixer.Channel(1).get_busy():
                pygame.mixer.Channel(1).play(walk_sound, loops=-1)
        else:
            pygame.mixer.Channel(1).stop()


        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)


        # Animation state
        if self.vy < 0:
            self.state = "jump"
        elif self.vy > 0 and self.rect.bottom < ground_level:
            self.state = "fall"
        elif moving:
            self.state = "walk"
        else:
            self.state = "idle"


        self.frame_count += 1
        if self.frame_count >= self.frame_delay:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1)


            if self.state == "walk":
                frames = self.movingframes
            elif self.state == "jump":
                frames = self.jumpframes
            elif self.state == "fall":
                frames = self.fallframes
            else:
                frames = self.frames


            self.current_frame %= len(frames)
            baseimage = frames[self.current_frame]
            self.image = baseimage if self.facingright else pygame.transform.flip(baseimage, True, False)


# Sprite setup
player = Animatedplayer(WIDTH // 2, ground_level)


spearThrowers = []
spearThrower_spawn_points = [100, 300, 600, 900, 1200]
spearThrower_spawn_timer = 0
spearThrower_next_spawn = 120
spearThrower_index = 0


clubbers = []
clubber_spawn_points = [200, 400, 800, 700, 100]
clubber_spawn_timer = 0
clubber_next_spawn = 120
clubber_index = 0


allSprites = pygame.sprite.Group()
allSprites.add(player)

title = pygame.image.load("title.png").convert_alpha()

# Game loop
game_state = "start"
fade_alpha = 0
fade_speed = 1
running = True
attack_timer = 0
attack_cooldown = 10  # cooldown in frames

#button sounds hover
start_hovered_last = False
exit_hovered_last = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if game_state == "start":
        mouse_pos = pygame.mouse.get_pos()

        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(np.flip(frame, axis=1))
            screen.blit(pygame.surfarray.make_surface(frame), (0, 0))
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Cap alpha at 255
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)

        # Create copies of images with adjusted alpha
        title_fade = title.copy()
        start_img_fade = (start_button_hover_img if start_button_rect.collidepoint(mouse_pos)
                        else start_button_img).copy()
        exit_img_fade = (exit_button_hover_img if exit_button_rect.collidepoint(mouse_pos)
                        else exit_button_img).copy()

        # Set alpha transparency
        title_fade.set_alpha(fade_alpha)
        start_img_fade.set_alpha(fade_alpha)
        exit_img_fade.set_alpha(fade_alpha)

        # Check if currently hovering
        start_hovered_now = start_button_rect.collidepoint(mouse_pos)
        exit_hovered_now = exit_button_rect.collidepoint(mouse_pos)

        # Play hover sound if newly hovered
        if start_hovered_now and not start_hovered_last:
            hover_sound.play()
        if exit_hovered_now and not exit_hovered_last:
            hover_sound.play()

        # Update hover states for next frame
        start_hovered_last = start_hovered_now
        exit_hovered_last = exit_hovered_now
        screen.blit(title_fade, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))
        screen.blit(start_img_fade, start_button_rect)
        screen.blit(exit_img_fade, exit_button_rect)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    game_state = "play"
                    cap.release()
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("battlesong1.mp3")  # Replace with your gameplay music file
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(-1)
                elif exit_button_rect.collidepoint(event.pos):
                    running = False
        continue
        
    frame_counter += 1
    if frame_counter >= frame_delay:
        current_frame = (current_frame + 1) % num_frames
        frame_counter = 0


    # Main gameplay
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Update attack timer
    if attack_timer > 0:
        attack_timer -= 0.5


    attack_rect = None


    # Detect left mouse click to attack
    if pygame.mouse.get_pressed()[0] and attack_timer == 0 and not player.attacking:
        attack_sound.play()
        attack_timer = attack_cooldown
        player.attacking = True
        player.attack_frame_index = 0
        player.attack_frame_count = 0

        # Create attack hitbox depending on facing direction
        if player.facingright:
            attack_rect = pygame.Rect(player.rect.right, player.rect.top + 10, 40, player.rect.height - 20)
        else:
            attack_rect = pygame.Rect(player.rect.left - 40, player.rect.top + 10, 40, player.rect.height - 20)

        player.slash_active = True
        player.slash_index = 0
        player.slash_frame_count = 0
        player.slash_pos = attack_rect.topleft
        # Attack spear throwers
        for st in spearThrowers[:]:
            if attack_rect.colliderect(st.rect):
                st.health -= 5
                if player.facingright:
                    st.rect.x += 30
                else:
                    st.rect.x -= 30
                if st.health <= 0:
                    spearThrowers.remove(st)


        # Attack clubbers
        for clb in clubbers[:]:
            if attack_rect.colliderect(clb.rect):
                clb.health -= 5
                if player.facingright:
                    clb.rect.x += 30
                else:
                    clb.rect.x -= 30
                if clb.health <= 0:
                    clubbers.remove(clb)


    screen.fill(BGCOLOUR)
    screen.blit(background_frames[current_frame], (0, 0))


    allSprites.draw(screen)
    draw_health_bar(screen, 20, 20, player.health, maxHealth)


    # Spawn spear throwers
    spearThrower_spawn_timer += 1
    if spearThrower_index < len(spearThrower_spawn_points) and spearThrower_spawn_timer >= spearThrower_next_spawn:
        x = spearThrower_spawn_points[spearThrower_index]
        spearThrowers.append(SpearThrower(x, ground_level - spearThrowerHeight))
        spearThrower_index += 1
        spearThrower_spawn_timer = 0


    for st in spearThrowers:
        st.update(player)
        st.draw(screen)


    # Spawn clubbers
    clubber_spawn_timer += 1
    if clubber_index < len(clubber_spawn_points) and clubber_spawn_timer >= clubber_next_spawn:
        x = clubber_spawn_points[clubber_index]
        clubbers.append(Clubber(x, ground_level - clubberHeight))
        clubber_index += 1
        clubber_spawn_timer = 0


    for st in clubbers:
        st.update(player)
        st.draw(screen)
        if player.health <= 0:
            player.rect.x, player.rect.y = WIDTH // 2, ground_level - person_height // 2
            player.health = maxHealth
            lives -= 1
    
    if len(clubbers) == 0 and enemy_walk_channel.get_busy():
            enemy_walk_channel.stop()


    if player.health <= 0:
        player.rect.x, player.rect.y = WIDTH // 2, ground_level - person_height // 2
        player.health = maxHealth
        lives -= 1

    #SLash anim
    if player.slash_active and player.slash_pos is not None:
        slash_frame = player.slash_frames[player.slash_index]
        if not player.facingright:
            slash_frame = pygame.transform.flip(slash_frame, True, False)
        screen.blit(slash_frame, player.slash_pos)
        

    draw_lives(screen, lives)

        # Check if game should return to title screen
    all_enemies_defeated = (
        spearThrower_index >= len(spearThrower_spawn_points)
        and clubber_index >= len(clubber_spawn_points)
        and len(spearThrowers) == 0
        and len(clubbers) == 0
    )

    if lives <= 0 or all_enemies_defeated:
        # Reset game state
        game_state = "start"

        # Reset player
        player.rect.x, player.rect.y = WIDTH // 2, ground_level - person_height
        player.health = maxHealth
        lives = 3

        # Reset enemies
        spearThrowers.clear()
        clubbers.clear()
        spearThrower_index = 0
        spearThrower_spawn_timer = 0
        clubber_index = 0
        clubber_spawn_timer = 0

        # Restart video and music
        cap = cv2.VideoCapture("homeScreen.mp4")
        pygame.mixer.music.stop()
        pygame.mixer.music.load("screensong.mp3")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)
        enemy_walk_channel.stop()
        pygame.mixer.Channel(1).stop()

        fade_alpha = 0
        

        continue  # skip rest of loop to go to title screen

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()



