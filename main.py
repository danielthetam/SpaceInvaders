import pygame
import sys
import os
import random
from pygame import math


class Line:
    def __init__(self, LINE_SIZE, LINE_SPEED, LINE_COLOR, LINE_POSITION, LINE_DIRECTION):
        self.LINE_SIZE = LINE_SIZE
        self.LINE_SPEED = LINE_SPEED * LINE_DIRECTION
        self.LINE_COLOR = LINE_COLOR
        self.LINE_POSITION = LINE_POSITION
        self.line_rect = None


    def draw(self, display):
        self.LINE_POSITION.y += self.LINE_SPEED  # Moving the lines
        self.line_rect = pygame.draw.rect(display, self.LINE_COLOR, pygame.Rect(self.LINE_POSITION, self.LINE_SIZE))


    def check_border(self, border):
        if self.LINE_POSITION.y + self.LINE_SIZE.y <= border:
            return True

        else:
            return False


class Particles:
    def __init__(self, particle_pos, PARTICLE_COUNT, PARTICLE_COLOR, PARTICLE_SIZE, SPREAD_RADIUS, PARTICLE_SPEED):
        self.PARTICLE_COUNT = PARTICLE_COUNT
        self.PARTICLE_COLOR = PARTICLE_COLOR
        self.PARTICLE_SIZE = PARTICLE_SIZE
        self.SPREAD_RADIUS = SPREAD_RADIUS  # Determines the speed at which the particles die off
        self.PARTICLE_SPEED = PARTICLE_SPEED
        self.particle_pos = particle_pos

        self.particles = []  # Each list contains the position, velocity

        for i in range(self.PARTICLE_COUNT):  # Add a particle list in the range of particle count
            # Generating random velocity/direction
            random_vel_x = random.randint(self.PARTICLE_SPEED[0], self.PARTICLE_SPEED[1])
            random_vel_y = random.randint(self.PARTICLE_SPEED[0], self.PARTICLE_SPEED[1])

            # Declaring particle position
            particle_pos = math.Vector2(particle_pos[0], particle_pos[1])

            self.particles.append([particle_pos, math.Vector2(random_vel_x, random_vel_y)])


    def draw(self, display):
        """
        This is where we draw particles
        """
        for particle in self.particles:
            particle[0] += particle[1]  # Adding position of particle by velocity

            pygame.draw.rect(display, self.PARTICLE_COLOR, pygame.Rect(particle[0], self.PARTICLE_SIZE))

    def update(self):
        # Decreasing particle size
        self.PARTICLE_SIZE -= math.Vector2(self.SPREAD_RADIUS, self.SPREAD_RADIUS)


class Bullet:
    def __init__(self, BULLET_SIZE, BULLET_SPEED, BULLET_COLOR, bullet_pos, BULLET_DIRECTION, ignore_class):
        self.BULLET_SIZE = BULLET_SIZE
        self.BULLET_SPEED = BULLET_SPEED * BULLET_DIRECTION
        self.BULLET_COLOR = BULLET_COLOR
        self.bullet_pos = bullet_pos
        self.bullet_rect = None
        self.ignore_class = ignore_class

    def draw(self, display):
        # Draws the bullet rect
        self.move()
        self.bullet_rect = pygame.draw.rect(display, self.BULLET_COLOR, pygame.Rect(self.bullet_pos, self.BULLET_SIZE))

    def move(self):
        # Moves the bullet in the correct direction
        self.bullet_pos.y += self.BULLET_SPEED

    def check_collision(self, objects):
        for object in objects:
            if self.bullet_rect.colliderect(object.rect) and not isinstance(object, self.ignore_class):
                return object
        return None


    def check_border(self, border):
        # Checks to see if the bullet's position is over the boundary

        if self.bullet_pos.y + self.BULLET_SIZE.y <= border:
            return True
        else:
            return False


class Enemy:
    def __init__(self, size, position, color, speed, forward_speed):
        self.size = size
        self.position = math.Vector2(position.x, position.y)
        self.color = color
        self.speed = speed
        self.forward_speed = forward_speed
        self.right = True
        self.rect = None

    def draw(self, display):
        self.update()
        self.rect = pygame.draw.rect(display, self.color, pygame.Rect(self.position, self.size))  # Rendering enemy

    def check_border_collision(self, window_size):
        """
        Checks for collision with borders
        """
        if self.position.x <= 0:  # Over the left border
            return True
        elif self.position.x + self.size.x >= window_size[0]:  # Over the right border
            return True
        else:
            return False

    def check_player_collision(self):
        pass

    def update(self):
        """
        Defines the movement of the enemy
        """
        if self.right:
            self.position.x += self.speed
        else:
            self.position.x -= self.speed

    def move_forward(self):
        # Move the enemy forward
        self.position.y += self.forward_speed
        self.right = not self.right

