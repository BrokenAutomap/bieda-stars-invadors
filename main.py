import sys
import math
import numpy
import pygame
import time

pygame.init()


class GameObject:
    rect_dict = [
        "topleft", "top", "topright",
        "midleft", "center", "midright",
        "bottomleft", "bottom", "bottomright",
        "height", "width"]
    object_list = []
    collision_groups_all = {}
    smart_collision_groups = {}

    def __init__(
            self, name,
            position, max_speed, acceleration, resistance, mass, bounciness,
            object_picture, *collision_group_ids, **custom_hitbox):

        # Name, not used as of now.
        self.name = name
        self.object_list.append(self)  # Adding object to general class list

        # Position and movement information
        assert isinstance(position, list)
        self.position = position  # Object's position in format [x, y]
        self.speed = [0.0, 0.0]  # Sign is used to show direction.
        # For example -1 would mean one pixel up
        # on every frame (for coordinate space look to pygame)
        self.max_speed = max_speed  # Max object speed (absolute values)
        # in format [up, down, left, right].
        # It applies to speed across axis for now.
        # It makes object go faster when moving diagonally,
        # because speeds add up geometrically.
        # Use absolute values, format is [up, down, left, right].
        self.acceleration = acceleration  # For making move smoother.
        # Object actually speeds up over time instead of
        # accelerating suddenly. The acceleration is specific to the object.
        # Use absolute values for correct behavior, format is [up, down, left, right].
        self.resistance = resistance  # Object slows down after time
        # (main use for players, makes it easier to stop at the same time).
        # Use absolute values, format is [up, down, left, right].
        self.move_direction = [False, False, False, False]  # Indicates if "force" is
        # applied to the object, in other words if the player wants to move
        # format is [up, down, left, right]
        self.mass = mass  # Used in calculating collisions, works like in real life
        self.bounciness = bounciness  # Represents object's elasticity or just
        # how bouncy it is. The value is in range between 0 and 1.
        # For example if both colliding objects have bounciness 1 then the
        # collision will be fully elastic.

        # Object's picture and hitbox
        self.object_picture = object_picture
        self.object_rect = object_picture.get_rect(
            center=position, height=object_picture.get_height(),
            width=object_picture.get_width())

        self.collision_group_ids = collision_group_ids
        if not collision_group_ids:
            self.collision_group_ids = []
        # Objects in the same group collide.
        # collision_group as an *arg is a tuple, so an object can be in many groups.
        # It's an optional argument, lack of group
        # means that object never collides.

        # Below a nested collision group dictionary is initialized.
        # It's a general class data structure used for quick access
        # to specific data necessary to resolve all collisions.
        # The structure is as follows
        # {id of the specific group: dictionary containing the Game_object instances belonging to the group}
        #                                                     |
        #                                                     v
        #                            {Game_object (or child) instance: pygame.Rect instance}
        for group_id in self.collision_group_ids:
            group_dict = {self: self.object_rect}
            if group_id not in self.collision_groups_all.keys():
                self.collision_groups_all.update({group_id: group_dict})
            elif True:
                collision_group = self.collision_groups_all.get(group_id)
                collision_group.update(group_dict)

        # Normally object has the same sized hitbox
        # as its picture, but custom sizes are possible.
        # Take note that hitboxes are always rectangles.
        # Adding keywords (look for pygame.Rect or Game_object.rect_dict) on initialization
        # makes for custom hitboxes.
        # Hitbox can be also changed later using set_hitbox() method.
        # Section below is responsible for handling **kwargs keywords
        for keyword, value in custom_hitbox.items():
            if keyword in self.rect_dict:
                if isinstance(value, list):
                    command_value = "".join(map(str, value))
                elif True:
                    command_value = str(value)
                exec("self.object_rect." + keyword + " = " + command_value)

    def set_hitbox(self, **custom_hitbox):
        for keyword, value in custom_hitbox.items():
            if keyword in self.rect_dict:
                if isinstance(value, list):
                    command_value = "".join(map(str, value))
                elif True:
                    command_value = str(value)
                exec("self.object_rect." + keyword + " = " + command_value)

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
            self.speed[0] = math.copysign(
                abs(self.speed[0]) - self.resistance[0], self.speed[0])
        if abs(self.speed[1]) < self.resistance[1]:
            self.speed[1] = 0
        elif True:
            self.speed[1] = math.copysign(
                abs(self.speed[1]) - self.resistance[1], self.speed[1])

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
        self.position = [
            self.position[0] + self.speed[0], self.position[1] + self.speed[1]]
        self.object_rect.center = self.position

    def move_outside_collision(self, collided_object, relative_speed):
        # This functions moves out collided objects so that they are no longer overlapping.
        # It prevents collision clipping which shows itself with objects stuck in each other
        # when colliding in certain conditions.
        distance = {"x": abs(self.object_rect.center[0]-collided_object.object_rect.center[0]),
                    "y": abs(self.object_rect.center[1]-collided_object.object_rect.center[1])}
        # The actual distance between two object's on individual axes.
        max_correct_offset = {"x": (self.object_rect.width+collided_object.object_rect.width)/2+1,
                              "y": (self.object_rect.height+collided_object.object_rect.height)/2+1}
        # The offset in which objects don't intersect on both axes, calculated by considering their sizes.

        optimal_axis = max(distance, key=distance.get)  # Choosing the proper axis to offset the object.
        # Using the proper axis is essential for getting a seamless transition which is indicated
        # by the previous move and side on which the collision occurred.
        correct_offset = max_correct_offset.get(optimal_axis)-distance.get(optimal_axis)
        # correct_offset indicates the minimal offset needed to move object's out of the way.
        # Depending on the axis used an offset vector is returned with direction opposite to the
        # direction of relative_speed vector.
        if optimal_axis == "x":
            a = correct_offset / relative_speed[0]
            return [-relative_speed[0], -a*relative_speed[1]]
        elif optimal_axis == "y":
            a = correct_offset / relative_speed[1]
            return [-a*relative_speed[0], -relative_speed[1]]

    @classmethod
    def handle_collision(cls, object_1, object_2):

        # mean_bounciness is the average bounciness of two colliding objects
        mean_bounciness = (object_1.bounciness + object_2.bounciness) / 2
        # relative_speed is the relative speed between the colliding objects.
        # We choose the frame of reference in which object_2 is stationary
        relative_speed = (object_1.speed[0] - object_2.speed[0],
                          object_1.speed[1] - object_2.speed[1])
        # relative_momentum is a momentum of the only moving object in the frame of reference: object_2
        # At the same time it's the total momentum of a whole system.
        relative_momentum = [object_1.mass * relative_speed[0],  object_1.mass * relative_speed[1]]
        # min_transferred_momentum is the minimal momentum object_1 can transfer to object_2
        # It's the actual transferred momentum only when bounciness of both objects is 0.
        # Maximal transferred momentum is just the whole object_1 momentum.
        # So we don't need to calculate it again.
        min_transferred_momentum = (
            object_2.mass * relative_momentum[0]
            / (object_1.mass + object_2.mass),
            object_2.mass * relative_momentum[1]
            / (object_1.mass + object_2.mass))
        # transferred_momentum is the actual momentum transferred. It's in range
        # between minimal and maximal possible transfer, the actual amount is decided
        # by mean_bounciness (bounciness 1 indicates the maximal transfer, and bounciness 0
        # indicates minimal possible momentum transfer)
        transferred_momentum = (
            (relative_momentum[0] - min_transferred_momentum[0]) * mean_bounciness
            + min_transferred_momentum[0],
            (relative_momentum[1] - min_transferred_momentum[1]) * mean_bounciness
            + min_transferred_momentum[1],
        )
        # We assign final momentum to both objects
        self_momentum = (relative_momentum[0] - transferred_momentum[0],
                         relative_momentum[1] - transferred_momentum[1])
        collided_object_momentum = transferred_momentum
        # Based on the objects' masses and momentum we calculate their speed
        object_1.speed = [self_momentum[0] / object_1.mass + object_2.speed[0],
                          self_momentum[1] / object_1.mass + object_2.speed[1]]
        object_2.speed = [
            collided_object_momentum[0] / object_2.mass + object_2.speed[0],
            collided_object_momentum[1] / object_2.mass + object_2.speed[1]]
        # We move object_1 out of the object_2 to negate clipping effect
        offset_position = object_1.move_outside_collision(object_2, relative_speed)
        object_1.position = (offset_position[0]+object_1.object_rect.center[0],
                             offset_position[1]+object_1.object_rect.center[1])

    @classmethod
    def manage_movement(cls):  # Method used to efficiently manage movement and collisions (work in progress)
        # It works by checking if every object sharing the same collision group is in collision
        # and then lets handle_collision() method resolve the situation.
        # It tries to not call handle_collision() twice for the same collision.
        # The behaviour in three object collisions is untested and probably glitched
        # It also calls for object_move() method for every known object.
        copy_object_list = cls.object_list[:]
        for game_object in copy_object_list:
            every_group = {}
            for group_id in game_object.collision_group_ids:
                every_group.update(cls.collision_groups_all.get(group_id))
            every_group.pop(game_object)
            collision_list = game_object.object_rect.collidedictall(every_group, 1)
            for collision in collision_list:
                copy_object_list.remove(collision[0])
                cls.handle_collision(game_object, collision[0])
        for game_object in cls.object_list:
            game_object.move_object()


