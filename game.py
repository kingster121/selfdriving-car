import pygame
import numpy as np
import math
from walls import Wall, get_walls
from goals import Goal, get_goals

# Rewards
GOAL_REWARD = 1
PENALTY = -1


def distance(pt1, pt2):
    return ((pt1.x - pt2.x) ** 2 + (pt1.y - pt2.y) ** 2) ** 0.5


def rotate(origin, point, angle):
    qx = (
        origin.x
        + math.cos(angle) * (point.x - origin.x)
        - math.sin(angle) * (point.y - origin.y)
    )
    qy = (
        origin.y
        + math.sin(angle) * (point.x - origin.x)
        + math.cos(angle) * (point.y - origin.y)
    )
    q = Point(qx, qy)
    return q


def rotate_rect(pt1, pt2, pt3, pt4, angle):
    pt_center = Point((pt1.x + pt3.x) / 2, (pt1.y + pt3.y) / 2)

    pt1 = rotate(pt_center, pt1, angle)
    pt2 = rotate(pt_center, pt2, angle)
    pt3 = rotate(pt_center, pt3, angle)
    pt4 = rotate(pt_center, pt4, angle)

    return pt1, pt2, pt3, pt4


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, pt1, pt2):
        self.pt1 = Point(pt1.x, pt1.y)
        self.pt2 = Point(pt2.x, pt2.y)


class Ray:
    def __init__(self,x,y,angle):
        self.x = x
        self.y = y
        self.angle = angle

    def cast(self, wall):
        x1 = wall.x1 
        y1 = wall.y1
        x2 = wall.x2
        y2 = wall.y2

        vec = rotate(Point(0,0), Point(0,-1000), self.angle)
        
        x3 = self.x
        y3 = self.y
        x4 = self.x + vec.x
        y4 = self.y + vec.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            
        if(den == 0):
            den = 0
        else:
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

            if t > 0 and t < 1 and u < 1 and u > 0:
                pt = Point(math.floor(x1 + t * (x2 - x1)), math.floor(y1 + t * (y2 - y1)))
                return(pt)


