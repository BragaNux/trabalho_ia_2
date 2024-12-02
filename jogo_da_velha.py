import pygame
import sys
import random
import pickle
import math

# inicia
pygame.init()

# config
tamanho_janela = 900
linhas, colunas = 3, 3
tamanho_celula = tamanho_janela // linhas

# corzinha
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
CINZA = (200, 200, 200)

# nova window
janela = pygame.display.set_mode((tamanho_janela, tamanho_janela))
pygame.display.set_caption('Jogo da Velha - IA vs IA')

# tabuleiro
JOGADOR_X = 1
JOGADOR_O = -1

# recompensa
recompensa_X = 0
recompensa_O = 0
vitorias_X = 0
vitorias_O = 0
empates = 0

# aprendizado por reforço
memoria_X = []
memoria_O = []

# carregar valores de estados aprendidos anteriormente, se existirem
try:
    with open('valores_estado.pkl', 'rb') as f:
        valores_estado = pickle.load(f)
except FileNotFoundError:
    valores_estado = {}  # armazena os valores de cada estado do tabuleiro

# parametros de aprendizado
alpha = 0.1  # taxa de aprendizado
gamma = 0.95  # fator de desconto
epsilon = 0.5  # probabilidade de exploração inicial
epsilon_decay = 0.995  # fator de decaimento do epsilon
min_epsilon = 0.01  # valor minimo do epsilon

# softmax
def softmax(q_values, temperatura=1.0):
    exp_q = [math.exp(q / temperatura) for q in q_values]
    soma_exp_q = sum(exp_q)
    probabilidades = [q / soma_exp_q for q in exp_q]
    return probabilidades