class Player(GameObject):  # Player class, health system to implement

    bullet_picture = []
    keywords = ["bullet_picture"]

    def __init__(
            self, name,
            position, max_speed, acceleration, resistance, mass, bounciness,
            object_picture, health, *collision_group, **custom_hitbox):
        super().__init__(
            name,
            position, max_speed, acceleration, resistance, mass, bounciness,
            object_picture, *collision_group, **custom_hitbox)
        self.health = health
        self.timer = time.time()

        for keyword, value in custom_hitbox.items():
            if keyword in self.keywords:
                if isinstance(value, pygame.Surface):
                    self.bullet_picture.append(value)


    @classmethod
    def control(cls, player_1, player_2):  # Method used to manage events used for player's control
        for event in pygame.event.get():
            print(cls.bullet_picture[0])
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player_1.move_direction[0] = True
                if event.key == pygame.K_s:
                    player_1.move_direction[1] = True
                if event.key == pygame.K_a:
                    player_1.move_direction[2] = True
                if event.key == pygame.K_d:
                    player_1.move_direction[3] = True

                if event.key == pygame.K_UP:
                    player_2.move_direction[0] = True
                if event.key == pygame.K_DOWN:
                    player_2.move_direction[1] = True
                if event.key == pygame.K_LEFT:
                    player_2.move_direction[2] = True
                if event.key == pygame.K_RIGHT:
                    player_2.move_direction[3] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    player_1.move_direction[0] = False
                if event.key == pygame.K_s:
                    player_1.move_direction[1] = False
                if event.key == pygame.K_a:
                    player_1.move_direction[2] = False
                if event.key == pygame.K_d:
                    player_1.move_direction[3] = False

                if event.key == pygame.K_UP:
                    player_2.move_direction[0] = False
                if event.key == pygame.K_DOWN:
                    player_2.move_direction[1] = False
                if event.key == pygame.K_LEFT:
                    player_2.move_direction[2] = False
                if event.key == pygame.K_RIGHT:
                    player_2.move_direction[3] = False

                if time.time() - player_1.timer > 2:

                    if event.key == pygame.K_SPACE:
                        Bullet.summon_bullet(player_1.position, cls.bullet_picture[0])
                        position = [player_1.position[0] + 25, player_1.position[1]]
                        Bullet.summon_bullet(position, cls.bullet_picture[0])
                        player_1.timer = time.time()

                if time.time() - player_2.timer > 2:
                    if event.key == pygame.K_RCTRL:
                        bullet = Bullet.summon_bullet(player_2.position, cls.bullet_picture[0])
                        bullet.speed = [0, 10]
                        position = [player_2.position[0] + 25, player_2.position[1]]
                        bullet = Bullet.summon_bullet(position, cls.bullet_picture[0])
                        bullet.speed = [0, 10]
                        player_2.timer = time.time()
                # if event.key == pygame.K_SPACE:
                #     Bullet.summon_bullet(player_1.position)
                #     position = [player_1.position[0] + 25, player_1.position[1]]
                #     Bullet.summon_bullet(position)


