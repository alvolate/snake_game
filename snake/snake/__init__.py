from gymnasium.envs.registration import register

from snake.envs.snake_env import SnakeEnv


register(
    id="snake-v0",
    entry_point="snake.envs:SnakeEnv"
)
