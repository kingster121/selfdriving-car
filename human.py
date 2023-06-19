# Allows human to play the game
import pygame

from game import RacingEnv


game = RacingEnv()
game.reset()
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    keys = pygame.key.get_pressed()
    new_state, reward, done = game.step(keys)
    game.render(keys)