class Bullet(GameObject):

    object_list = []

    def __init__(
            self, name,
            position, max_speed, acceleration, resistance,
            object_picture, health):
        super().__init__(
            name, position, max_speed,
            acceleration, resistance,
            object_picture)
        self.speed = [0, -10]
        self.health = health
        self.object_list.append(self)

    @classmethod
    def summon_bullet(cls, position, picture):
        return cls("player_1", position,
                   (999, 999, 999, 999), (0.1, 0.1, 0.1, 0.1),
                   (0, 0), picture, 100)


def mirrored_vector(normal, vector):
    beta = math.acos(
        (numpy.dot(normal, vector))
        / (numpy.sqrt(numpy.dot(normal, normal))
           * numpy.sqrt(numpy.dot(vector, vector))))
    return [vector[0] * math.cos(2 * beta) - vector[1] * math.sin(2 * beta),
            vector[0] * math.sin(2 * beta) - vector[1] * math.cos(2 * beta)]


size = width, height = 800, 640  # Temporary solution, display resolution
# Initializing display
screen = pygame.display.set_mode(size)
# Loading pictures
player_picture = pygame.image.load("g3.png").convert_alpha()
picture = pygame.transform.scale(player_picture, (50, 50))
bullet_picture = pygame.image.load("arrow.png").convert_alpha()
picture_bullet_picture = pygame.transform.scale(bullet_picture, (30, 30))

# Creating Player instances
player_1 = Player(
    "player_1", [300, 300], [0.5, 0.5, 0.5, 0.5], [0.01, 0.01, 0.01, 0.01],
    [0.0, 0.0], 1, 1, picture, 100, 1, bullet_picture=picture_bullet_picture)
player_2 = Player(
    "player_1", [100, 100], [0.5, 0.5, 0.5, 0.5], [0.01, 0.01, 0.01, 0.01],
    [0.0, 0.0], 1, 1, picture, 100, 1, bullet_picture=picture_bullet_picture)
test_object = GameObject(
    "object", [400, 400], [3, 3, 3, 3], [0.1, 0.1, 0.1, 0.1],
    [0, 0], 1, 0.5, picture, 100, 1)

c = pygame.time.Clock()

while True:
    Player.control(player_1, player_2)
    """c.tick() #Uncomment for fps counter
    print("fps ", c.get_fps())
    """
    screen.fill((0, 0, 0))  # After each frame screen is being emptied
    GameObject.manage_movement()
    screen.blit(player_1.object_picture, player_1.object_rect)  # Displaying player
    screen.blit(player_2.object_picture, player_2.object_rect)
    pygame.display.update()  # Updating display
    pygame.time.wait(1)  # Temporary solution, proper time management needed
