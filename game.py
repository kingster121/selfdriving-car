import pygame
import math


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


def rotateRect(pt1, pt2, pt3, pt4, angle):
    pt_center = Point((pt1.x + pt3.x) / 2, (pt1.y + pt3.y) / 2)

    pt1 = rotate(pt_center, pt1, angle)
    pt2 = rotate(pt_center, pt2, angle)
    pt3 = rotate(pt_center, pt3, angle)
    pt4 = rotate(pt_center, pt4, angle)

    return pt1, pt2, pt3, pt4


# pygame setup
pygame.init()
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

# Loading up spirtes
car_image = pygame.image.load("./images/car.png").convert()
car_rect = car_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# In game params
STEER_SPEED = math.radians(2)  # Steering speed, radian
car_angle = 0  # Initial angle, radian

CAR_ACCELERATION = 0.25
car_speed = 0  # Initial speed
max_speed = 5  # Maximum speed

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Logic
    keys = pygame.key.get_pressed()

    # Steering control
    if keys[pygame.K_a]:
        car_angle += STEER_SPEED
    if keys[pygame.K_d]:
        car_angle += 2 * math.pi - STEER_SPEED
    car_angle = car_angle % (2 * math.pi)

    # Acceleration control
    if keys[pygame.K_w]:
        car_speed += CAR_ACCELERATION
        if car_speed > max_speed:
            car_speed = max_speed
    if keys[pygame.K_s]:
        car_speed -= CAR_ACCELERATION
        if car_speed < -max_speed:
            car_speed = -max_speed

    # Update car position based on speed and angle
    car_dx = math.cos(car_angle) * car_speed
    car_dy = -math.sin(car_angle) * car_speed
    car_rect.move_ip(car_dx, car_dy)

    # Rendering
    screen.fill((0, 0, 0))
    rotated_car = pygame.transform.rotate(car_image, math.degrees(car_angle))
    screen.blit(rotated_car, car_rect)

    # Print game info on screen
    text_font = pygame.font.SysFont("Arial", 20)
    # Steering
    text_img = text_font.render(f"Steering angle: {car_angle}", True, (255, 255, 255))
    screen.blit(text_img, (600, 50))
    # Velocity
    text_img = text_font.render(f"dx: {car_dx} dy: {car_dy}", True, (255, 255, 255))
    screen.blit(text_img, (0, 50))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
