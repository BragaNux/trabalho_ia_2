# #️⃣ Treinamento da IA no Jogo da Velha

## Visão Geral

Este documento descreve o desenvolvimento e o treinamento de uma inteligência artificial para jogar "Jogo da Velha" utilizando a biblioteca Pygame, TensorFlow e Python. A IA foi programada para competir contra o jogador humano e também realizar partidas de auto-treinamento em cenários de 9 jogos simultâneos.

## Objetivo

O objetivo deste projeto é desenvolver uma IA suficientemente inteligente para jogar o Jogo da Velha sem perder contra um jogador humano, mesmo quando este tentar usar táticas estratégicas como cercos (situações em que o jogador humano se posiciona para vencer em duas ou mais opções ao mesmo tempo).

A IA utiliza aprendizado por reforço e uma rede neural treinada para aprender a melhor forma de evitar perder partidas e buscar empatar quando o adversário tentar uma tática estratégica.

## Por que Mudei para o Jogo da Velha

Inicialmente, o projeto estava focado em desenvolver uma IA para o jogo de Truco. No entanto, algumas dificuldades técnicas e de design acabaram motivando a mudança para o Jogo da Velha. Entre os principais desafios encontrados no desenvolvimento da IA para o Truco, destacam-se:

1. **Complexidade das Regras**: O Truco é um jogo que envolve muitas variáveis, incluindo blefes, leitura de comportamento do adversário e combinações específicas de cartas. Isso tornou a modelagem da IA muito complexa em relação às ferramentas que eu tinha disponíveis.

2. **Dificuldade em Simular Blefes**: Ensinar uma IA a blefar ou interpretar blefes é um desafio significativo que exige métodos avançados de aprendizado de máquina. Esses aspectos tornaram o progresso mais lento do que o esperado.

3. **Limitações no Tempo Disponível**: O desenvolvimento de uma IA para Truco requer um tempo considerável de pesquisa, teste e ajuste fino. Com as limitações de tempo, decidi redirecionar meus esforços para um projeto mais viável no curto prazo.

Por outro lado, o Jogo da Velha apresentou-se como uma alternativa mais adequada para o momento, permitindo que eu aplicasse técnicas de aprendizado por reforço de maneira eficaz e ao mesmo tempo tivesse um escopo gerenciável.

## Ferramentas Utilizadas

- **Python**: Linguagem de programação usada no desenvolvimento do código.
- **Pygame**: Biblioteca para criar interfaces gráficas e simular o tabuleiro do jogo.
- **TensorFlow**: Biblioteca de aprendizado de máquina para criar, treinar e ajustar a rede neural que compõe a IA.
- **Pickle**: Utilizado para salvar estados do tabuleiro aprendidos anteriormente.

## Estratégia de Treinamento

1. **Treinamento em Auto-Competição**: A IA foi configurada para jogar contra si mesma em 9 jogos simultâneos. Isso ajuda a explorar várias possibilidades de jogadas e melhorar o aprendizado de estratégias.

2. **Treinamento Baseado em Jogos Significativos**: Para acelerar o aprendizado, a IA só salva estados de jogos que foram considerados significativos, como partidas em que ocorreu empate ou situações em que a IA evitou um cerco. Esse mecanismo visa evitar o armazenamento de estados triviais e focar nos aspectos mais desafiadores do jogo.

3. **Verificação de Cercos**: Foi implementada uma função específica que detecta cercos criados pelo adversário. Essa função é utilizada para garantir que a IA possa reagir adequadamente ao evitar perder em cenários em que o adversário tenha duas opções de vitória.

4. **Utilização de Softmax para Escolhas**: A função softmax é utilizada para converter os valores de Q em probabilidades, permitindo uma tomada de decisão mais flexível e exploratória. Isso é importante para garantir que a IA explore o espaço de solução e, ao mesmo tempo, aprenda a priorizar jogadas mais vantajosas.

## Atualizações Recentes

1. **Salvamento de Estados e Modelo**: Foi implementado um mecanismo para salvar o modelo treinado em formato `.h5` e os estados aprendidos em um arquivo `valores_estado.pkl` ao final de cada sessão de treinamento, garantindo que o progresso não seja perdido.

2. **Problemas no Salvamento**: Identificou-se que, em algumas execuções, o modelo salvo não refletia o aprendizado esperado. Apesar de os arquivos serem gerados, o desempenho da IA em partidas contra humanos indicava que ela não utilizava plenamente o que havia sido treinado.

3. **Jogadas Iminentes e Cercos**: A IA foi programada para priorizar, em primeiro lugar, jogadas que garantem sua própria vitória. Caso não exista essa possibilidade, ela verifica se o adversário está próximo de vencer e bloqueia a jogada. Se não houver jogadas iminentes, ela tenta prever cercos e bloqueá-los.

4. **Limitações Observadas**: Apesar dos ajustes, a IA ainda apresenta comportamento subótimo em situações de cerco e, em muitos casos, realiza jogadas aleatórias que sugerem falta de aprendizado consistente.

## Resultados Observados

Nos testes recentes, foi observado que a IA ainda comete erros que permitem ao jogador humano vencer, principalmente em situações de cerco. Além disso, o progresso em evitar derrotas e empatar jogos parece ser inconsistente, mesmo após longos períodos de treinamento.

Embora a IA consiga aumentar a quantidade de empates e vitórias contra si mesma em cenários de auto-treinamento, sua performance contra jogadores humanos continua aquém do esperado. Os testes sugerem que o problema pode estar relacionado ao salvamento ou carregamento inadequado do modelo treinado.

## Próximos Passos

- **Verificação do Processo de Salvamento e Carregamento**: Garantir que o modelo treinado está sendo salvo corretamente e que os pesos aprendidos estão sendo utilizados durante os jogos contra humanos.
- **Revisão do Algoritmo de Treinamento**: Analisar e ajustar o algoritmo de treinamento para garantir que a IA esteja realmente aprendendo com as partidas realizadas.
- **Aprimorar Detecção de Cenários Críticos**: Melhorar a função de verificação de cercos para que a IA se torne mais eficiente em identificar e evitar situações críticas.
- **Revisão dos Pesos de Recompensa**: Ajustar os pesos das recompensas para otimizar o aprendizado, buscando uma distribuição que incentive o comportamento defensivo e ofensivo de forma equilibrada.

## Como Executar

1. **Instalar Dependências**: Certifique-se de instalar as dependências necessárias, incluindo Pygame, TensorFlow e Pickle:
   ```sh
   pip install pygame tensorflow
   ```

2. **Executar o Jogo**: Para iniciar o treinamento ou jogar contra a IA, execute o script principal:
   ```sh
   python jogo_da_velha.py
   ```

## Considerações Finais

Apesar de esforços significativos, a IA ainda não alcançou o nível esperado de inteligência para competir contra jogadores humanos de forma consistente. O projeto destaca os desafios práticos de aplicar aprendizado por reforço em jogos estratégicos, mesmo em cenários simples como o Jogo da Velha.

Com ajustes contínuos no treinamento, salvamento e detecção de cenários críticos, espera-se que a IA evolua para um nível em que possa empatar ou vencer consistentemente. Por ora, os resultados reforçam a importância de um ciclo iterativo de testes e melhorias para alcançar os objetivos desejados.
