# Jogo para a disciplina PMR5005 em 2022

## Objetivos

O objetivo desse projeto é desenvolver um jogo para analisar a movimentação no guidão instrumentado do Laboratório de Biomecatrônica - Poli USP

## Como usar

1. Subir o arquivo Acquisition_rework.ino (encontrado na pasta others) ao Arduino do guidão. O arquivo contém algumas modificações em relação ao original, para melhorar a compatibilidade com o programa desenvolvido.

2. Instalar as dependências, listadas no arquivo requirements.txt

3. Abrir o arquivo consts.py e conferir as 3 configurações principais.

4. (opcional) Para jogar o tutorial, alterar a constante LEVEL para 'level_0'. Senão, deixar em 'level_1'.

5. (opcional) Para testar o envio de dados do guidão, rodar o arquivo testhandlebar.py dentro da pasta others. Seguir para o passo 7.

6. Rodar o jogo, arquivo game.py. O jogo pode ser iniciado com a barra de espaço ou clicando no botão Start.

7. Após o jogo, o programa vai gerar um arquivo dentro da pasta results, com a data e hora da sessão. Copiar o nome desse arquivo e substituir na linha 38 do arquivo graphs.py. Rodar o arquivo.