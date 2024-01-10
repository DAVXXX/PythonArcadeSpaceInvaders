import arcade
import random
import json
import os

HIGH_SCORE_FILE = "high_scores.json"

# Set up constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Space Invaders"

# Set up player constants
PLAYER_SPEED = 5
PLAYER_RADIUS = 25

# Set up enemy constants
ENEMY_SPEED_X = 2
ENEMY_SPEED_Y = 10
ENEMY_RADIUS = 20
ENEMY_COUNT = 5
ENEMY_WAVE_COUNT = 5
ENEMY_PROJECTILE_SPEED = 3

# Set up bullet constants
BULLET_SPEED = 5
BULLET_RADIUS = 5

# Set up barrier constants
BARRIER_WIDTH = 50
BARRIER_HEIGHT = 30
BARRIER_COUNT = 3


def load_high_scores():
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    with open(HIGH_SCORE_FILE, "r") as file:
        return json.load(file)


def save_high_scores(high_scores):
    with open(HIGH_SCORE_FILE, "w") as file:
        json.dump(high_scores, file)


class GameOverView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.player_score = game_view.score
        self.high_scores = load_high_scores()
        self.initials = ["A", "A", "A"]
        self.initials_index = 0
        self.cursor_time = 0  # Timer for cursor blinking

    def save_high_score(self):
        # Convert initials list to string
        initials_str = "".join(self.initials)
        self.high_scores.append((self.player_score, initials_str))
        self.high_scores.sort(key=lambda x: x[0], reverse=True)
        self.high_scores = self.high_scores[:5]
        save_high_scores(self.high_scores)

    def on_draw(self):
        arcade.start_render()
        # ... [existing draw code for Game Over, Your Score, etc.]

        # Display initials with a cursor
        for i, letter in enumerate(self.initials):
            # Determine color; if current letter is being edited, make it red
            color = arcade.color.RED if i == self.initials_index and int(
                self.cursor_time) % 2 == 0 else arcade.color.WHITE
            letter_x_position = SCREEN_WIDTH / 2 - 15 + (i * 15)
            arcade.draw_text(letter, letter_x_position, SCREEN_HEIGHT / 2 - 50,
                             color, font_size=20, anchor_x="center")

        # Display High Scores
        arcade.draw_text("High Scores:", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        for i, score in enumerate(self.high_scores):
            text = f"{i + 1}. {score[1]}: {score[0]}"
            arcade.draw_text(text, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 130 - (i * 20),
                             arcade.color.WHITE, font_size=15, anchor_x="center")

    def on_key_press(self, key, _modifiers):

        # Handle arrow keys for initials
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN]:
            if key == arcade.key.LEFT:
                self.initials_index = max(0, self.initials_index - 1)
            elif key == arcade.key.RIGHT:
                self.initials_index = min(2, self.initials_index + 1)
            elif key == arcade.key.UP:
                self.initials[self.initials_index] = chr((ord(self.initials[self.initials_index]) - 65 + 1) % 26 + 65)
            elif key == arcade.key.DOWN:
                self.initials[self.initials_index] = chr((ord(self.initials[self.initials_index]) - 65 - 1) % 26 + 65)

        if key == arcade.key.ENTER:
            # Save high score and transition to StartView or another view
            self.save_high_score()
            start_view = StartView(self.high_scores)
            self.window.show_view(start_view)


class PowerUp(arcade.Sprite):
    def __init__(self, image_path, scale, speed):
        super().__init__(image_path, scale)
        self.speed = speed

    def update(self):
        self.center_y -= self.speed  # Decreases y position to make it fall


