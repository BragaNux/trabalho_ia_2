import pygame
import sys
import random

# Inicializar pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Truco com IA")

# Configurações gerais
FPS = 60
FONT = pygame.font.Font(None, 36)


# Hierarquia das cartas
HIERARQUIA_CARTAS = [
    "1_espadas", "1_bastos", "7_espadas", "7_ouros",
    "3_espadas", "3_bastos", "3_copas", "3_ouros",
    "2_espadas", "2_bastos", "2_copas", "2_ouros",
    "1_copas", "1_ouros",
    "12_espadas", "12_bastos", "12_copas", "12_ouros",
    "11_espadas", "11_bastos", "11_copas", "11_ouros",
    "10_espadas", "10_bastos", "10_copas", "10_ouros",
    "7_bastos", "7_copas", "6_espadas", "6_bastos", "6_copas", "6_ouros",
    "5_espadas", "5_bastos", "5_copas", "5_ouros",
    "4_espadas", "4_bastos", "4_copas", "4_ouros",
]

# Carregar as cartas
def carregar_cartas():
    cartas = {}
    for valor in [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]:
        for naipe in ["espadas", "bastos", "copas", "ouros"]:
            nome = f"{valor}_{naipe}"
            caminho = f"assets/cartas/{nome}.png"
            try:
                imagem = pygame.image.load(caminho)
                cartas[nome] = pygame.transform.scale(imagem, (80, 120))
            except pygame.error:
                print(f"Erro ao carregar a carta: {caminho}")
    return cartas

# Criar baralho
def criar_baralho():
    naipes = ["espadas", "bastos", "copas", "ouros"]
    valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
    baralho = [f"{valor}_{naipe}" for valor in valores for naipe in naipes]
    return baralho

# Distribuir cartas
def distribuir_cartas(baralho):
    random.shuffle(baralho)
    jogador1 = baralho[:3]
    jogador2 = baralho[3:6]
    return jogador1, jogador2

# Avaliar quem venceu a jogada
def avaliar_vencedor(carta1, carta2):
    index1 = HIERARQUIA_CARTAS.index(carta1)
    index2 = HIERARQUIA_CARTAS.index(carta2)

    if index1 < index2:
        return "jogador1"
    elif index1 > index2:
        return "jogador2"
    else:
        return "empate"

# Função principal do jogo
def iniciar_jogo():
    clock = pygame.time.Clock()
    running = True

    # Configurações do jogo
    cartas_imagens = carregar_cartas()
    baralho = criar_baralho()
    jogador1, jogador2 = distribuir_cartas(baralho)
    mesa = []

    # Pontuações e rodadas
    pontos_jogador1 = 0
    pontos_jogador2 = 0
    jogadas_do_round = 0
    vitorias_jogador1 = 0
    vitorias_jogador2 = 0
    turno_jogador = True  # True para jogador 1, False para jogador 2 (IA)
    resultados_turnos = ["", "", ""]  # Resultado de cada turno

    # Fundo da mesa (imagem decorativa)
    mesa_fundo = pygame.image.load("assets/mesa.png")
    mesa_fundo = pygame.transform.scale(mesa_fundo, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Imagem da carta virada
    carta_virada = pygame.image.load("assets/cartas/carta_virada.png")
    carta_virada = pygame.transform.scale(carta_virada, (80, 120))

    # Variáveis de arraste
    carta_selecionada = None
    posicao_inicial = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Evento de clique para selecionar a carta
            if event.type == pygame.MOUSEBUTTONDOWN and turno_jogador:
                mouse_pos = pygame.mouse.get_pos()
                x_offset = 200
                for i, carta in enumerate(jogador1):
                    carta_rect = pygame.Rect(x_offset, 450, 80, 120)
                    if carta_rect.collidepoint(mouse_pos):
                        carta_selecionada = carta
                        posicao_inicial = (x_offset, 450)
                        break
                    x_offset += 100

            # Soltar a carta no meio da mesa
            if event.type == pygame.MOUSEBUTTONUP and carta_selecionada:
                mouse_pos = pygame.mouse.get_pos()
                if 300 < mouse_pos[0] < 500 and 200 < mouse_pos[1] < 400:
                    mesa.append(("jogador1", carta_selecionada))
                    jogador1.remove(carta_selecionada)
                    turno_jogador = False  # Troca o turno para a IA
                    carta_selecionada = None

        # Movimento da carta durante o arraste
        if carta_selecionada and posicao_inicial:
            mouse_pos = pygame.mouse.get_pos()
            posicao_inicial = (mouse_pos[0] - 40, mouse_pos[1] - 60)

        # Turno da IA (jogador 2)
        if not turno_jogador and jogador2:
            carta_adversario = random.choice(jogador2)
            mesa.append(("jogador2", carta_adversario))
            jogador2.remove(carta_adversario)
            turno_jogador = True  # Volta o turno para o jogador 1

            # Avaliar vencedor da jogada
            if len(mesa) == 2:
                pygame.time.delay(1000)  # Adicionado delay antes de calcular o vencedor
                vencedor = avaliar_vencedor(mesa[0][1], mesa[1][1])
                if vencedor == "jogador1":
                    vitorias_jogador1 += 1
                    resultados_turnos[jogadas_do_round] = "Jogador 1"
                elif vencedor == "jogador2":
                    vitorias_jogador2 += 1
                    resultados_turnos[jogadas_do_round] = "Jogador 2"

                # Limpar a mesa e contar o turno
                mesa.clear()
                jogadas_do_round += 1

                # Verificar se alguém ganhou o round
                if vitorias_jogador1 == 2:
                    pontos_jogador1 += 1
                    vitorias_jogador1, vitorias_jogador2 = 0, 0
                    jogadas_do_round = 0
                    resultados_turnos = ["", "", ""]
                    jogador1, jogador2 = distribuir_cartas(baralho)
                elif vitorias_jogador2 == 2:
                    pontos_jogador2 += 1
                    vitorias_jogador1, vitorias_jogador2 = 0, 0
                    jogadas_do_round = 0
                    resultados_turnos = ["", "", ""]
                    jogador1, jogador2 = distribuir_cartas(baralho)

        # Desenhar a mesa
        screen.blit(mesa_fundo, (0, 0))

        # Desenhar turnos no canto esquerdo
        for i, resultado in enumerate(resultados_turnos):
            texto = FONT.render(f"{i + 1} - {resultado}", True, (255, 255, 255))
            screen.blit(texto, (50, 200 + i * 40))

        # Desenhar cartas do jogador 1
        x_offset = 200
        for carta in jogador1:
            if carta == carta_selecionada:
                screen.blit(cartas_imagens[carta], posicao_inicial)
            else:
                screen.blit(cartas_imagens[carta], (x_offset, 450))
            x_offset += 100

        # Desenhar cartas do jogador 2 (viradas para baixo)
        x_offset = 200
        for _ in jogador2:
            screen.blit(carta_virada, (x_offset, 50))
            x_offset += 100

        # Desenhar cartas na mesa
        x_offset = 300
        for _, carta in mesa:
            screen.blit(cartas_imagens[carta], (x_offset, 250))
            x_offset += 100

        # Leaderboard no lado direito
        leaderboard = [
            f"Jogador 1: {pontos_jogador1} pontos",
            f"Jogador 2: {pontos_jogador2} pontos",
        ]
        for i, linha in enumerate(leaderboard):
            texto = FONT.render(linha, True, (255, 255, 255))
            screen.blit(texto, (610, 50 + i * 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    iniciar_jogo()