class Player:
    def __init__(self, speed, size, position, color):
        self.speed = speed
        self.size = size
        self.position = position
        self.color = color
        self.rect = None
        self.left = False
        self.right = False
        self.is_dead = False


    def draw(self, display):
        if not self.is_dead:
            self.rect = pygame.draw.rect(display, self.color, pygame.Rect(self.position, self.size))


    def update(self):
        if not self.is_dead:
            if self.left:
                self.position.x -= self.speed
            elif self.right:
                self.position.x += self.speed


    def dead(self, lives):
        if lives <= 0:
            self.is_dead = True
            return True
        else:
            return False


class Game:
    def __init__(self):
        # Initializing the program
        pygame.init()
        pygame.font.init()

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pygame.time.Clock()

        self.WINDOW_SIZE = (800, 800)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Space Invaders")

        # Setting Icon
        icon = pygame.image.load(r"space_invaders.png")
        pygame.display.set_icon(icon)

        # Initalizing the fonts
        self.font_size = 30
        self.font = pygame.font.Font(r"fonts\ARCADE_N.TTF", self.font_size)

        # Audio Initialisation
        pygame.mixer.init()
        self.blip_sfx = pygame.mixer.Sound(r"sfx/blip.wav")  # Played when enter key is pressed
        self.explosion_sfx = pygame.mixer.Sound(r"sfx/explosion.wav")
        self.laser_sfx = pygame.mixer.Sound(r"sfx/laser_shot.wav")
        self.damage_sfx = pygame.mixer.Sound(r"sfx/damage.wav")
        self.loading_sfx = pygame.mixer.Sound(r"sfx/loading.wav")  # Played when enemies die

        # Player Details
        self.player = Player(8, math.Vector2(50, 50), math.Vector2(450, 700), (100, 255, 105))
        self.bullet_cooldown = 3
        self.mouse_button_hold = False

        # Game Variables
        self.score = 0
        self.lives = 3
        self.enemy_speed_stages = [[35, False], [25, False], [10, False]]  # Give the percentages of enemies at which the speeds should increase
        self.enemy_speed_increase = .5
        self.can_restart = False  # Only enables when the player dies

        # Bullet Objects
        self.bullets = []
        self.shot_cooldown = 1.2 * 1000
        self.next_shot_time = 0

        self.objects = []  # A list of colliders for the bullet class to collide with
        self.objects.append(self.player)

        # Particle Objects
        self.particles = []

        # Line Object
        self.lines = []
        self.next_line_spawn = 0
        self.line_spawn_cooldown = 0.3 * 1000

        # Enemy Details
        self.enemies = []
        self.enemy_count = 55
        self.spawn_enemies()
        self.enemy_max_speed = 4

        # Enemy Shooting
        self.enemy_shoot_cooldown = 1.5 * 1000
        self.next_enemy_shoot = 0

        # Wave Spawning when Enemy Dies
        self.wave_spawn_cooldown = 3 * 1000
        self.spawn_wave_time = 0
        self.no_enemies = False


    def draw(self):
        """
        Handles the drawing of rects and surfaces
        """
        self.display.fill((0, 0, 0))

        for line in self.lines:  # Rendering decorative background lines
            line.draw(self.display)

            if line.check_border(0):
                self.lines.remove(line)

        # Player
        self.player.draw(self.display)

        for bullet in self.bullets:  # Rendering bullets
            bullet.draw(self.display)

            if bullet.check_border(0):
                self.bullets.remove(bullet)


        for particle in self.particles:  # Rendering particles
            if particle.PARTICLE_SIZE.x > 0 and particle.PARTICLE_SIZE.y > 0:  # If the particle is not too small in size, continue to draw it
                particle.draw(self.display)
                particle.update()

            else:  # Or else, stop drawing it
                self.particles.remove(particle)

        enemy_move_forward = False
        for enemy in self.enemies:  # Rendering Enemies
            enemy.draw(self.display)

            if enemy.check_border_collision(self.WINDOW_SIZE):  # If enemy hits the border
                enemy_move_forward = True  # Set enemy_move_forward to true

        if enemy_move_forward:  # If enemy_move_forward is true
            for enemy in self.enemies:  # Move all enemies forward
                enemy.move_forward()

            enemy_move_forward = False  # Set it back to false

        # Rendering Texts
        score_text = self.font.render(f"Score: {self.score}", False, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.lives}", False, (255, 255, 255))

        self.display.blit(score_text, math.Vector2(20, self.WINDOW_SIZE[1] - (self.font_size * 3)))
        self.display.blit(lives_text, math.Vector2(20, self.WINDOW_SIZE[1] - self.font_size - 10))

        pygame.display.update()


    def enemy_shoot(self):
        shots = random.randint(1, 3)

        for i in range(shots):
            enemy = random.choice(self.enemies)
            # Spawn a bullet by the enemy's position
            bullet_size = math.Vector2(10, 20)
            bullet_pos = math.Vector2(enemy.position.x + (enemy.size.x/2) - (bullet_size.x/2), enemy.position.y)
            bullet = Bullet(bullet_size, 5, (100, 255, 105), bullet_pos, 1, Enemy)
            self.bullets.append(bullet)

            particle = Particles(bullet.bullet_pos, 15, (100, 255, 105), math.Vector2(20, 20), 1.5, (-10, 10))
            self.particles.append(particle)
            self.laser_sfx.play()

    def spawn_enemies(self):
        """
        Spawns the enemies
        """
        # Enemy details
        enemy_size = 40
        space_btwn_enemies = 30
        space_btwn_window_and_enemy = 60
        enemy_spawn_point = math.Vector2(space_btwn_window_and_enemy, 50)
        enemy_speed = .1

        for i in range(self.enemy_count):  # For every enemy
            if enemy_spawn_point.x + enemy_size > self.WINDOW_SIZE[0] - space_btwn_window_and_enemy:  # If enemy spawn point is over the border
                enemy_spawn_point = math.Vector2(space_btwn_window_and_enemy, enemy_spawn_point.y + (enemy_size * 1.5))  # Spawn at the next row

            new_enemy = Enemy(math.Vector2(enemy_size, enemy_size), enemy_spawn_point, (100, 255, 105), enemy_speed, 50)  # Spawn the enemy

            self.enemies.append(new_enemy)
            self.objects.append(new_enemy)

            enemy_spawn_point.x += space_btwn_enemies + enemy_size  # Declare the next spawn point for the next enemy


    def event_handler(self):
        """
        Handles events and input
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_a:  # On key press 'a'
                    self.player.left = True
                elif event.key == pygame.K_d:  # On key press 'd'
                    self.player.right = True

                elif event.key == pygame.K_SPACE and pygame.time.get_ticks() >= self.next_shot_time and not self.player.is_dead:  # On space key pressed
                    # Spawn a bullet and add it to the array of bullets
                    bullet_size = math.Vector2(10, 20)
                    bullet_pos = math.Vector2(self.player.position.x + (self.player.size.x/2) - (bullet_size.x/2), self.player.position.y)
                    bullet = Bullet(bullet_size, 5, (100, 255, 105), bullet_pos, -1, Player)
                    self.bullets.append(bullet)
                    self.next_shot_time = pygame.time.get_ticks()
                    self.next_shot_time += self.shot_cooldown
                    self.laser_sfx.play()

                    # Spawning Particle
                    particle = Particles(bullet.bullet_pos, 15, (100, 255, 105), math.Vector2(20, 20), 1.5, (-10, 10))
                    self.particles.append(particle)

                elif event.key == pygame.K_RETURN and self.can_restart:
                    self.restart_game()
                    self.blip_sfx.play()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.player.left = False
                elif event.key == pygame.K_d:
                    self.player.right = False

            elif event.type == pygame.MOUSEBUTTONDOWN:  # When player clicks the mouse
                self.mouse_button_hold = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_button_hold = False

    def spawn_particles(self, position, particle_count):
        particle = Particles(position, particle_count, (100, 255, random.randint(80, 130)), math.Vector2(20, 20), .6, (-10, 10))
        self.particles.append(particle)


    def check_bullet_collision(self):
        for bullet in self.bullets:  # For every bullet
            collided_object = bullet.check_collision(self.objects)  # Check if the bullet is colliding with an object in the list of objects/colliders
            if isinstance(collided_object, Enemy) and collided_object in self.enemies:  # If the collided object is an enemy
                self.enemies.remove(collided_object)  # Remove the enemy from list of colliders and enemies
                self.objects.remove(collided_object)
                self.spawn_particles(collided_object.position, 50)
                self.score += 30  
                self.explosion_sfx.play()

            elif isinstance(collided_object, Player) and self.lives > 0:  # If the collided object is a player
                self.lives -= 1
                self.damage_sfx.play()
            else:
                continue
            self.bullets.remove(bullet)

    
    def check_speed_up(self):
        if len(self.enemies) == 3 and self.enemies[0] != self.enemy_max_speed:
            for enemy in self.enemies:
                enemy.speed = self.enemy_max_speed
            return None

        percentage_of_enemies = (len(self.enemies)/self.enemy_count) * 100  # Use a list of lists that store the percentage and booleans
        for stage in self.enemy_speed_stages:
            if int(percentage_of_enemies) <= stage[0] and not stage[1]: 
                self.enemy_speed_stages[self.enemy_speed_stages.index(stage)][1] = True  # Has been used
                for enemy in self.enemies:
                    enemy.speed += self.enemy_speed_increase


    def restart_game(self):
        self.player = Player(8, math.Vector2(50, 50), math.Vector2(450, 700), (100, 255, 105))

        self.score = 0
        self.lives = 3

        self.enemy_speed_stages = [[35, False], [25, False], [10, False]]  # Give the percentages of enemies at which the speeds should increase

        self.bullets = []

        self.objects = []
        self.objects.append(self.player)

        self.enemies = []
        self.spawn_enemies()

        self.can_restart = False

    
    def check_enemy_invaded_planet(self):
        """
        Checks if the enemy goes over the player, the player's lives decrease
        """
        for enemy in self.enemies:
            if enemy.position.y >= self.WINDOW_SIZE[1]:
                self.lives -= 1
                self.spawn_particles(enemy.position, 30)
                self.explosion_sfx.play()
                self.enemies.remove(enemy)


    def update(self):
        """
        Handles the checking of collisions and boundaries and update of movement
        """

        self.player.update()  # Moving the player according to key press
        self.check_bullet_collision()  # Checking for bullet collision with 
        self.check_speed_up()
        self.check_enemy_invaded_planet()


        # Right-side Boundary
        if (self.player.position.x + self.player.size.x) >= self.WINDOW_SIZE[0]:  # If player is colliding with right side
            self.player.right = False  # Stop moving right
            self.player.position.x = self.WINDOW_SIZE[0] - self.player.size.x  # Reset position
        elif self.player.position.x <= 0:  # If player is colliding with left side
            self.player.left = False
            self.player.position.x = 0

        # Spawning decorative space lines over a cooldown
        if pygame.time.get_ticks() >= self.next_line_spawn:
            # Create a new line
            line_size = 10
            line_speed = random.randint(5, 15)
            line = Line(math.Vector2(line_size, line_size), line_speed, (255, 255, 255), math.Vector2(random.randint(0, self.WINDOW_SIZE[0] - line_size), 0 - line_size), 1)
            self.lines.append(line)  # Add the new line to an array of lines
            self.next_line_spawn = pygame.time.get_ticks()
            self.next_line_spawn += self.line_spawn_cooldown  # Reset the cooldown

        # When the player is holding the mouse button
        if self.mouse_button_hold:
            # Keep spawning particles haha
            # Particles go brrrr
            self.spawn_particles(pygame.mouse.get_pos(), 30)

        if not self.player.is_dead and self.player.dead(self.lives):  # If the player dies
            self.spawn_particles(self.player.position, 50)  # Spawn some particles
            for enemy in self.enemies:  # Spawn particles by every enemy
                self.spawn_particles(enemy.position, 50)
                self.explosion_sfx.play()

            self.enemies = []  # Clear all enemies
            self.can_restart = True  # Allow the player to restart the game


        if pygame.time.get_ticks() >= self.next_enemy_shoot and len(self.enemies) != 0:  # Timing the enemy shots
            self.enemy_shoot()
            self.next_enemy_shoot = pygame.time.get_ticks()
            self.next_enemy_shoot += self.enemy_shoot_cooldown

        if len(self.enemies) == 0 and not self.no_enemies and not self.player.is_dead:  # If all enemies are dead
            self.no_enemies = True
            self.bullets = []
            self.spawn_wave_time = pygame.time.get_ticks() + self.wave_spawn_cooldown 
        
        elif self.no_enemies and self.spawn_wave_time <= pygame.time.get_ticks():  # Checking if it is time to spawn a new wave of enemies
            self.spawn_enemies()
            self.no_enemies = False


    def run(self):
        """
        Handles the way the game should loop aka function calls and all that
        """
        self.event_handler()
        self.draw()
        self.update()
        self.clock.tick(60)



if __name__ == "__main__":
    game = Game()
    while True:
        game.run()