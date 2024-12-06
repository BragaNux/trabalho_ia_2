import pickle

# Carregar valores de treinamento
try:
    with open('valores_estado.pkl', 'rb') as f:
        valores_estado = pickle.load(f)
    print(f"Total de estados aprendidos: {len(valores_estado)}")
    # Exibir os 10 primeiros valores para validação
    for idx, (estado, valor) in enumerate(valores_estado.items()):
        print(f"Estado {idx + 1}: {estado}, Valor: {valor}")
        if idx >= 9:  # Limitar a exibição
            break
except FileNotFoundError:
    print("Arquivo valores_estado.pkl não encontrado. Treine a IA primeiro.")
