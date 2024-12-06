import pygame
import pickle
import numpy as np
import tensorflow as tf

# Configurações do pygame
pygame.init()
largura_tela, altura_tela = 300, 300
tamanho_celula = largura_tela // 3

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
azul = (0, 0, 255)

# Jogadores
jogador_x = 1
jogador_o = -1

# Carregar valores de estados aprendidos anteriormente
try:
    with open('valores_estado.pkl', 'rb') as f:
        valores_estado = pickle.load(f)
    print(f"Total de estados aprendidos: {len(valores_estado)}")
except FileNotFoundError:
    print("Arquivo de treinamento 'valores_estado.pkl' não encontrado. Treine a IA primeiro!")
    exit()

# Carregar o modelo treinado
try:
    modelo = tf.keras.models.load_model('modelo_treinado.h5')
    print("Modelo treinado carregado com sucesso!")
except FileNotFoundError:
    print("Modelo treinado 'modelo_treinado.h5' não encontrado. Treine a IA primeiro!")
    exit()

# Função para verificar vencedor
def verificar_vencedor(tabuleiro):
    for i in range(3):
        if sum(tabuleiro[i]) in [3 * jogador_x, 3 * jogador_o]:
            return tabuleiro[i][0]
        if sum([tabuleiro[j][i] for j in range(3)]) in [3 * jogador_x, 3 * jogador_o]:
            return tabuleiro[0][i]

    diagonal_principal = sum(tabuleiro[i][i] for i in range(3))
    diagonal_secundaria = sum(tabuleiro[i][2 - i] for i in range(3))
    if diagonal_principal in [3 * jogador_x, 3 * jogador_o]:
        return tabuleiro[0][0]
    if diagonal_secundaria in [3 * jogador_x, 3 * jogador_o]:
        return tabuleiro[0][2]

    return 0

# IA para realizar jogadas
def jogada_ia(tabuleiro, jogador):
    estado_atual = np.array(tabuleiro).flatten().reshape(1, -1)
    escolhas_possiveis = [(i, j) for i in range(3) for j in range(3) if tabuleiro[i][j] == 0]

    if not escolhas_possiveis:  # Verifica se há jogadas possíveis
        return  # Nenhuma jogada a fazer

    previsoes = modelo.predict(estado_atual, verbose=0)[0]
    q_values = [previsoes[i * 3 + j] for i, j in escolhas_possiveis]
    melhor_jogada = escolhas_possiveis[np.argmax(q_values)]

    tabuleiro[melhor_jogada[0]][melhor_jogada[1]] = jogador

# Desenhar tabuleiro
def desenhar_tabuleiro(tela, tabuleiro):
    tela.fill(branco)
    for i in range(1, 3):
        pygame.draw.line(tela, preto, (0, i * tamanho_celula), (largura_tela, i * tamanho_celula), 2)
        pygame.draw.line(tela, preto, (i * tamanho_celula, 0), (i * tamanho_celula, altura_tela), 2)

    for i in range(3):
        for j in range(3):
            cx = j * tamanho_celula + tamanho_celula // 2
            cy = i * tamanho_celula + tamanho_celula // 2
            if tabuleiro[i][j] == jogador_x:
                pygame.draw.line(tela, vermelho, (cx - 20, cy - 20), (cx + 20, cy + 20), 3)
                pygame.draw.line(tela, vermelho, (cx + 20, cy - 20), (cx - 20, cy + 20), 3)
            elif tabuleiro[i][j] == jogador_o:
                pygame.draw.circle(tela, azul, (cx, cy), 30, 3)

# Função principal
def jogo_contra_ia():
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    pygame.display.set_caption("Jogo da Velha - Você vs IA")
    clock = pygame.time.Clock()

    primeiro_jogador = jogador_x  # Começa com o humano
    continuar_jogando = True

    while continuar_jogando:
        tabuleiro = [[0 for _ in range(3)] for _ in range(3)]
        jogador_atual = primeiro_jogador
        rodando = True

        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    continuar_jogando = False
                    rodando = False

                if evento.type == pygame.MOUSEBUTTONDOWN and jogador_atual == jogador_x:
                    x, y = pygame.mouse.get_pos()
                    linha, coluna = y // tamanho_celula, x // tamanho_celula
                    if tabuleiro[linha][coluna] == 0:
                        tabuleiro[linha][coluna] = jogador_x
                        jogador_atual = jogador_o

            if jogador_atual == jogador_o and rodando:
                jogada_ia(tabuleiro, jogador_o)
                jogador_atual = jogador_x

            vencedor = verificar_vencedor(tabuleiro)
            if vencedor != 0 or all(tabuleiro[i][j] != 0 for i in range(3) for j in range(3)):
                desenhar_tabuleiro(tela, tabuleiro)
                pygame.display.flip()
                pygame.time.wait(2000)
                resultado = "Você venceu!" if vencedor == jogador_x else "IA venceu!" if vencedor == jogador_o else "Empate!"
                print(resultado)
                rodando = False

            desenhar_tabuleiro(tela, tabuleiro)
            pygame.display.flip()
            clock.tick(30)

        # Alterna o primeiro jogador para a próxima rodada
        primeiro_jogador = jogador_o if primeiro_jogador == jogador_x else jogador_x

    pygame.quit()

if __name__ == "__main__":
    jogo_contra_ia()
