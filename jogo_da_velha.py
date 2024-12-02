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
pygame.display.set_caption('jogo da velha - ia vs humano')

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
epsilon = 0.1  # probabilidade de exploração inicial ajustada para valor baixo
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
def desenhar_tabuleiro(tabuleiro):
    janela.fill(branco)
    tamanho_celula_tabuleiro = tamanho_janela // linhas

    # linhas do tabuleiro
    for linha in range(1, linhas):
        pygame.draw.line(janela, preto, (0, linha * tamanho_celula_tabuleiro), (tamanho_janela, linha * tamanho_celula_tabuleiro), 2)
        pygame.draw.line(janela, preto, (linha * tamanho_celula_tabuleiro, 0), (linha * tamanho_celula_tabuleiro, tamanho_janela), 2)
    
    # desenhar x e o
    for linha in range(linhas):
        for coluna in range(colunas):
            centro_x = coluna * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
            centro_y = linha * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
            if tabuleiro[linha][coluna] == jogador_x:
                pygame.draw.line(janela, vermelho, (centro_x - 20, centro_y - 20), (centro_x + 20, centro_y + 20), 3)
                pygame.draw.line(janela, vermelho, (centro_x + 20, centro_y - 20), (centro_x - 20, centro_y + 20), 3)
            elif tabuleiro[linha][coluna] == jogador_o:
                pygame.draw.circle(janela, azul, (centro_x, centro_y), tamanho_celula_tabuleiro // 3, 3)

    # exibir pontuação
    fonte = pygame.font.Font(None, 36)
    texto_pontuacao = fonte.render(f'Vitórias X: {vitorias_x} | Vitórias O: {vitorias_o} | Empates: {empates}', True, preto)
    janela.blit(texto_pontuacao, (10, tamanho_janela - 50))

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

# função para identificar se o adversário está tentando fazer um cerco
def identificar_cerco(tabuleiro, jogador):
    jogadas_possiveis = [(linha, coluna) for linha in range(linhas) for coluna in range(colunas) if tabuleiro[linha][coluna] == 0]
    cerco_possivel = []

    for linha, coluna in jogadas_possiveis:
        tabuleiro[linha][coluna] = jogador
        cerco_detectado = verificar_cerco(tabuleiro, jogador)
        if cerco_detectado:
            cerco_possivel.append((linha, coluna))
        tabuleiro[linha][coluna] = 0

    if len(cerco_possivel) > 0:
        return cerco_possivel[0]
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
                # identificar se o adversário está tentando fazer um cerco em duas jogadas futuras
                jogada = identificar_cerco(tabuleiro, oponente)
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
    jogador_atual = jogador_x
    tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
    
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                break
            if evento.type == pygame.MOUSEBUTTONDOWN and jogador_atual == jogador_x:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                linha = mouse_y // tamanho_celula
                coluna = mouse_x // tamanho_celula
                if tabuleiro[linha][coluna] == 0:
                    tabuleiro[linha][coluna] = jogador_x
                    jogador_atual = jogador_o
        
        if not rodando:
            break
        
        vencedor = verificar_vencedor(tabuleiro)
        if vencedor != 0 or all(tabuleiro[linha][coluna] != 0 for linha in range(linhas) for coluna in range(colunas)):
            if vencedor == jogador_x:
                print('você venceu!')
                vitorias_x += 1
            elif vencedor == jogador_o:
                print('ia venceu!')
                vitorias_o += 1
            else:
                print('empate!')
                empates += 1
            pygame.time.delay(2000)  # adicionar um delay de 2 segundos após o término da partida
            tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
            jogador_atual = jogador_x
        
        if jogador_atual == jogador_o:
            jogada_ia(tabuleiro, jogador_o)
            jogador_atual = jogador_x
        
        desenhar_tabuleiro(tabuleiro)
        pygame.display.update()
    
    # salvar os valores de estado aprendidos
    with open('valores_estado.pkl', 'wb') as f:
        pickle.dump(valores_estado, f)

if __name__ == "__main__":
    jogo_da_velha()
