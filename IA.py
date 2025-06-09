import numpy as np
import random

W = 800
H = 600

epsilon = 0.2
alpha = 0.1
gamma = 0.9

div = 6 # Discretizacao do espaco em um grid div x div

q_table = {
    (bx, by, py, bvx, bvy): [0.0, 0.0, 0.0]
    for bx in range(div)
    for by in range(div)
    for py in range(div)
    for bvx in range(-div+1,div)
    for bvy in range(-div+1,div)
}

def get_state(bp, pp, bv):
    return (
        int(bp.x*div/W),
        int(bp.y*div/H),
        int(pp.y*div/H),
        int(bv.x*div/8),
        int(bv.y*div/8)
    )

def choose_action(state):
    if random.random() < epsilon:
        return random.choice([0,1,2])
    else:
        return np.argmax(q_table[state])

def update_q_table(state, action, reward, next_state):
    global q_table
    best_next = max(q_table[next_state])
    q_table[state][action] += alpha * (reward + gamma * best_next - q_table[state][action])

def size_q_table():
    return sum(1 for valores in q_table.values() if valores != [0.0, 0.0, 0.0])

def save_q_table():
    np.save("q_table.npy", q_table)

    with open("q_table.txt", "w") as f:
        for state, q_values in q_table.items():
            f.write(f"{state} -> {q_values}\n")

    print(size_q_table())

def load_q_table():
    global q_table

    try:
        q_table = np.load("q_table.npy", allow_pickle=True).item()
        print(size_q_table())
    except FileNotFoundError:
        q_table = {
            (bx, by, py, bvx, bvy): [0.0, 0.0, 0.0]
            for bx in range(div)
            for by in range(div)
            for py in range(div)
            for bvx in range(-div+1,div)
            for bvy in range(-div+1,div)
        }