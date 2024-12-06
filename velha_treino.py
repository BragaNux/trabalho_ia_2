import random
import pickle
import numpy as np
import tensorflow as tf

# Configurações de IA e treinamento
linhas, colunas = 3, 3
jogador_x = 1
jogador_o = -1
epsilon = 0.1  # Probabilidade inicial de exploração
epsilon_decay = 0.9999  # Decaimento mais lento para garantir exploração suficiente
min_epsilon = 0.05  # Limite mínimo de exploração
gamma = 0.95   # Fator de desconto
alpha = 0.1    # Taxa de aprendizado

# Carregar valores de estados aprendidos anteriormente
try:
    with open('valores_estado.pkl', 'rb') as f:
        valores_estado = pickle.load(f)
    print(f"Total de estados aprendidos: {len(valores_estado)}")
except FileNotFoundError:
    print("Arquivo valores_estado.pkl não encontrado. Treine a IA primeiro.")
    valores_estado = {}

# Modelo TensorFlow aprimorado
modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(9,)),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(9, activation='linear')
])
modelo.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005), loss=tf.keras.losses.MeanSquaredError())

# Função para verificar vencedor
def verificar_vencedor(tabuleiro):
    for i in range(linhas):
        if sum(tabuleiro[i]) in [3 * jogador_x, 3 * jogador_o]:
            return tabuleiro[i][0]
        if sum([tabuleiro[j][i] for j in range(colunas)]) in [3 * jogador_x, 3 * jogador_o]:
            return tabuleiro[0][i]

    diagonal_principal = sum(tabuleiro[i][i] for i in range(linhas))
    diagonal_secundaria = sum(tabuleiro[i][linhas - i - 1] for i in range(linhas))
    if diagonal_principal in [3 * jogador_x, 3 * jogador_o]:
        return tabuleiro[0][0]
    if diagonal_secundaria in [3 * jogador_x, 3 * jogador_o]:
        return tabuleiro[0][linhas - 1]

    return 0

# Identificar situações de cerco
def identificar_cerco(tabuleiro, jogador):
    jogadas_possiveis = [(i, j) for i in range(linhas) for j in range(colunas) if tabuleiro[i][j] == 0]
    ameacas = 0

    for linha, coluna in jogadas_possiveis:
        tabuleiro[linha][coluna] = jogador
        if verificar_vencedor(tabuleiro) == jogador:
            ameacas += 1
        tabuleiro[linha][coluna] = 0

    return ameacas >= 2

# Atualizar valores de estados aprendidos
def atualizar_valores_estado(estado_atual, recompensa):
    global valores_estado
    estado_chave = tuple(estado_atual.flatten())
    valores_estado[estado_chave] = valores_estado.get(estado_chave, 0) + alpha * (recompensa - valores_estado.get(estado_chave, 0))

# IA para realizar jogadas
def jogada_ia(tabuleiro, jogador):
    estado_atual = np.array(tabuleiro).flatten().reshape(1, -1)
    escolhas_possiveis = [(i, j) for i in range(linhas) for j in range(colunas) if tabuleiro[i][j] == 0]

    if not escolhas_possiveis:
        return

    previsoes = modelo.predict(estado_atual, verbose=0)[0]
    q_values = [previsoes[i * colunas + j] for i, j in escolhas_possiveis]
    melhor_jogada = escolhas_possiveis[np.argmax(q_values)]

    tabuleiro[melhor_jogada[0]][melhor_jogada[1]] = jogador

# Treinamento otimizado
def treinar_ia(max_rodadas=1_000_000):
    global valores_estado, epsilon
    rodadas = 0
    ataque_count = 0
    defesa_count = 0
    cerco_count = 0

    try:
        print("Iniciando o treinamento da IA...")
        while rodadas < max_rodadas:
            tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
            jogador_atual = jogador_x
            rodando = True

            while rodando:
                estado_atual = np.array(tabuleiro).flatten()
                vencedor = verificar_vencedor(tabuleiro)

                if vencedor != 0:
                    recompensa = 10 if vencedor == jogador_x else -10
                    atualizar_valores_estado(np.array(tabuleiro), recompensa)
                    rodando = False
                    if vencedor == jogador_x:
                        ataque_count += 1
                elif all(tabuleiro[i][j] != 0 for i in range(linhas) for j in range(colunas)):
                    recompensa = 1  # Empate tem baixa recompensa
                    atualizar_valores_estado(np.array(tabuleiro), recompensa)
                    rodando = False
                else:
                    if jogador_atual == jogador_o:
                        # Defesa contra vitória iminente
                        jogadas_possiveis = [(i, j) for i in range(linhas) for j in range(colunas) if tabuleiro[i][j] == 0]
                        for linha, coluna in jogadas_possiveis:
                            tabuleiro[linha][coluna] = jogador_x
                            if verificar_vencedor(tabuleiro) == jogador_x:
                                recompensa = 5
                                atualizar_valores_estado(np.array(tabuleiro), recompensa)
                                defesa_count += 1
                            tabuleiro[linha][coluna] = 0

                        # Penalizar cerco
                        if identificar_cerco(tabuleiro, jogador_x):
                            recompensa = 3
                            atualizar_valores_estado(np.array(tabuleiro), recompensa)
                            cerco_count += 1

                    jogada_ia(tabuleiro, jogador_atual)
                    jogador_atual = jogador_o if jogador_atual == jogador_x else jogador_x

            rodadas += 1
            if rodadas % 10_000 == 0:
                epsilon = max(epsilon * epsilon_decay, min_epsilon)
                print(f"Rodadas: {rodadas}, Ataques: {ataque_count}, Defesas: {defesa_count}, Cercos evitados: {cerco_count}")

    except KeyboardInterrupt:
        print("Treinamento interrompido manualmente. Salvando progresso...")
    finally:
        # Salvar progresso
        with open('valores_estado.pkl', 'wb') as f:
            pickle.dump(valores_estado, f)
        modelo.save('modelo_treinado.h5')
        print("Progresso salvo:")
        print(f" - Modelo salvo em 'modelo_treinado.h5'")
        print(f" - Estados salvos em 'valores_estado.pkl'")
        print(f"Resumo final - Rodadas: {rodadas}, Ataques: {ataque_count}, Defesas: {defesa_count}, Cercos evitados: {cerco_count}")

if __name__ == "__main__":
    treinar_ia()