class Car:
    def __init__(self, x, y):
        # Position and size of car
        self.pt = Point(x, y)
        self.x = x
        self.y = y
        self.width = 14
        self.height = 30

        # Velocity and acceleration
        self.dvel = 0.5
        self._vel = 0
        self.velX = 0
        self.velY = 0
        self.maxvel = 5  # Max velocity

        self.points = 0

        # Angle
        self.angle = math.radians(0)
        self.desired_angle = self.angle

        # Corners of car, doesn't rotate
        self.pt1 = Point(
            self.pt.x - self.width / 2, self.pt.y - self.height / 2
        )  # Bottom left
        self.pt2 = Point(
            self.pt.x + self.width / 2, self.pt.y - self.height / 2
        )  # Bottom right
        self.pt3 = Point(
            self.pt.x + self.width / 2, self.pt.y + self.height / 2
        )  # Top right
        self.pt4 = Point(
            self.pt.x - self.width / 2, self.pt.y + self.height / 2
        )  # Top left

        # Corners of car, allows for rotation
        self.p1, self.p2, self.p3, self.p4 = self.pt1, self.pt2, self.pt3, self.pt4

        # Sprite
        self.original_image = pygame.image.load("./images/car.png").convert()
        self.image = self.original_image  # Refernce to the original image
        self.image.set_colorkey(
            (0, 0, 0)
        )  # Converts the white background to transparent
        self.rect = self.image.get_rect(center=(x, y))

    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, value):
        self._vel = max(-self.maxvel, min(value, self.maxvel))

    def action(self, keys):
        """keys = pygame.key.get_pressed() when human play
        keys = 0 or 1 or 2 or 3 when machine play"""

        print(type(keys), keys)
        # Machine 
        if isinstance(keys, int) or isinstance(keys, np.int64):
            if keys == 0:
              self.accelerate(-self.dvel)
            if keys == 1:
                self.accelerate(self.dvel)
            if keys == 2:
                self.turn(-1)
            if keys == 3:
                self.turn(1)

        # Human
        else:
            if keys[pygame.K_w]:
                self.accelerate(-self.dvel)
            if keys[pygame.K_s]:
                self.accelerate(self.dvel)
            if keys[pygame.K_d]:
                self.turn(-1)
            if keys[pygame.K_a]:
                self.turn(1)

    def accelerate(self, dvel):
        self.vel += dvel

    def turn(self, dir):
        self.desired_angle += dir * math.radians(5)

    def update(self):
        self.angle = self.desired_angle

        # Velocity
        velocity = rotate(Point(0, 0), Point(0, self.vel), -self.angle)
        self.velX, self.velY = velocity.x, velocity.y

        # Position
        self.x += self.velX
        self.y += self.velY
        self.rect.center = self.x, self.y

        # Corners
        self.pt1 = Point(self.pt1.x + self.velX, self.pt1.y + self.velY)
        self.pt2 = Point(self.pt2.x + self.velX, self.pt2.y + self.velY)
        self.pt3 = Point(self.pt3.x + self.velX, self.pt3.y + self.velY)
        self.pt4 = Point(self.pt4.x + self.velX, self.pt4.y + self.velY)
        self.p1, self.p2, self.p3, self.p4 = rotate_rect(
            self.pt1,
            self.pt2,
            self.pt3,
            self.pt4,
            self.desired_angle,
        )

        # Rotate image
        self.image = pygame.transform.rotate(
            self.original_image, (math.degrees(self.desired_angle) + 90)
        )
        x, y = self.rect.center  # Get current center
        self.rect = self.image.get_rect(
            center=(x, y)
        )  # Replace old rect with new rect'

    def cast(self, walls):

        ray1 = Ray(self.x, self.y, self.desired_angle)
        ray2 = Ray(self.x, self.y, self.desired_angle - math.radians(30))
        ray3 = Ray(self.x, self.y, self.desired_angle + math.radians(30))
        ray4 = Ray(self.x, self.y, self.desired_angle + math.radians(45))
        ray5 = Ray(self.x, self.y, self.desired_angle - math.radians(45))
        ray6 = Ray(self.x, self.y, self.desired_angle + math.radians(90))
        ray7 = Ray(self.x, self.y, self.desired_angle - math.radians(90))
        ray8 = Ray(self.x, self.y, self.desired_angle + math.radians(180))

        ray9 = Ray(self.x, self.y, self.desired_angle + math.radians(10))
        ray10 = Ray(self.x, self.y, self.desired_angle - math.radians(10))
        ray11 = Ray(self.x, self.y, self.desired_angle + math.radians(135))
        ray12 = Ray(self.x, self.y, self.desired_angle - math.radians(135))
        ray13 = Ray(self.x, self.y, self.desired_angle + math.radians(20))
        ray14 = Ray(self.x, self.y, self.desired_angle - math.radians(20))

        ray15 = Ray(self.p1.x,self.p1.y, self.desired_angle + math.radians(90))
        ray16 = Ray(self.p2.x,self.p2.y, self.desired_angle - math.radians(90))

        ray17 = Ray(self.p1.x,self.p1.y, self.desired_angle + math.radians(0))
        ray18 = Ray(self.p2.x,self.p2.y, self.desired_angle - math.radians(0))

        self.rays = []
        self.rays.append(ray1)
        self.rays.append(ray2)
        self.rays.append(ray3)
        self.rays.append(ray4)
        self.rays.append(ray5)
        self.rays.append(ray6)
        self.rays.append(ray7)
        self.rays.append(ray8)

        self.rays.append(ray9)
        self.rays.append(ray10)
        self.rays.append(ray11)
        self.rays.append(ray12)
        self.rays.append(ray13)
        self.rays.append(ray14)

        self.rays.append(ray15)
        self.rays.append(ray16)

        self.rays.append(ray17)
        self.rays.append(ray18)


        observations = []
        self.closestRays = []

        for ray in self.rays:
            closest = None #myPoint(0,0)
            record = math.inf
            for wall in walls:
                pt = ray.cast(wall)
                if pt:
                    dist = distance(Point(self.x, self.y),pt)
                    if dist < record:
                        record = dist
                        closest = pt

            if closest: 
                #append distance for current ray 
                self.closestRays.append(closest)
                observations.append(record)
               
            else:
                observations.append(1000)

        for i in range(len(observations)):
            #invert observation values 0 is far away 1 is close
            observations[i] = ((1000 - observations[i]) / 1000)

        observations.append(self.vel / self.maxvel)
        return observations

    def collision(self, wall):
        line1 = Line(self.p1, self.p2)
        line2 = Line(self.p2, self.p3)
        line3 = Line(self.p3, self.p4)
        line4 = Line(self.p4, self.p1)

        x1 = wall.x1
        y1 = wall.y1
        x2 = wall.x2
        y2 = wall.y2

        lines = []
        lines.append(line1)
        lines.append(line2)
        lines.append(line3)
        lines.append(line4)

        for li in lines:
            x3 = li.pt1.x
            y3 = li.pt1.y
            x4 = li.pt2.x
            y4 = li.pt2.y

            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            if den == 0:
                den = 0
            else:
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

                if t > 0 and t < 1 and u < 1 and u > 0:
                    return True

        return False

    def score(self, goal):
        line1 = Line(self.p1, self.p3)

        vec = rotate(Point(0, 0), Point(0, -50), self.angle)
        line1 = Line(Point(self.x, self.y), Point(self.x + vec.x, self.y + vec.y))

        x1 = goal.x1
        y1 = goal.y1
        x2 = goal.x2
        y2 = goal.y2

        x3 = line1.pt1.x
        y3 = line1.pt1.y
        x4 = line1.pt2.x
        y4 = line1.pt2.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if den == 0:
            den = 0
        else:
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

            if t > 0 and t < 1 and u < 1 and u > 0:
                pt = math.floor(x1 + t * (x2 - x1)), math.floor(y1 + t * (y2 - y1))

                d = distance(Point(self.x, self.y), Point(pt[0], pt[1]))
                if d < 20:
                    # pygame.draw.circle(win, (0,255,0), pt, 5)
                    self.points += GOAL_REWARD
                    return True

        return False

    def draw(self, win):
        win.blit(self.image, self.rect)