class StartView(arcade.View):
    def __init__(self, high_scores, player_score=None):
        super().__init__()
        self.high_scores = high_scores
        self.player_score = player_score

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Space Invaders", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to Play", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Press Q to Quit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

        # Draw High Scores
        if self.high_scores:
            arcade.draw_text("High Scores:", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150,
                             arcade.color.YELLOW, font_size=30, anchor_x="center")
            for i, score in enumerate(self.high_scores):
                score_text = f"{i + 1}. {score[1]} - {score[0]}"
                arcade.draw_text(score_text, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180 - (i * 30),
                                 arcade.color.WHITE, font_size=20, anchor_x="center")

    # Other methods (on_mouse_press, etc.)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = SpaceInvadersGame()
        game_view.setup()
        self.window.show_view(game_view)

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.Q:
            arcade.close_window()


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_draw(self):
        self.game_view.on_draw()
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                     SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                     arcade.color.BLACK + (200,))
        arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Press P to Resume", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Press Q to Quit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 25,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.P:
            self.window.show_view(self.game_view)
        elif key == arcade.key.Q:
            arcade.close_window()


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("images/player_ship.png", 0.1)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = 50
        self.visible = True  # Ensure the player starts as visible

    def toggle_visibility(self, delta_time):
        self.visible = not self.visible

    def update(self):
        self.center_x += self.change_x
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/enemy_ship.png", 0.1)
        self.center_x = x
        self.center_y = y
        self.change_x = ENEMY_SPEED_X
        self.speed_increase_factor = 1.3  # Define a factor to increase speed by, e.g., 5%

    def on_hit(self):
        self.scale = 1.2  # Temporarily increase size
        self.angle = 15  # Temporarily rotate
        arcade.schedule(self.reset_effect, 0.1)

    def reset_effect(self, delta_time):
        self.scale = 1.0
        self.angle = 0
        arcade.unschedule(self.reset_effect)

    def update(self):
        self.center_x += self.change_x
        if self.left <= 0 or self.right >= SCREEN_WIDTH:
            self.change_x *= -1  # Change direction

            # Move the enemy down after hitting a wall
            self.center_y -= ENEMY_SPEED_Y  # Adjust this value as needed

            self.increase_speed()  # Increase speed after bouncing

    def increase_speed(self):
        # Increase the speed by a factor
        new_speed = self.change_x * self.speed_increase_factor
        max_speed = 10  # Define a maximum speed limit
        if abs(new_speed) < max_speed:
            self.change_x = new_speed
        else:
            self.change_x = max_speed if new_speed > 0 else -max_speed


