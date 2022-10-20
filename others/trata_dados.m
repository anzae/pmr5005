function R = trata_dados(out);
clc
% formato do dado de entrada: out = ['#T,S1,S2,S3,S4,S5,S6@E#T,S1,...#'] onde,
% T é o tempo em microsegundos
% SX é o valor medido na célula de carga X (0-8192, 13bits)
% E é o valor medido no encoder
% '#' - demarca o início da amostra / divide amostras completas
% ',' - divide dados dentro de uma mesma amostra (exceto para encoder)
% '@' - demarca o ponto onde tem-se a medida do encoder

% formato do dado de saída: R = [T;S1;S2;S3;S4;S5;S6;E,T;S1;...;E]

% descarta a primeira e/ou última amostra caso estejam incompletas
out2 = double(out);
f = find(out2==35); % ASCII 35 = "#"
% para primeira amostra
if out(1)~='#',
    out = out(f(1):end);
end
% para primeira amostra
if out(end)~='#',
    out = out(1:f(end));
end

% quantidade total de amostras válidas
out2 = double(out);
f = find(out2==35); % ASCII 35 = "#"
N = size(f,2)-1;

% criação da matriz de saída, R (vetorização dos dados)
for n = 2:N+1,
     A = out(f(n-1)+1:f(n)-1);
     A2 = double(A);
     i = find(A2==44); % ASCII 44 = ","
     g = find(A2==64); % ASCII 64 = "@"
     % encontra e armazena valores de tempo
     R(n-1,1) = str2double(A(1:i(1)-1));
     % encontra e armazena valores das células de carga
     R(n-1,2:7) = str2num(A(i(1)+1:g-1));
     % encontra e armazena valores do encoder
     R(n-1,8) = str2double(A(g+1:end));
end
end