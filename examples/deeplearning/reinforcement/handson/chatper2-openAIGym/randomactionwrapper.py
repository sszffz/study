import random
from typing import TypeVar

import gym
from gym import ActionWrapper


Action = TypeVar("Action")


class RandomActionWrapper(ActionWrapper):

    def __init__(self, env, epsilon=0.1):
        super().__init__(env)
        self.epsilon = epsilon

    def action(self, action: Action) -> Action:
        if random.random() < self.epsilon:
            print("Random!")
            return self.env.action_space.sample()
        else:
            return action

    def reverse_action(self, action):
        pass


if __name__ == "__main__":
    env = RandomActionWrapper(gym.make("CartPole-v0"))
    env = gym.wrappers.Monitor(env, "recording")
    env.reset()

    total_reward = 0

    while True:
        obs, reward, done, _ = env.step(0)
        total_reward += reward
        if done:
            break

    print("Total reward: ", total_reward)



