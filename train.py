import pygame
import random
import numpy as np
from IA import get_state, choose_action, update_q_table, save_q_table, load_q_table

# game variables
W = 800
H = 600

player_dir = 0
player_score = 0

cpu_dir = 0
cpu_score = 0

ang_tol = 5*np.pi/180
vp = 4
vb = 8

state = [0, 0, 0, 0, 0]
action = [0, 0, 0]
next_action = [0, 0, 0]
reward = 0

load_q_table() # Carrega a memoria da IA

episodes = int(4e4)
for _ in range(episodes):
    player_pos = pygame.Vector2(20, (H-200) / 2)
    cpu_pos = pygame.Vector2(W-(40+20), (H-200) / 2)

    ball_pos = pygame.Vector2((W-20) / 2, (H-20) / 2)
    angle = random.uniform(np.pi-ang_tol, np.pi+ang_tol)
    ball_dir = pygame.Vector2(np.cos(angle),np.sin(angle))

    for _ in range(500): # ticks
        # Movimentacao do player
        eps = 5
        dist = (player_pos.y+100) - ball_pos.y

        if dist < -eps:
            player_dir = 1
        elif dist > eps:
            player_dir = -1
        else:
            player_dir = 0

        if player_pos.y > 0 and player_pos.y+200 < H:
            player_pos.y += vp*player_dir
        else:
            player_pos.y = eps if player_pos.y <= 0 else H-(200+eps)

        eps = 1.0e-2

        # Movimentacao da cpu
        state = get_state(ball_pos, player_pos, ball_dir)
        action = choose_action(state)
        cpu_dir = [-1,0,1][action] # -1: descer | 0: ficar parado | 1: subir

        if cpu_pos.y > 0 and cpu_pos.y+200 < H:
            cpu_pos.y += vp*cpu_dir
        else:
            cpu_pos.y = eps if cpu_pos.y <= 0 else H-(200+eps)
            reward = -0.1 # Recompensa negativa por tentar sair da tela

        # Colisao da bola c/ a parede
        if ball_pos.x > 0 and ball_pos.x < W-20:
            ball_pos.x += vb*ball_dir.x
        else:
            if ball_pos.x <= 0:
                cpu_score += 1
                reward = 1 # Recompensa positiva por fazer o ponto
            else:
                player_score += 1
                reward = -1 # Recompensa negativa por tomar o ponto

            ball_pos = pygame.Vector2((W-20) / 2, (H-20) / 2)
            angle = random.uniform(np.pi-ang_tol, np.pi+ang_tol)
            ball_dir = pygame.Vector2(np.cos(angle),np.sin(angle))

        if ball_pos.y >= 0 and ball_pos.y <= H-20:
            ball_pos.y += vb*ball_dir.y
        else:
            ball_pos.y = 0 if ball_pos.y < 0 else H-20
            ball_dir.y *= -1

        # Colisao da bola c/ o player
        if (ball_pos.x <= player_pos.x+40) and\
        (ball_pos.y < player_pos.y and ball_pos.y+20 >= player_pos.y):
            # Colidiu na parte de cima
            ball_pos.y = player_pos.y-20
            ball_dir.x = abs(ball_dir.x)
            ball_dir.y = -abs(ball_dir.y)
        elif (ball_pos.x <= player_pos.x+40) and\
        (ball_pos.y < player_pos.y+200 and ball_pos.y+20 >= player_pos.y+200):
            # Colidiu na parte de baixo
            ball_pos.y = player_pos.y+200
            ball_dir.x = abs(ball_dir.x)
            ball_dir.y = abs(ball_dir.y)
        elif (ball_pos.x > player_pos.x and ball_pos.x < player_pos.x+40) and (ball_pos.x+20 > player_pos.x+40) and\
        (ball_pos.y >= player_pos.y and ball_pos.y <= player_pos.y+200) and (ball_pos.y+20 >= player_pos.y and ball_pos.y+20 <= player_pos.y+200):
            # Colidiu na direita
            ball_pos.x = player_pos.x+40
            ball_dir.x *= -1
        elif (ball_pos.x < player_pos.x) and (ball_pos.x+20 > player_pos.x and ball_pos.x+20 < player_pos.x+40) and\
        (ball_pos.y >= player_pos.y and ball_pos.y <= player_pos.y+200) and (ball_pos.y+20 >= player_pos.y and ball_pos.y+20 <= player_pos.y+200):
            # Colidiu na esquerda (nao acontece, porque precisaria bater na parede primeiro, que reseta a bola)
            ball_pos.x = player_pos.x-20
            ball_dir.x *= -1

        # Colisao da bola c/ a cpu
        if (ball_pos.x+20 >= cpu_pos.x) and\
        (ball_pos.y < cpu_pos.y and ball_pos.y+20 >= cpu_pos.y):
            # Colidiu na parte de cima
            ball_pos.y = cpu_pos.y-20
            ball_dir.x = -abs(ball_dir.x)
            ball_dir.y = -abs(ball_dir.y)

            reward = 0.3 # Recompensa positiva por tocar na bola

        elif (ball_pos.x+20 >= cpu_pos.x) and\
        (ball_pos.y < cpu_pos.y+200 and ball_pos.y+20 >= cpu_pos.y+200):
            # Colidiu na parte de baixo
            ball_pos.y = cpu_pos.y+200
            ball_dir.x = -abs(ball_dir.x)
            ball_dir.y = abs(ball_dir.y)

            reward = 0.3 # Recompensa positiva por tocar na bola

        elif (ball_pos.x < cpu_pos.x) and (ball_pos.x+20 > cpu_pos.x and ball_pos.x+20 < cpu_pos.x+40) and\
        (ball_pos.y >= cpu_pos.y and ball_pos.y <= cpu_pos.y+200) and (ball_pos.y+20 >= cpu_pos.y and ball_pos.y+20 <= cpu_pos.y+200):
            # Colidiu na esquerda
            ball_pos.x = cpu_pos.x-20
            ball_dir.x *= -1

            reward = 0.3 # Recompensa positiva por tocar na bola

        elif (ball_pos.x > cpu_pos.x and ball_pos.x < cpu_pos.x+40) and (ball_pos.x+20 > cpu_pos.x+40) and\
        (ball_pos.y >= cpu_pos.y and ball_pos.y <= cpu_pos.y+200) and (ball_pos.y+20 >= cpu_pos.y and ball_pos.y+20 <= cpu_pos.y+200):
            # Colidiu na direita (nao acontece, porque precisaria bater na parede primeiro, que reseta a bola)
            ball_pos.x = cpu_pos.x+40
            ball_dir.x *= -1
        
        next_state = get_state(ball_pos, player_pos, ball_dir)
        update_q_table(state, action, reward, next_state)

print(f"Treinado! Score final BOT {player_score} - {cpu_score} IA")
save_q_table() # Salva a memoria da IA