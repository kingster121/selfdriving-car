import game
import pygame
import numpy as np
from ddqn_keras import DDQNAgent
from collections import deque
import random, math

TOTAL_GAMETIME = 1000 # Max game time for one episode
N_EPISODES = 10000
REPLACE_TARGET = 50 

game = game.RacingEnv()
game.fps = 60

GameTime = 0 
GameHistory = []
renderFlag = True

ddqn_agent = DDQNAgent(alpha=0.0005, gamma=0.99, n_actions=5, epsilon=1.00, epsilon_end=0.10, epsilon_dec=0.9995, replace_target= REPLACE_TARGET, batch_size=512, input_dims=19)

# if you want to load the existing model uncomment this line.
# careful an existing model might be overwritten
ddqn_agent.load_model()

ddqn_scores = []
eps_history = []

def run():
        
        game.reset() #reset env 

        done = False
        score = 0
        counter = 0
        
        observation_, reward, done = game.step(0)
        observation = np.array(observation_)

        gtime = 0 # set game time back to 0
        
        renderFlag = True # if you want to render every episode set to true

        while not done:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    return

            action = ddqn_agent.choose_action(observation)
            observation_, reward, done = game.step(action)
            observation_ = np.array(observation_)

            ddqn_agent.remember(observation, action, reward, observation_, int(done))
            observation = observation_
            ddqn_agent.learn()
            
            gtime += 1

            if gtime >= TOTAL_GAMETIME:
                done = True

            if renderFlag:
                game.render(action)

run()        