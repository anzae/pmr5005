function run_game(sCOM)
% **run_game (teste_jogo9)**
% Desenvolvido por: Lucas Cardoso
% Data: 05/05/2019
% Baseado em "teste_jogo8"
% Utiliza arduino M0 PRO, USB conectado à porta nativa ("NATIVE PORT") 
% Para ser utilizado com programa de arduino "Impedance_Control_v5" ou mais recentes
% No prompt de comando deve ser iniciado o código "sCOM = serial('COMX');", onde X é a port na qual o arduino esta conectado
% Para tratamento dos dados utiliza-se "trata_dados.m"

close all;
clc;

%-------------------------------------------------------------------------
% Configuration of the serial communication
%-------------------------------------------------------------------------
baudrate = 2000000;
set(sCOM,'BaudRate',baudrate);
set(sCOM,'InputBufferSize',baudrate);
set(sCOM,'Terminator','');
%-------------------------------------------------------------------------
%
%-------------------------------------------------------------------------
%Ensure the figure will always display on the second screen
%-------------------------------------------------------------------------
% sz = screensize(2);
% figure('units', 'pixels', 'outerposition', sz)
% pos = get (gcf, 'position');
% set(0, 'DefaultFigurePosition', pos)
% close all

%-------------------------------------------------------------------------
%
%-------------------------------------------------------------------------
%Configuration of the game
%-------------------------------------------------------------------------
game.fig = figure();
color = get(game.fig,'Color');
set(gca,'XColor',color,'YColor',color,'TickDir','out')
hold on

game.speed = 0.5;
game.end = 0;
game.theta = 90;
game.flag = 0;
game.time = 2;
game.erro = 0.05;
game.theta_target = 90;
game.dir = 1;
game.ii = (round(rand(1)*(90)))+1;
game.cnt=1;
game.user = 100;

Ts=1/8000;
t=[0:Ts:0.1];
F_A=440; %Frequency of note A is 440 Hz
game.sound=sin(2*pi*F_A*t);

axis([-1 1 0 1.2]);
axis manual; %axis wont be resized

game.back_plot = plot(NaN,NaN);
game.pointer_plot = plot(NaN,NaN);
game.target_plot = plot(NaN,NaN);
game.status = plot(NaN,NaN);

% Create background game
r=0.08; %radius of rest and target circle

% Draw rest position (grern)
th = 0:pi/50:2*pi;
xunit = r * cos(th) + 0;
yunit = r * sin(th) + 1;
set(game.back_plot,'XData', xunit, 'YData', yunit,'Color',[0 1 0],'LineWidth',1);

% Definition of each target
x = [-cos(45*pi()/180),-cos(60*pi()/180),-cos(75*pi()/180),cos(75*pi()/180),cos(60*pi()/180),cos(45*pi()/180)]; %x coord. for each target
y = [sin(45*pi()/180),sin(60*pi()/180),sin(75*pi()/180),sin(75*pi()/180),sin(60*pi()/180),sin(45*pi()/180)]; %y coord. for each target

% Draw all targets (black)
for i=1:6,
    th = 0:pi/50:2*pi;
    xunit = r * cos(th) + x(i);
    yunit = r * sin(th) + y(i);
    game.target(i) = copyobj(game.back_plot,gca);
    set(game.target(i),'XData', xunit, 'YData', yunit,'Color',[0 0 0],'LineWidth',1);
end
%-------------------------------------------------------------------------
%
%-------------------------------------------------------------------------
% Start everything
%-------------------------------------------------------------------------
game.user1 = input('Subject #: ');
clc
%while 1,
    game.user2 = input(['Subject #: ', num2str(game.user1),'\n\n Select the mode: \n\n RAN -> 1 \n CCW -> 2 \n SEQ -> 3 \n EXIT -> 4 \n\n Input: ']);
    switch game.user2
%         case 0 % -> Training
%             break
        case 1 % -> RAN
            game.flag = 1;
            game.i=round(rand(1)*(max(size(game.target))-1))+1; %new target position
        case 2 % -> CCW
            game.flag = 2;
            game.i = 1;
            game.signal = 1;
        case 3 % -> SEQ
            game.flag = 3;
            game.seq = [3 1 5 4 2 3 6 2];
            game.i = 1;
        case 4 % -> EXIT 
            return %break
    end
    guidata(game.fig, game); 
    main_loop(game,sCOM)
    clc
    set(game.target,'Color',[0 0 0],'LineWidth',1);
%end
close all
clc
end

function main_loop(game,sCOM)
out = [];
fopen(sCOM);
fwrite(sCOM,1);
tempo_jogo = tic;
limite_jogo = 15;
limite_ciclo = 0.01;
tempo_target = tic;
limite_target = 1;
rest_flag = 1;
k=1;

