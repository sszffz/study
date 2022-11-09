import random
from typing import List

from gym import Env, Space


class Environment:
    """
    Define the whole environment. Theoretically, environment knows everything.
    But agent needs to figure out the best policy
    """

    def __init__(self):
        self.steps_left = 10

    # noinspection PyMethodMayBeStatic
    def get_observation(self) -> List[float]:
        return [0.0, 0.0, 0.0]

    # noinspection PyMethodMayBeStatic
    def get_actions(self) -> List[int]:
        """
        return all possible actions that agent can take
        :return:
        """
        return [0, 1]

    def is_done(self) -> bool:
        """
        test whether an episode ends or not
        :return:
        """
        return self.steps_left == 0

    def action(self, action: int) -> float:
        """
        It is the core of RL. It gets an action from agent, and then return reward
        :param action:
        :return:
        """
        if self.is_done():
            raise Exception("Game is over")

        self.steps_left -= 1
        return random.random()


class Agent:
    """
    implement policy. Each agent has its own policy which is implemented in the
    method "step"
    """

    def __init__(self):
        self.total_reward = 0.0

    def step(self, env: Environment):
        current_obs = env.get_observation()
        actions = env.get_actions()
        reward = env.action(random.choice(actions))
        self.total_reward += reward


if __name__ == "__main__":
    env = Environment()
    agent = Agent()

    while not env.is_done():
        agent.step(env)

    print("Total reward got : %.4f" % agent.total_reward)