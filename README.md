# Jogo para a disciplina PMR5005 em 2022

## Objetivos

O objetivo desse projeto é desenvolver um jogo para analisar a movimentação no guidão instrumentado do Laboratório de Biomecatrônica - Poli USP

## Instruções
---
### Arduino
---

1. Subir o arquivo Acquisition_rework_encoder.ino (encontrado na pasta others) ao Arduino do guidão. 

O arquivo contém algumas modificações em relação ao original, para melhorar a compatibilidade com o programa desenvolvido. Além disso, como o CI quebrou, precisou-se fazer algumas alterações na parte do encoder de última hora. Caso o CI volte a funcionar, pode utilizar o código Acquisition_rework.ino.

2. Manter a conexão USB ativa.

3. Colocar na tomada o motor, os sensores e o monitor.
---
### PC (jogo)
---

1. Instalar o Python3 no computador.

2. Instalar as dependências, listadas no arquivo requirements.txt

3. Abrir o arquivo consts.py e conferir as 3 configurações principais (TOGGLE_SERIAL, PORT_NAME e LEVEL).

* TOGGLE_SERIAL indica se será usada a comunicação serial ou não. É possível jogar o jogo usando apenas o teclado, para fins de testes e debug.

* PORT_NAME é o nome da porta com a qual é feita a comunicação serial com o Arduino. 

* LEVEL é o level que será jogado no jogo.

4. Rodar o jogo, arquivo game.py. O jogo pode ser iniciado com a barra de espaço ou clicando no botão Start.

5. Após o jogo, o programa vai gerar um arquivo dentro da pasta results, com a data e hora da sessão. 

6. Para gerar os gráficos correspondentes a essa sessão, copiar o nome do arquivo na linha 14 do script graphs.py e rodar.

---
### Opctional
---
1. Para testar o envio de dados do guidão, rodar o arquivo testhandlebar.py. Esse arquivo serve para verificar se o envio de dados dos sensores e do encoder estão sendo feitos corretamente. Esse script gera um arquivo .json dentro da pasta results com os dados recebidos.

2. Para simular os dados enviados pelo guidão, rodar o arquivo results_generator.py. Um arquivo .json será criado na pasta results com dados aleatórios.