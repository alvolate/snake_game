import pygame, sys, time, random
from pygame.surfarray import array3d
from pygame import display

import numpy as np 
from gymnasium import error,spaces, utils
from gymnasium.utils import seeding
import gymnasium as gym

BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
RED = pygame.Color(255,0,0)
GREEN = pygame.Color(0,255,0)


class SnakeEnv(gym.Env):
    
    metadata = {'render_modes':['human']}
    
    def __init__(self,render_mode = None):

        self.frame_size_x = 200
        self.frame_size_y = 200
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_x))
        
        self.action_space= spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(self.frame_size_x,self.frame_size_x,3), dtype=np.float64)
        
        
        #reset the game
        self.reset()
        self.STEP_LIMIT = 1000
        self.sleep = 0
        self.score = 0
        
        self.done = False
        self.truncated =False
        
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        
    def reset(self):
        
        self.game_window.fill(BLACK)
        self.snake_pos = [100,50]
        self.snake_body = [[100,50], [100-10,50], [100-20,50]]
        self.food_pos = self.spawn_food()
        self.food_spawn = True
        
        self.direction = 2
        self.action = self.direction
        
        self.score = 0
        self.steps = 0
        
        img = array3d(display.get_surface())
        img = np.swapaxes(img,0,1)
        info = {"score": self.score}
        
        self.update_game_state()
        if self.render_mode == "human":
            self.render()
        
        return img,info
        
    @staticmethod
    def change_direction(action,direction):
        if action ==0 and direction != 1:
            direction = 0
        if action ==1 and direction != 0:
            direction = 0
        if action ==2 and direction != 3:
            direction = 2
        if action ==3 and direction != 2:
            direction = 3
            
        return direction
    
    @staticmethod
    def move(direction,snake_pos):
        if direction == 0:
            snake_pos[1] -= 10
        if direction == 1:
            snake_pos[1] += 10
        if direction == 2:
            snake_pos[0] += 10
        if direction == 3:
            snake_pos[0] -= 10
            
        return snake_pos    
        
        
    def spawn_food(self):
        return [random.randrange(1,(self.frame_size_x//10))*10, random.randrange(1,(self.frame_size_y//10))*10 ]
    
    def eat(self):
        return self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]
    
    def step(self,action):
        #if self.done or self.truncated:
            #print("game finished")
        
        scoreholder = self.score
        self.direction = SnakeEnv.change_direction(action,self.direction)
        self.snake_pos = SnakeEnv.move(self.direction,self.snake_pos)
        self.snake_body.insert(0,list(self.snake_pos))
        self.steps+=1
        reward = self.food_handler()
        
        self.update_game_state()
        
        reward, done = self.game_over(reward)
        self.done= done
        
        truncated = 1 if self.score> self.STEP_LIMIT else 0
        self.truncated= truncated
        
        img = self.get_image_array_from_game()
        
        info = {'score':self.score}
        
        time.sleep(self.sleep)
        
        if self.render_mode == "human":
            self.render()
        
        return img,reward, done, truncated, info
        
        
    def get_image_array_from_game(self):
        img = array3d(display.get_surface())
        img = np.swapaxes(img,0,1)
        return img
    
    def food_handler(self):
        if self.eat():
            self.score += 1
            reward =1
            self.food_spawn=False
        else:
            self.snake_body.pop()
            reward = 0
            
        if not self.food_spawn:
            self.food_pos = self.spawn_food()
        self.food_spawn= True
        
        return reward
        
    def update_game_state(self):
        #Drawing the snake
        self.game_window.fill(BLACK)
        for pos in self.snake_body:
            pygame.draw.rect(self.game_window, GREEN, pygame.Rect(pos[0],pos[1],10,10))


        #Drawing of food
        pygame.draw.rect(self.game_window, WHITE, pygame.Rect(self.food_pos[0],self.food_pos[1],10,10))
        
    def game_over(self,reward):
        #TOUCH BOX
        if self.snake_pos[0] < 0 or self.snake_pos[0]> self.frame_size_x-10:
            return -1, True
        if self.snake_pos[1] < 0 or self.snake_pos[1]> self.frame_size_y-10:
            return -1, True
            
        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                return -1, True
            
    
        return reward , False
        
        #TOUCH OWN BODY
    
    def render(self):
        display.update()
        
    def close(self):
        if self.render_mode == "human":
            pygame.display.quit()
            pygame.quit()
            self._renderer = None
        super().close()