# desenha os tabuleiros
def desenhar_tabuleiro(tabuleiros):
    janela.fill(BRANCO)
    num_jogos = len(tabuleiros)
    cols = int(num_jogos ** 0.5)
    rows = (num_jogos + cols - 1) // cols
    celula_jogo = tamanho_janela // max(rows, cols)
    tamanho_celula_tabuleiro = celula_jogo // linhas

    for idx, tabuleiro in enumerate(tabuleiros):
        base_x = (idx % cols) * celula_jogo
        base_y = (idx // cols) * celula_jogo
        
        # separar
        pygame.draw.rect(janela, CINZA, (base_x, base_y, celula_jogo, celula_jogo))
        
        # linhas do tabuleiro
        for linha in range(1, linhas):
            pygame.draw.line(janela, PRETO, (base_x, base_y + linha * tamanho_celula_tabuleiro), (base_x + celula_jogo, base_y + linha * tamanho_celula_tabuleiro), 2)
            pygame.draw.line(janela, PRETO, (base_x + linha * tamanho_celula_tabuleiro, base_y), (base_x + linha * tamanho_celula_tabuleiro, base_y + celula_jogo), 2)
        
        # jogadore X e O
        for linha in range(linhas):
            for coluna in range(colunas):
                centro_x = base_x + coluna * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
                centro_y = base_y + linha * tamanho_celula_tabuleiro + tamanho_celula_tabuleiro // 2
                if tabuleiro[linha][coluna] == JOGADOR_X:
                    pygame.draw.line(janela, VERMELHO, (centro_x - 20, centro_y - 20), (centro_x + 20, centro_y + 20), 3)
                    pygame.draw.line(janela, VERMELHO, (centro_x + 20, centro_y - 20), (centro_x - 20, centro_y + 20), 3)
                elif tabuleiro[linha][coluna] == JOGADOR_O:
                    pygame.draw.circle(janela, AZUL, (centro_x, centro_y), tamanho_celula_tabuleiro // 3, 3)

# verifica o vencedor
def verificar_vencedor(tabuleiro):
    # linhas,colunas
    for i in range(linhas):
        if sum(tabuleiro[i]) == 3 * JOGADOR_X or sum(tabuleiro[i]) == 3 * JOGADOR_O:
            return tabuleiro[i][0]
        if sum([tabuleiro[j][i] for j in range(colunas)]) == 3 * JOGADOR_X or sum([tabuleiro[j][i] for j in range(colunas)]) == 3 * JOGADOR_O:
            return tabuleiro[0][i]
    
    # diagonais
    diagonal_principal = sum([tabuleiro[i][i] for i in range(linhas)])
    diagonal_secundaria = sum([tabuleiro[i][linhas - i - 1] for i in range(linhas)])
    if diagonal_principal == 3 * JOGADOR_X or diagonal_principal == 3 * JOGADOR_O:
        return tabuleiro[0][0]
    if diagonal_secundaria == 3 * JOGADOR_X or diagonal_secundaria == 3 * JOGADOR_O:
        return tabuleiro[0][linhas - 1]
    
    return 0

# funcao para fazer jogadas automaticas com aprendizado por reforço
def jogada_ia(tabuleiro, jogador):
    escolhas_possiveis = [(linha, coluna) for linha in range(linhas) for coluna in range(colunas) if tabuleiro[linha][coluna] == 0]
    estado_atual = tuple(tuple(linha) for linha in tabuleiro)  # converte o estado do tabuleiro para uma tupla para ser usada como chave
    
    if random.uniform(0, 1) < epsilon:  #explora
        linha, coluna = random.choice(escolhas_possiveis)
    else:  # melhores opções conhecidas usando softmax
        q_values = []
        for linha, coluna in escolhas_possiveis:
            tabuleiro[linha][coluna] = jogador
            novo_estado = tuple(tuple(l) for l in tabuleiro)
            valor_estado = valores_estado.get(novo_estado, 0)
            q_values.append(valor_estado)
            tabuleiro[linha][coluna] = 0
        
        probabilidades = softmax(q_values)
        escolha_idx = random.choices(range(len(escolhas_possiveis)), weights=probabilidades)[0]
        linha, coluna = escolhas_possiveis[escolha_idx]
    
    # jogada
    tabuleiro[linha][coluna] = jogador
    
    # salva o estado atual
    novo_estado = tuple(tuple(linha) for linha in tabuleiro)
    if jogador == JOGADOR_X:
        memoria_X.append((estado_atual, novo_estado))
    else:
        memoria_O.append((estado_atual, novo_estado))

# main do jogo
def jogo_da_velha():
    global recompensa_X, recompensa_O, memoria_X, memoria_O, valores_estado, epsilon, vitorias_X, vitorias_O, empates
    rodando = True
    jogador_atual = JOGADOR_X
    max_partidas = 10000  # numero de partidas
    num_jogos = 9  # qnt jogo simultaneo
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
                jogada_ia(tabuleiro, jogador_atual)
                jogador_atual *= -1
                vencedor = verificar_vencedor(tabuleiro)
            
            if vencedor != 0 or all(tabuleiro[linha][coluna] != 0 for linha in range(linhas) for coluna in range(colunas)):
                recompensa = 0
                if vencedor == JOGADOR_X:
                    recompensa_X += 5  # recompesa da vitoria
                    recompensa_O -= 3  # penalidade da derrota
                    recompensa = 5
                    vitorias_X += 1
                    print(f'Jogador X venceu no jogo {i + 1}!')
                elif vencedor == JOGADOR_O:
                    recompensa_O += 5  
                    recompensa_X -= 3  
                    recompensa = -5
                    vitorias_O += 1
                    print(f'Jogador O venceu no jogo {i + 1}!')
                else:
                    recompensa_X += 5  # recompensa pra empate
                    recompensa_O += 5
                    recompensa = 5
                    empates += 1
                    print(f'Empate no jogo {i + 1}!')
                
                # ajuste de aprendizado q-learning simples
                for estado_ant, estado_atual in memoria_X:
                    valores_estado[estado_ant] = valores_estado.get(estado_ant, 0) + alpha * (recompensa + gamma * valores_estado.get(estado_atual, 0) - valores_estado.get(estado_ant, 0))
                for estado_ant, estado_atual in memoria_O:
                    valores_estado[estado_ant] = valores_estado.get(estado_ant, 0) + alpha * (-recompensa + gamma * valores_estado.get(estado_atual, 0) - valores_estado.get(estado_ant, 0))
                
                # reiniciar proxima partida
                tabuleiros[i] = [[0 for _ in range(colunas)] for _ in range(linhas)]
                jogador_atual = JOGADOR_X if partidas % 2 == 0 else JOGADOR_O
                memoria_X.clear()
                memoria_O.clear()
                
                # diminui o epsilon pra diminuir a exploracao
                if epsilon > min_epsilon:
                    epsilon *= epsilon_decay
                
                # finalmente ficou inteligente
                partidas += 1
                if partidas >= max_partidas and (vitorias_X == 0 or vitorias_O == 0 or empates / partidas > 0.95):
                    rodando = False
        
        desenhar_tabuleiro(tabuleiros)
        pygame.display.update()
    
    # exibir recompensas finais e estatisticas
    print(f'Recompensa Final - Jogador X: {recompensa_X}, Jogador O: {recompensa_O}')
    print(f'Vitórias Jogador X: {vitorias_X}, Vitórias Jogador O: {vitorias_O}, Empates: {empates}')
    
    # salvar os valores de estado aprendidos
    with open('valores_estado.pkl', 'wb') as f:
        pickle.dump(valores_estado, f)

if __name__ == "__main__":
    jogo_da_velha()
