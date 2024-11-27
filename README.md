# Truco com IA

## Descrição do Projeto
Este é um jogo de **Truco com IA** desenvolvido utilizando a biblioteca `pygame`. O objetivo principal do projeto é proporcionar uma experiência de jogo divertida, com regras clássicas do Truco e uma inteligência artificial simples para o adversário.

## Funcionalidades
- **Interface gráfica interativa** com cartas centralizadas e placares organizados.
- **Adversário controlado por IA**, que joga cartas aleatórias.
- **Placar de turnos**: Exibe o resultado de cada turno.
- **Placar de rounds**: Exibe a pontuação total dos rounds ganhos.
- **Mensagens temporárias**: Informam as ações realizadas durante o jogo, como jogadas e resultados de turnos e rounds.
- Sistema de **arraste e soltura de cartas** para o jogador humano.

## Requisitos
- Python 3.8 ou superior.
- Biblioteca `pygame` instalada.

## Instalação
1. Clone o repositório ou baixe o código-fonte.
2. Certifique-se de ter o Python e o `pygame` instalados:
   ```bash
   pip install pygame
   ```
3. Coloque as imagens das cartas e da mesa na pasta `assets/cartas`.

## Estrutura do Projeto
- **main.py**: Código principal do jogo.
- **assets/**: Contém os arquivos gráficos, como imagens das cartas e da mesa.

## Como Jogar
1. Execute o arquivo `main.py`:
   ```bash
   python main.py
   ```
2. No início do jogo, as cartas serão distribuídas automaticamente.
3. Clique e arraste as cartas do jogador para soltá-las na mesa.
4. O adversário (IA) jogará automaticamente sua carta.
5. Veja os resultados dos turnos e rounds nos placares.
6. Continue jogando até que um dos jogadores alcance 2 vitórias no turno.

## Organização da Interface
- **Cartas do jogador**: Centralizadas na parte inferior da tela.
- **Cartas da IA**: Centralizadas na parte superior da tela.
- **Mesa de jogo**: Centralizada verticalmente para exibir as cartas jogadas.
- **Placar de turnos**: Exibido à esquerda, centralizado em altura.
- **Placar de rounds**: Exibido no canto superior direito.
- **Mensagens temporárias**: Aparecem no topo central da tela para descrever ações.

## Melhorias Implementadas
- **Resolução ampliada**: Tela ajustada para 1280x720 para uma melhor experiência visual.
- **Mensagens de delay ajustadas**: Agora as mensagens aparecem uma única vez durante o delay.
- **Cartas centralizadas**: Layout refinado para alinhar as cartas ao centro horizontal.
- **Placar dinâmico**: Exibe corretamente quem venceu os turnos e os rounds.

## Futuras Melhorias
- Implementar níveis de dificuldade para a IA.
- Adicionar animações nas jogadas.
- Criar modo multijogador local ou online.

## Contribuição
Contribuições são bem-vindas! Se você deseja adicionar melhorias ou corrigir problemas, envie um pull request ou entre em contato com o desenvolvedor.

## Licença
Este projeto é de código aberto e está sob a licença MIT. Sinta-se à vontade para usar e modificar conforme necessário.

---
Divirta-se jogando **Truco com IA**!

