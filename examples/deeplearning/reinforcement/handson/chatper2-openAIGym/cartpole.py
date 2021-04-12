import random

import gym


def gym_concept():
    e = gym.make("CartPole-v0")

    obs = e.reset()
    print("first obs: ", obs)
    print("action_space ", e.action_space)
    print("observation_space ", e.observation_space)

    ret = e.step(0)
    print("first return: ", ret)


def random_cartpole_action():
    env = gym.make("CartPole-v0")
    total_reward = 0
    total_step = 0

    obs = env.reset()
    print("first obs: ", obs)
    while True:
        obs, reward, done, _ = env.step(env.action_space.sample())
        total_step += 1
        total_reward += reward
        if done:
            break

    print("total reward: ", total_reward)
    print("total steps: ", total_step)


if __name__ == "__main__":
    for _ in range(100):
        random_cartpole_action()