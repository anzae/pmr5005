function convert_data(folder,subjs)
% FUN��O UTILIZADA APENAS PARA CONVERTER OS DADOS COLETADOS, DE TXT PARA
% MAT. UMA VEZ UTILIZADAS, POPULA AUTOMATIVAMENTE A PASTA PARA AN�LISE E
% N�O PRECISA MAIS SER UTILIZADA

%folder - qual a pasta (nome da pasta � a data) que deseja converter? [dia-mes-ano]
%subjs - quais sujeitos?

Ss1 = 'C:\Users\jeean\Desktop\Doutorado\Guid�o Rob�tico\Resultados';
S1 = 'C:\Users\jeean\Desktop\Doutorado\Guid�o Rob�tico\Resultados';
S2 = folder;
S3 = '\Subject_';

n=max(size(subjs));
for i=1:n %para cada um dos sujeitos
    
    S4 = num2str(subjs(i));
    destdirectory = strcat(Ss1,S3,S4);
    mkdir(destdirectory);   %cria o diret�rio para salvar dados
    S5 = '-';
    
    for j=1:1 %para cada uma das modalidades de teste
        switch j
            case 0
                S6 = 'TRAIN';
            case 1
                S6 = 'RAN';
            case 2
                S6 = 'CCW';
            case 3
                S6 = 'SEQ';
            case 4
                S6 = 'RAN2';
        end
        for k=1:2 %para posi��o do usu�rio (k=1) ou referencias (k=2)
            switch k
                case 1
                    S7 = '';
                    S = strcat(S2,S3,S4,S5,S6,S7);
                    data=load(S);
                    R=trata_dados(data.out);
                case 2
                    S7 = '-ref';
                    S = strcat(S2,S3,S4,S5,S6,S7);
                    data=load(S);
                    R_ref=data.out_des;
            end
        end
        Ssave = strcat(Ss1,S3,S4,'\',S6,'.mat');
        save(Ssave','R','R_ref')
    end
end

