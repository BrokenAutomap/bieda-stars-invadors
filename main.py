import sys
import math

import pygame

pygame.init()


class GameObject:
    def __init__(
            self, object_id, name,
            position, max_speed, acceleration, resistance,
            object_picture):

        # Naming, might come as unnecessary
        self.object_id = object_id
        self.name = name

        # Position and movement information
        assert isinstance(position, list)
        self.position = position  # Object's position in format [x, y]
        self.speed = [0.0, 0.0]  # Sign is used to show direction.
        # For example -1 would mean one pixel up on every tick (for coordinate space look to pygame)
        self.max_speed = max_speed  # Max object speed (absolute values)
        # in format (up, down, left, right). It applies to speed across axis for now.
        # It makes object go faster when moving diagonally,
        # because speeds add up geometrically.
        # Use absolute values, format is (up, down, left, right).
        self.acceleration = acceleration  # For making move smoother.
        # Object actually speeds up over time instead of
        # accelerating suddenly. The acceleration is specific to the object.
        # Use absolute values for correct behavior, format is (up, down, left, right).
        self.resistance = resistance  # Object slows down after time
        # (main use for players, makes it easier to stop at the same time).
        # Use absolute values, format is (up, down, left, right).
        self.move_direction = [False, False, False, False]  # Indicates if "force" is
        # applied to the object, in other words if the player wants to move
        # format is [up, down, left, right]

        # Object's picture and hitbox
        self.object_picture = object_picture
        self.object_rect = object_picture.get_rect(center=position)

    def move_object(self):  # Method for moving the object.
        # Should be updated regularly to maintain behavior.

        # This section is responsible for accelerating when we want it.
        if self.move_direction[0]:
            self.speed[1] -= self.acceleration[0]
        if self.move_direction[1]:
            self.speed[1] += self.acceleration[1]
        if self.move_direction[2]:
            self.speed[0] -= self.acceleration[2]
        if self.move_direction[3]:
            self.speed[0] += self.acceleration[3]

        # This section is responsible for applying resistance.
        if abs(self.speed[0]) < self.resistance[0]:
            self.speed[0] = 0
        elif True:
            self.speed[0] = math.copysign(abs(self.speed[0])-self.resistance[0], self.speed[0])
        if abs(self.speed[1]) < self.resistance[1]:
            self.speed[1] = 0
        elif True:
            self.speed[1] = math.copysign(abs(self.speed[1]) - self.resistance[1], self.speed[1])

        # This section is responsible for constraining speed
        if self.speed[1] < -self.max_speed[0]:
            self.speed[1] = -self.max_speed[0]
        elif self.speed[1] > self.max_speed[1]:
            self.speed[1] = self.max_speed[1]
        if self.speed[0] < -self.max_speed[2]:
            self.speed[0] = -self.max_speed[2]
        elif self.speed[0] > self.max_speed[3]:
            self.speed[0] = self.max_speed[3]

        # After calculations we update object's position
        self.position = [self.position[0]+self.speed[0], self.position[1]+self.speed[1]]


class Player(GameObject):  # Player class, health system to implement
    def __init__(
            self, object_id, name,
            position, max_speed, acceleration, resistance,
            object_picture, health):
        super().__init__(
            object_id, name,
            position, max_speed, acceleration, resistance,
            object_picture)
        self.health = health

    def control(self):  # Method used to manage events used for player's control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.move_direction[0] = True
                if event.key == pygame.K_s:
                    self.move_direction[1] = True
                if event.key == pygame.K_a:
                    self.move_direction[2] = True
                if event.key == pygame.K_d:
                    self.move_direction[3] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.move_direction[0] = False
                if event.key == pygame.K_s:
                    self.move_direction[1] = False
                if event.key == pygame.K_a:
                    self.move_direction[2] = False
                if event.key == pygame.K_d:
                    self.move_direction[3] = False


size = width, height = 800, 640  # Temporary solution, display resolution
# Initializing display
screen = pygame.display.set_mode(size)
# Loading pictures
player_picture = pygame.image.load("g3.png").convert_alpha()
picture = pygame.transform.scale(player_picture, (50, 50))

# Creating Player instances
player_1 = Player(0, "player_1", [300, 300], (3, 3, 3, 3), (0.1, 0.1, 0.1, 0.1), (0.05, 0.05), picture, 100)


while True:
    player_1.control()
    print(player_1.speed, player_1.position)
    screen.fill((0, 0, 0))  # After each frame screen is being emptied
    player_1.move_object()  # Updating player's movement
    screen.blit(player_1.object_picture, player_1.position)  # Displaying player
    pygame.display.update()  # Updating display
    pygame.time.wait(10)  # Temporary solution, proper time management needed
