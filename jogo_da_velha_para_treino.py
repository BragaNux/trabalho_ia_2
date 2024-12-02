import pygame
import sys
import random
import pickle
import math
import tensorflow as tf
import numpy as np

# inicia pygame
pygame.init()

# config principais
tamanho_janela = 900
linhas, colunas = 3, 3
tamanho_celula = tamanho_janela // linhas

# cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
azul = (0, 0, 255)
cinza = (200, 200, 200)

# cria janela do jogo
janela = pygame.display.set_mode((tamanho_janela, tamanho_janela))
pygame.display.set_caption('jogo da velha - ia vs ia')

# estado do tabuleiro
jogador_x = 1
jogador_o = -1

# recompensas
recompensa_x = 0
recompensa_o = 0
vitorias_x = 0
vitorias_o = 0
empates = 0

# memória para aprendizado por reforço
memoria_x = []
memoria_o = []

# carregar valores de estados aprendidos anteriormente, se existirem
try:
    with open('valores_estado.pkl', 'rb') as f:
        valores_estado = pickle.load(f)
except FileNotFoundError:
    valores_estado = {}  # armazena os valores de cada estado do tabuleiro

# parâmetros de aprendizado
alpha = 0.1  # taxa de aprendizado
gamma = 0.95  # fator de desconto
epsilon = 0.5  # probabilidade de exploração inicial
epsilon_decay = 0.995  # fator de decaimento do epsilon
min_epsilon = 0.01  # valor mínimo do epsilon