class EnemyProjectile(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/enemy_projectile.png", 1)
        self.center_x = x
        self.center_y = y

    def update(self):
        self.center_y -= ENEMY_PROJECTILE_SPEED


class Barrier(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/barrier.png", 1)
        self.center_x = x
        self.center_y = y
        self.health = 3  # Set the initial health of the barrier

    def update(self):
        if self.health == 2:
            self.texture = arcade.load_texture("images/barrier_damaged.png")
        elif self.health == 1:
            self.texture = arcade.load_texture("images/barrier_almost_destroyed.png")
        elif self.health <= 0:
            self.remove_from_sprite_lists()
        else:
            self.texture = arcade.load_texture("images/barrier.png")


class Bullet(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/bullet.png", 1)
        self.center_x = x
        self.center_y = y

    def update(self):
        self.center_y += BULLET_SPEED  # Change this line to move the bullet upwards


class SpaceInvadersGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.enemy_projectile_list = arcade.SpriteList()
        self.enemy_count = ENEMY_COUNT  # Initialize enemy count
        self.barrier_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.score = 0
        self.wave = 0
        self.boss = None
        self.boss_defeated = False
        self.high_scores = load_high_scores()
        self.game_over = False
        self.power_up_list = arcade.SpriteList()
        self.unlimited_shooting_enabled = False
        self.spawn_power_up()  # Ensure this is called in each frame
        self.power_up_list.update()
        self.power_up_duration = 0  # Duration of the unlimited shooting power-up
        self.emitters = []  # A list to store all active emitters

    def spawn_boss(self):
        # Check if it's time to spawn the boss
        if self.wave % 2 == 0 and not self.boss:
            self.boss = Boss()
            self.boss.center_x = SCREEN_WIDTH // 2
            self.boss.center_y = SCREEN_HEIGHT - 100

    def spawn_power_up(self):
        # Logic to spawn power-up at random intervals
        if random.random() < 0.001:  # Increased probability for testing
            power_up = PowerUp("images/green_power_up.png", 0.05, 2)  # Adjust scale and speed as needed
            power_up.center_x = random.randint(0, SCREEN_WIDTH)
            power_up.center_y = SCREEN_HEIGHT
            self.power_up_list.append(power_up)

    def setup(self):
        self.wave += 1
        self.enemy_count += 1  # Increase the enemy count by 1 with each wave
        self.spawn_boss()
        if not self.player_list:
            player = Player()
            self.player_list.append(player)

        self.enemy_list = arcade.SpriteList()
        for i in range(self.enemy_count):
            # Reset enemy position to the top of the screen
            enemy_y_position = SCREEN_HEIGHT - 50  # Adjust this value as needed
            enemy = Enemy((i + 1) * SCREEN_WIDTH // (self.enemy_count + 1), enemy_y_position)
            self.enemy_list.append(enemy)

        self.enemy_projectile_list = arcade.SpriteList()
        self.barrier_list = arcade.SpriteList()
        for i in range(BARRIER_COUNT):
            barrier = Barrier((i + 1) * SCREEN_WIDTH // (BARRIER_COUNT + 1), SCREEN_HEIGHT // 4)
            self.barrier_list.append(barrier)

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.enemy_list.draw()
        self.enemy_projectile_list.draw()
        self.barrier_list.draw()
        self.bullet_list.draw()
        self.power_up_list.draw()  # Draw power-ups

        for emitter in self.emitters:
            emitter.draw()

        if self.boss:
            self.boss.draw()  # Draw the boss if present

        # Draw the score
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 20, arcade.color.WHITE, 16)
        # Draw the wave counter
        arcade.draw_text(f"Wave: {self.wave}", SCREEN_WIDTH - 100, SCREEN_HEIGHT - 20, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.player_list.update()
        self.enemy_list.update()
        self.enemy_projectile_list.update()
        self.barrier_list.update()
        self.bullet_list.update()
        self.spawn_power_up()  # Call this every frame
        self.power_up_list.update()

        for emitter in self.emitters:
            emitter.update()
            if not emitter.alive:
                self.emitters.remove(emitter)

        # Update the boss if it's present
        if self.boss:
            self.boss.update()

            if self.boss and self.boss.health <= 0:
                self.boss.remove_from_sprite_lists()
                self.boss = None
                self.boss_defeated = True
                self.score += 20  # Or any score value for defeating the boss
            # Boss firing projectiles
            if random.random() < 0.01:  # Adjust the probability as needed
                boss_projectile = EnemyProjectile(self.boss.center_x, self.boss.center_y - 20)
                self.enemy_projectile_list.append(boss_projectile)

            # Update bullets and check for collisions
        for bullet in self.bullet_list:
            bullet.update()
            if bullet.top > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

            # Check for collisions with the boss
            if self.boss and arcade.check_for_collision(bullet, self.boss):
                bullet.remove_from_sprite_lists()
                self.boss.health -= 1
                if self.boss.health <= 0:
                    self.boss.remove_from_sprite_lists()
                    self.boss = None
                    self.boss_defeated = True
                    self.score += 5

            # Check for collisions with enemies
            hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            for enemy in hit_enemies:
                enemy.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                enemy.on_hit()
                self.score += 1

        # Check for collisions between enemies and player
        for enemy in self.enemy_list:
            if arcade.check_for_collision(enemy, self.player_list[0]):
                self.player_list[0].remove_from_sprite_lists()
                self.game_over = True
                game_over_view = GameOverView(self)
                self.window.show_view(game_over_view)
                break

        # Check for collisions between player and enemy projectiles
        for projectile in self.enemy_projectile_list:
            if arcade.check_for_collision(projectile, self.player_list[0]):
                self.game_over = True
                game_over_view = GameOverView(self)
                self.window.show_view(game_over_view)
                break

        # Check for collisions between enemy projectiles and barriers
        for projectile in self.enemy_projectile_list:
            hit_barriers = arcade.check_for_collision_with_list(projectile, self.barrier_list)
            for barrier in hit_barriers:
                projectile.remove_from_sprite_lists()
                barrier.health -= 1

        # Check for collisions between player bullets and barriers
        for bullet in self.bullet_list:
            hit_barriers = arcade.check_for_collision_with_list(bullet, self.barrier_list)
            for barrier in hit_barriers:
                bullet.remove_from_sprite_lists()
                barrier.health -= 1

        # Check if enemies are off-screen and remove them
        for enemy in self.enemy_list:
            if enemy.top < 0:
                enemy.remove_from_sprite_lists()

        # Check if all enemies are defeated to spawn a new wave
        if len(self.enemy_list) == 0:
            self.setup()

        # Randomly fire projectiles from enemies
        if random.random() < 0.005:
            for enemy in self.enemy_list:
                projectile = EnemyProjectile(enemy.center_x, enemy.center_y)
                self.enemy_projectile_list.append(projectile)

        # Safe power-up collision logic
        if self.player_list:  # Ensure player exists before checking collisions
            power_up_hit_list = arcade.check_for_collision_with_list(self.player_list[0], self.power_up_list)
            for power_up in power_up_hit_list:
                try:
                    power_up.remove_from_sprite_lists()
                    self.enable_unlimited_shooting()
                except Exception as e:
                    print(f"Error handling power-up collision: {e}")

    def enable_unlimited_shooting(self):
        self.unlimited_shooting_enabled = True
        arcade.schedule(self.player_list[0].toggle_visibility, 0.2)  # Flash player every 0.2 seconds
        arcade.schedule(self.disable_unlimited_shooting, 7)  # Disable power-up after 7 seconds

    def disable_unlimited_shooting(self, delta_time):
        self.unlimited_shooting_enabled = False
        arcade.unschedule(self.player_list[0].toggle_visibility)  # Stop flashing
        self.player_list[0].visible = True  # Make sure the player is visible

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player_list[0].change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player_list[0].change_x = PLAYER_SPEED
        elif key == arcade.key.SPACE:
            if len(self.bullet_list) < 2:
                bullet = Bullet(self.player_list[0].center_x, self.player_list[0].center_y)
                self.bullet_list.append(bullet)
        elif key == arcade.key.P:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)
        if self.game_over:
            return  # Disable input if game over
        if key == arcade.key.SPACE:
            if self.unlimited_shooting_enabled or len(self.bullet_list) < 2:
                bullet = Bullet(self.player_list[0].center_x, self.player_list[0].center_y)
                self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT and self.player_list[0].change_x < 0:
            self.player_list[0].change_x = 0
        elif key == arcade.key.RIGHT and self.player_list[0].change_x > 0:
            self.player_list[0].change_x = 0


class Boss(arcade.Sprite):
    def __init__(self):
        super().__init__("images/boss_ship.png", 0.1)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT - 100
        self.health = 5  # Correctly initialized
        self.change_x = ENEMY_SPEED_X * 1.8
        self.center_x += self.change_x
        self.speed_increase_factor = 1.3  # Define a factor to increase speed by, e.g., 5%

    def update(self):
        # Boss movement
        self.center_x += self.change_x
        if self.left < 0 or self.right > SCREEN_WIDTH:
            self.change_x *= -1  # Change direction at screen edges
            # Move the enemy down after hitting a wall
            self.center_y -= ENEMY_SPEED_Y  # Adjust this value as needed

            self.increase_speed()  # Increase speed after bouncing

    def increase_speed(self):
        # Increase the speed by a factor
        new_speed = self.change_x * self.speed_increase_factor
        max_speed = 10  # Define a maximum speed limit
        if abs(new_speed) < max_speed:
            self.change_x = new_speed
        else:
            self.change_x = max_speed if new_speed > 0 else -max_speed


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Load high scores before creating StartView
    high_scores = load_high_scores()

    start_view = StartView(high_scores)
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