class RacingEnv:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)

        # Config
        self.width = 1000
        self.height = 600
        self.fps = 120
        self.history = []

        # Params
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Selfdriving Car")
        self.back_image = pygame.image.load("./images/track.png").convert()
        self.back_rect = self.back_image.get_rect()

        # In-game stats
        self.game_reward = 0  # For the AI, mini-goals
        self.score = 0  # Actual score

        self.reset()

    def reset(self):
        self.screen.fill((0, 0, 0))

        self.car = Car(50, 300)
        self.walls = get_walls()
        self.goals = get_goals()
        self.game_reward = 0

    def step(self, keys):
        done = False
        print("here", keys)
        self.car.action(keys)
        self.car.update()
        reward = 0

        # Checks if car passed goals and/or scores
        index = 0
        for index, goal in enumerate(self.goals):
            # print(goal)
            if goal.isactiv:
                if self.car.score(goal):
                    goal.isactiv = False
                    self.goals[index + 1].isactiv = True
                    reward += GOAL_REWARD

        # Checks if car crashed into wall
        for wall in self.walls:
            if self.car.collision(wall):
                reward += PENALTY
                done = True

        new_state = self.car.cast(self.walls)
        #normalize states
        if done:
            new_state = None

        return new_state, reward, done

    def render(self, keys):
        DRAW_WALLS = True
        DRAW_GOALS = True
        DRAW_RAYS = False

        pygame.time.delay(10)
        self.clock = pygame.time.Clock()

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.back_image, self.back_rect)

        if DRAW_WALLS:
            for wall in self.walls:
                wall.draw(self.screen)

        if DRAW_GOALS:
            for goal in self.goals:
                goal.draw(self.screen)

        self.car.draw(self.screen)

        if DRAW_RAYS:
            i = 0
            for pt in self.car.closestRays:
                pygame.draw.circle(self.screen, (0,0,255), (pt.x, pt.y), 5)
                i += 1
                if i < 15:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.x, self.car.y), (pt.x, pt.y), 1)
                elif i >=15 and i < 17:
                    pygame.draw.line(self.screen, (255,255,255), ((self.car.p1.x + self.car.p2.x)/2, (self.car.p1.y + self.car.p2.y)/2), (pt.x, pt.y), 1)
                elif i == 17:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.p1.x , self.car.p1.y ), (pt.x, pt.y), 1)
                else:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.p2.x, self.car.p2.y), (pt.x, pt.y), 1)


        # Render keys input WASD
        pygame.draw.rect(self.screen, (255, 255, 255), (800, 100, 40, 40), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (850, 100, 40, 40), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (900, 100, 40, 40), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (850, 50, 40, 40), 2)

        # Machine
        if isinstance(keys, int) or isinstance(keys, np.int64):
            if keys == 0:
                pygame.draw.rect(self.screen, (0, 255, 0), (850, 50, 40, 40))
            if keys == 1:
                pygame.draw.rect(self.screen, (255, 255, 255), (850, 100, 40, 40))
            if keys == 2 :
                pygame.draw.rect(self.screen, (255, 255, 255), (900, 100, 40, 40))
            if keys == 3:
                pygame.draw.rect(self.screen, (255, 255, 255), (800, 100, 40, 40))

        # Human
        else:
            if keys[pygame.K_w]:
                pygame.draw.rect(self.screen, (0, 255, 0), (850, 50, 40, 40))
            if keys[pygame.K_s]:
                pygame.draw.rect(self.screen, (255, 255, 255), (850, 100, 40, 40))
            if keys[pygame.K_d]:
                pygame.draw.rect(self.screen, (255, 255, 255), (900, 100, 40, 40))
            if keys[pygame.K_a]:
                pygame.draw.rect(self.screen, (255, 255, 255), (800, 100, 40, 40))

        # Scores
        text_surface = self.font.render(
            f"Points {self.car.points}", True, pygame.Color("green")
        )
        self.screen.blit(text_surface, dest=(0, 0))

        # Speed
        text_surface = self.font.render(
            f"Speed {self.car.vel*-1}", True, pygame.Color("green")
        )
        self.screen.blit(text_surface, dest=(800, 0))

        self.clock.tick(self.fps)
        pygame.display.update()

    def close(self):
        pygame.quit()