while toc(tempo_jogo)<limite_jogo,
    
    tempo_ciclo = tic;
    while toc(tempo_ciclo)<limite_ciclo,
    end

    game = guidata(game.fig);
    while sCOM.BytesAvailable==0,
    end
    out1 = fscanf(sCOM,'%c',sCOM.BytesAvailable);
    out = [out out1];
    out2 = double(out1);
    f = max(find(out2==35));
    i = max(find(out2(1:f)==64));

    game.theta = (((str2double(out1(i+1:f-1)))/1800)*180)+90;

    guidata(game.fig, game);
    draw(game)

    %Training - game.flag=0
    %RAN - game.flag=1
    %CCW - game.flag=2
    %SEQ - game.flag=3

     if toc(tempo_target)>=limite_target,
         if rest_flag>0,
             set(game.back_plot,'Color',[0 1 0],'LineWidth',1);
             %marca tempo e posição desejada
             out_des(k,1) = toc(tempo_jogo); %tempo
             if game.flag ~= 3,
                 out_des(k,2) = game.i;%posição
             else
                 out_des(k,2) = game.seq(game.i);%posição
             end
             target_gen(game)
             rest_flag = -rest_flag;
             tempo_target=tic;
         else %posição de descanso
             %marca tempo e posição desejada
             out_des(k,1) = toc(tempo_jogo); %tempo
             out_des(k,2) = 0;%posição
             set(game.target,'Color',[0 0 0],'LineWidth',1);
             set(game.back_plot,'Color',[1 0 0],'LineWidth',3);
             rest_flag = -rest_flag;
             tempo_target=tic;
         end
         k=k+1;
     end
     pause(0.0000000000000001)

end

%-------------------------------------------------------------------------
% End game, close serial communication and save results
%-------------------------------------------------------------------------
fwrite(sCOM,0);
fclose(sCOM);

S1 = 'Resultados/';
S2 = date;
destdirectory = strcat(S1,S2);
mkdir(destdirectory);   %create the directory

S3 = '/Subject_';
S4 = num2str(game.user1);
S5 = '-';
switch game.user2
    case 1
        S6 = 'RAN';
    case 2
        S6 = 'CCW';
    case 3
        S6 = 'SEQ';
end
S = strcat(S1,S2,S3,S4,S5,S6);
save(S,'out')
S7 = '-ref';
S = strcat(S,S7);
save(S,'out_des')
%-------------------------------------------------------------------------
end

function draw(game)

    xx = cos(pi*game.theta/180);
    yy = sin(pi*game.theta/180);
    set(game.pointer_plot, 'XData', xx);
    set(game.pointer_plot, 'YData', yy);
    set(game.pointer_plot,'Color',[0 0 1]);
    set(game.pointer_plot,'Marker','.','MarkerSize',60);
    
end 

function target_gen(game)
    
switch game.flag
    
    case 1
    % check if is repeated (if it is red) and change in case it is
    while get(game.target(game.i),'Color')==[1 0 0],
        game.i=round(rand(1)*3)+1;
    end
    set(game.target,'Color',[0 0 0],'LineWidth',1); % Make all target position black
    set(game.target(game.i),'Color',[1 0 0],'LineWidth',3); % The target position is highlighted
    sound(game.sound,8000);
    game.i=round(rand(1)*(max(size(game.target))-1))+1; %new target position
    
    case 2
    set(game.target,'Color',[0 0 0],'LineWidth',1); % Make all target position black
    set(game.target(game.i),'Color',[1 0 0],'LineWidth',3); % The target position is highlighted
    sound(game.sound,8000);
    game.i = (game.i)+game.signal;
    if game.i>max(size(game.target)),
        game.signal = -game.signal;
        game.i = (game.i)+(2*game.signal);
    end
    if game.i<1,
        game.signal = -game.signal;
        game.i = (game.i)+(2*game.signal);
    end
    
    case 3
    set(game.target,'Color',[0 0 0],'LineWidth',1); % Make all target position black
    set(game.target(game.seq(game.i)),'Color',[1 0 0],'LineWidth',3); % The target position is highlighted
    sound(game.sound,8000);
    game.i = (game.i)+1;
    if game.i>max(size(game.seq)),
        game.i = 1;
    end
    
end
   guidata(game.fig, game);  
end

function intro(game)
prompt = '\n Training -> 0 \n RAN -> 1 \n CCW -> 2 \n SEQ -> 3 \n EXIT -> 4 \n\n Input: ';
game.user = input(prompt);
guidata(game.fig, game);
end