# definir o modelo tensorflow
modelo = tf.keras.Sequential([
    tf.keras.layers.InputLayer(shape=(9,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(9, activation='linear')
])
modelo.compile(optimizer='adam', loss='mse')

# função softmax
def softmax(q_values, temperatura=1.0):
    exp_q = [math.exp(q / temperatura) for q in q_values]
    soma_exp_q = sum(exp_q)
    probabilidades = [q / soma_exp_q for q in exp_q]
    return probabilidades

# função para desenhar o tabuleiro
def desenhar_tabuleiro(tabuleiros):
    janela.fill(branco)
    num_jogos = len(tabuleiros)
    cols = int(num_jogos ** 0.5)
    rows = (num_jogos + cols - 1) // cols
    celula_jogo = tamanho_janela // max(rows, cols)
    tamanho_celula_tabuleiro = celula_jogo // linhas

    for idx, tabuleiro in enumerate(tabuleiros):
        base_x = (idx % cols) * celula_jogo
        base_y = (idx // cols) * celula_jogo
        
        # fundo cinza para separar os jogos
        pygame.draw.rect(janela, cinza, (base_x, base_y, celula_jogo, celula_jogo))
        
        # linhas do tabuleiro
        for linha in range(1, linhas):
            pygame.draw.line(janela, preto, (base_x, base_y + linha * tamanho_celula_tabuleiro), (base_x + celula_jogo, base_y + linha * tamanho_celula_tabuleiro), 2)
            pygame.draw.line(janela, preto, (base_x + linha * tamanho_celula_tabuleiro, base_y), (base_x + linha * tamanho_celula_tabuleiro, base_y + celula_jogo), 2)
        
        # desenhar x e o
        for linha in range(linhas):
            for coluna in range(colunas):
                centro_x = base_x + coluna * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
                centro_y = base_y + linha * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
                if tabuleiro[linha][coluna] == jogador_x:
                    pygame.draw.line(janela, vermelho, (centro_x - 20, centro_y - 20), (centro_x + 20, centro_y + 20), 3)
                    pygame.draw.line(janela, vermelho, (centro_x + 20, centro_y - 20), (centro_x - 20, centro_y + 20), 3)
                elif tabuleiro[linha][coluna] == jogador_o:
                    pygame.draw.circle(janela, azul, (centro_x, centro_y), tamanho_celula_tabuleiro // 3, 3)

# função para verificar se há um vencedor
def verificar_vencedor(tabuleiro):
    # verificar linhas e colunas
    for i in range(linhas):
        if sum(tabuleiro[i]) == 3 * jogador_x or sum(tabuleiro[i]) == 3 * jogador_o:
            return tabuleiro[i][0]
        if sum([tabuleiro[j][i] for j in range(colunas)]) == 3 * jogador_x or sum([tabuleiro[j][i] for j in range(colunas)]) == 3 * jogador_o:
            return tabuleiro[0][i]
    
    # verificar diagonais
    diagonal_principal = sum([tabuleiro[i][i] for i in range(linhas)])
    diagonal_secundaria = sum([tabuleiro[i][linhas - i - 1] for i in range(linhas)])
    if diagonal_principal == 3 * jogador_x or diagonal_principal == 3 * jogador_o:
        return tabuleiro[0][0]
    if diagonal_secundaria == 3 * jogador_x or diagonal_secundaria == 3 * jogador_o:
        return tabuleiro[0][linhas - 1]
    
    return 0

# função para verificar se há uma jogada iminente de vitória ou derrota
def jogada_iminente(tabuleiro, jogador):
    for linha in range(linhas):
        for coluna in range(colunas):
            if tabuleiro[linha][coluna] == 0:
                tabuleiro[linha][coluna] = jogador
                if verificar_vencedor(tabuleiro) == jogador:
                    tabuleiro[linha][coluna] = 0
                    return (linha, coluna)
                tabuleiro[linha][coluna] = 0
    return None

# função para verificar cerco
def verificar_cerco(tabuleiro, jogador):
    jogadas_possiveis = [(linha, coluna) for linha in range(linhas) for coluna in range(colunas) if tabuleiro[linha][coluna] == 0]
    contagem_vitoria = 0
    ultima_jogada = None

    for linha, coluna in jogadas_possiveis:
        tabuleiro[linha][coluna] = jogador
        if jogada_iminente(tabuleiro, jogador):
            contagem_vitoria += 1
            ultima_jogada = (linha, coluna)
        tabuleiro[linha][coluna] = 0

    if contagem_vitoria >= 2:
        return ultima_jogada
    return None

# função para a ia fazer a jogada
def jogada_ia(tabuleiro, jogador):
    estado_atual = np.array(tabuleiro).flatten().reshape(1, -1)  # converter o estado do tabuleiro para um array

    # verificar se há uma jogada iminente de vitória para a ia
    jogada = jogada_iminente(tabuleiro, jogador)
    if jogada:
        linha, coluna = jogada
    else:
        # verificar se há uma jogada iminente de vitória para o oponente e bloquear
        oponente = jogador_x if jogador == jogador_o else jogador_o
        jogada = jogada_iminente(tabuleiro, oponente)
        if jogada:
            linha, coluna = jogada
        else:
            # verificar se o oponente está tentando fazer um cerco
            jogada = verificar_cerco(tabuleiro, oponente)
            if jogada:
                linha, coluna = jogada
            else:
                # se não houver jogada iminente, escolher a melhor jogada usando o modelo
                escolhas_possiveis = [(linha, coluna) for linha in range(linhas) for coluna in range(colunas) if tabuleiro[linha][coluna] == 0]
                
                if random.uniform(0, 1) < epsilon:  # exploração (escolher jogada aleatória)
                    linha, coluna = random.choice(escolhas_possiveis)
                else:  # usar o modelo para prever a melhor jogada
                    previsoes = modelo.predict(estado_atual)[0]
                    q_values = [previsoes[linha * colunas + coluna] for linha, coluna in escolhas_possiveis]
                    probabilidades = softmax(q_values)
                    escolha_idx = random.choices(range(len(escolhas_possiveis)), weights=probabilidades)[0]
                    linha, coluna = escolhas_possiveis[escolha_idx]

    # fazer a jogada
    tabuleiro[linha][coluna] = jogador

    # salvar o estado atual do tabuleiro na memória
    novo_estado = np.array(tabuleiro).flatten()
    if jogador == jogador_x:
        memoria_x.append((estado_atual, novo_estado))
    elif jogador == jogador_o:
        memoria_o.append((estado_atual, novo_estado))

# função principal do jogo
def jogo_da_velha():
    global recompensa_x, recompensa_o, memoria_x, memoria_o, valores_estado, epsilon, vitorias_x, vitorias_o, empates
    rodando = True
    max_partidas = 10000  # número de partidas para treinamento
    num_jogos = 9  # número de jogos simultâneos
    tabuleiros = [[[0 for _ in range(colunas)] for _ in range(linhas)] for _ in range(num_jogos)]
    
    partidas = 0
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                break
        
        if not rodando:
            break
        
        for i, tabuleiro in enumerate(tabuleiros):
            vencedor = verificar_vencedor(tabuleiro)
            if vencedor == 0 and any(tabuleiro[linha][coluna] == 0 for linha in range(linhas) for coluna in range(colunas)):
                jogada_ia(tabuleiro, jogador_x if partidas % 2 == 0 else jogador_o)
                vencedor = verificar_vencedor(tabuleiro)
            
            if vencedor != 0 or all(tabuleiro[linha][coluna] != 0 for linha in range(linhas) for coluna in range(colunas)):
                recompensa = 0
                if vencedor == jogador_x:
                    recompensa_x += 5  # recompensa por vitória
                    recompensa_o -= 3  # penalidade por derrota
                    recompensa = 5
                    vitorias_x += 1
                    print(f'jogador x venceu no jogo {i + 1}!')
                elif vencedor == jogador_o:
                    recompensa_o += 5  # recompensa por vitória
                    recompensa_x -= 3  # penalidade por derrota
                    recompensa = -5
                    vitorias_o += 1
                    print(f'jogador o venceu no jogo {i + 1}!')
                else:
                    recompensa_x += 5  # recompensa por empate
                    recompensa_o += 5
                    recompensa = 5
                    empates += 1
                    print(f'empate no jogo {i + 1}!')
                
                # ajuste de aprendizado (q-learning)
                for estado_ant, estado_atual in memoria_x:
                    modelo.fit(estado_ant, np.array([recompensa]), verbose=0)
                for estado_ant, estado_atual in memoria_o:
                    modelo.fit(estado_ant, np.array([-recompensa]), verbose=0)
                
                # salvar apenas estados de empates e cercos
                if vencedor == 0 or verificar_cerco(tabuleiro, jogador_x) or verificar_cerco(tabuleiro, jogador_o):
                    with open('valores_estado.pkl', 'wb') as f:
                        pickle.dump(valores_estado, f)
                
                # reiniciar o tabuleiro para a próxima partida
                tabuleiros[i] = [[0 for _ in range(colunas)] for _ in range(linhas)]
                memoria_x.clear()
                memoria_o.clear()
                
                # reduzir a exploração ao longo do tempo
                if epsilon > min_epsilon:
                    epsilon *= epsilon_decay
                
                # parar o treinamento se alcançar um bom desempenho
                partidas += 1
                if partidas >= max_partidas and (vitorias_x == 0 or vitorias_o == 0 or empates / partidas > 0.95):
                    rodando = False
        
        desenhar_tabuleiro(tabuleiros)
        pygame.display.update()
    
    # exibir resultados finais
    print(f'recompensa final - jogador x: {recompensa_x}, jogador o: {recompensa_o}')

if __name__ == "__main__":
    jogo_da_velha()
