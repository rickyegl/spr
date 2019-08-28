import torch
import numpy as np
from collections import deque, namedtuple

from memory import blank_trans
from src.envs import Env

Transition = namedtuple('Transition', ('timestep', 'state', 'action', 'reward', 'nonterminal'))


def get_random_agent_episodes(args):
    env = Env(args)
    env.train()
    action_space = env.action_space()
    print('-------Collecting samples----------')
    transitions = []
    timestep, done = 0, True
    for T in range(args.initial_exp_steps):
        if done:
            state, done = env.reset(), False
        state = state[-1].mul(255).to(dtype=torch.uint8,
                                      device=torch.device('cpu'))  # Only store last frame and discretise to save memory
        action = np.random.randint(0, action_space)
        next_state, reward, done = env.step(action)
        transitions.append(Transition(timestep, state, action, reward, not done))
        state = next_state
        timestep = 0 if done else timestep + 1

    env.close()
    return transitions


def sample_state(real_transitions):
    history = 4
    transition = np.array([None] * history)
    idx = np.random.randint(0, len(real_transitions))
    transition[3] = real_transitions[idx]

    for t in range(4 - 2, -1, -1):  # e.g. 2 1 0
        if transition[t + 1].timestep == 0:
            transition[t] = blank_trans  # If future frame has timestep 0
        else:
            transition[t] = real_transitions[idx - history + 1 + t]
    return transition
