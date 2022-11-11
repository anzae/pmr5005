// **Impedance Control v5**
// Desenvolvido por: Lucas Cardoso
// Data: 05/05/2019
// PID baseado em: "teste_PID_v3"(baseado em: PID Class by Ivan Seidel - GitHub.com/ivanseidel)
// Utiliza arduino M0 PRO, USB conectado à porta nativa ("NATIVE PORT") 
// Realiza a quadratura do encoder através do chip HCTL-2022 (utiliza o código "teste_chip_quad_encoder_v4")
// Controla o motor pela ponte H IBT_2
// Realiza leitura e conversão AD em alta velocidade através de acesso direto aos registradores (previamente desenvolvido em "Acquisition_v1")
// Utiliza programa Matlab "teste_jogo9" entre outros
// VERSÃO 5: Codigo final para experimentos

// Global preamble
#include "Arduino.h"
#include "wiring_private.h"

//##############################################################################
// Classe do controlador PID
// Baseado em: PID Class by Ivan Seidel (GitHub.com/ivanseidel)
//##############################################################################
class PID{
  public:
  
  double error;
  double sample;
  double lastSample;
  double kP, kI, kD;      
  double P, I, D;
  double pid;
  double setPoint;
  double Ref;
  long lastProcess;
  
  PID(double _kP, double _kI, double _kD){
    kP = _kP;
    kI = _kI;
    kD = _kD;
  }
  
  void addNewSample(double _sample){
    sample = _sample;
  }
  
  void setSetPoint(double _setPoint){
    setPoint = _setPoint;
  }

  void setRef(double _Ref){
    Ref = _Ref;
  }

  double calc_error(){
    error = setPoint - sample;
    return error;
  }
  
  double process(){
    // Implementação PID
    float deltaTime = (millis() - lastProcess) / 1000.0;
    lastProcess = millis();
    
    //P
    P = error * kP;
    
    //I
    I = I + (error * kI) * deltaTime;
    // if para zerar erro integral
    
    //D
    D = (lastSample - sample) * kD / deltaTime;
    lastSample = sample;


    // Soma tudo
    pid = abs(((P + I + D)/1.0)*238)+17;

    return pid;
  }
};
//##############################################################################

// Wait for synchronization of registers between the clock domains
// ADC
static __inline__ void ADCsync() __attribute__((always_inline, unused));
static void   ADCsync() {
  while (ADC->STATUS.bit.SYNCBUSY == 1); //Just wait till the ADC is free
}

// Definição de variáveis
// Para o ADC
uint32_t sensor1 = 0;
uint32_t sensor2 = 0;
uint32_t sensor3 = 0;
uint32_t sensor4 = 0;
uint32_t sensor5 = 0;
uint32_t sensor6 = 0;
uint32_t tempo = 0;
unsigned long t_start = 0; //tempo do contador no início do experimento (utilizado para cálculo do tempo do experimento)
unsigned int start_flag = 48; //indica o início do experimento - arduíno inicía coleta de dados

// Para a QUADRATURA
unsigned long result_LSB_new;
unsigned long result_LSB_old;
unsigned long result_MSB_new;
unsigned long result_MSB_old;
unsigned long result_LSB;
unsigned long result_MSB;
unsigned long result;
short count=0; // necessário ser short (16-bit) para que funcione a operação automática de complento de 2 e a variável seja lida como negativa quando msbit é HIGH
int chipQuad_pins[] = {4,5,11,13,10,12,6,7};
double pos_encoder=0;

// Para o PID
double err;
double control;

// Para o CTRL DE IMPEDÂNCIA

// Baixa Impedância
//  double I_c = 0.000052;
//  double B_c = 0.00001;
//  double K_c = 0.0002;

// Alta Impedância
//double I_c = -0.0013;
//double B_c = 0.00025;
//double K_c = 0.005;
//double K_c = 0.5;

//Impedância teste
//double I_c = 

double I_c = 0;//0.00012;//0.00006;//0.000006;//0.00006;//0.0006;//0.006;//0.15;//0.000001;
double B_c = 0.000001;//0.00004;//0.002;//0.000002;//0.00002;//0.0002;//0.002;//0.05;//0.000001;
double K_c = 0.000001;//0.0002;//0.000004;//0.00004;//0.0004;//0.004;//0.02;//0.000001;

double x_0 = 0;
double I = 0.00003;
double B = 0.05;

double K = 0.661115030403304; //ganho do motor (determinado experimentalmente)
double tau =  0.051279328086485; //cte de tempo do motor (determinado experimentalmente)
double Im = 600.0/10000.0; //momento de inercia do eixo do motor (em kg.m²)
double Ra = 1.4; //resistência do enrolamento de armadura do motor (em ohms)


signed int D;
double T;
double T_act;
double spd;
double Va;
double x_2, t_2;
double t_1 = 0;
double x_1 = 0;
double x = 0;
double td_1, td_2;
double avv_ref = 0;
double a = 0;
double b = 0;

// Para a MÉDIA MÓVEL
const int numReadings = 250; // tamanho da média móvel
signed int readings[numReadings]; // vetor com medidas para cálculo da média móvel
signed int teste;
signed int teste2;
signed int teste3;
int readIndex = 0; // indice da medida atual de força
signed int total = 0; // soma total dos valores medidos
signed int average = 0; // média

// Para a MÉDIA MÓVEL de X
const int numReadingss = 50;//12; // tamanho da média móvel
signed int readingss[numReadingss]; // vetor com medidas para cálculo da média móvel
int readIndexs = 0; // indice da medida atual de força
signed int totals = 0; // soma total dos valores medidos
signed int averages = 0; // média
double avv = 0;

// Outros
unsigned long inicio = 0;
unsigned long fim = 0;
int acc=0;
unsigned long t1=0; 
unsigned long t2=0;
double sinal;


long tempo_teste = 0;
long tempo_teste2 = 0;

int constante_multiplicativa_magica = 1;


// Definições
//RESET - zera a leitura do encoder
#define RSTN 0

//Habilita/Desabilita leitura (CHIP DE QUADRATURA: pino ?)
#define EON 2

//Escolhe Byte para leitura - MSB: SEL1=0 / LSB: SEL1=1 (CHIP DE QUADRATURA: pino ?) 
#define SEL1 3

//Ativação do motor por PWM (PONTE H: pino )
#define pinCONTROL_RH 8
#define pinCONTROL_LH 9   

//PID myPid(0.4, 0, 0.005);
//PID myPid(0.3, 0, 0.01);
PID myPid(0.3, 0, 0.05);

void setup() {
  SerialUSB.begin(2000000);//inicia a comunicação serial
  
  //###################################################################################
  // ADC setup stuff
  //###################################################################################
  ADCsync();
  ADC->INPUTCTRL.bit.GAIN = ADC_INPUTCTRL_GAIN_DIV2_Val;    // Gain select as 2X
  ADCsync();
  ADC->REFCTRL.bit.REFSEL = ADC_REFCTRL_REFSEL_INTVCC1_Val; //  1/2 VDDANA

  // As 4 linhas de código acima fazem: multiplica o ganho da referência por 2 e utiliza referência como 3.3V / 2 = 1.65V. 
  // Com ganho 2, temos que a referência do ADC será justamente VDDANA, ou seja, 3.3V 

  ADCsync();
  ADC->AVGCTRL.reg = 0x12; //13-bit
  ADCsync();
  ADC->SAMPCTRL.reg = 0x0; //sample length in 1/2 CLK_ADC cycles Default is 3F
  
  //Control B register
  int16_t ctrlb = 0x410; // Control register B hibyte = prescale, lobyte is resolution and mode 
  ADCsync();
  ADC->CTRLB.reg = ctrlb; 
  
  //Discard first conversion after setup as ref changed
  sensor1 = anaRead(A0);
  sensor2 = anaRead(A1);
  sensor3 = anaRead(A2);
  sensor4 = anaRead(A3);
  sensor5 = anaRead(A4);
  sensor6 = anaRead(A5);

  //###################################################################################
  // Inicializa vetor para o chip de quadratura
  //###################################################################################
   for (int pin = 0; pin < 8; pin++) {
    pinMode(chipQuad_pins[pin], INPUT);
  }
  
  //########### ########################################################################
  // Inicializa vetor para a média móvel
  //###################################################################################
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings[thisReading] = 0;
  }

    //###################################################################################
  // Inicializa vetor para a média móvel de X
  //###################################################################################
  for (int thisReadings = 0; thisReadings < numReadingss; thisReadings++) {
    readingss[thisReadings] = 0.0;
  }
  
  pinMode(EON,OUTPUT);
  pinMode(SEL1,OUTPUT);

  pinMode(RSTN,INPUT);
  digitalWrite(RSTN,HIGH);
  pinMode(pinCONTROL_LH, OUTPUT);
  pinMode(pinCONTROL_RH, OUTPUT);
  
}

void loop() {
  while (start_flag==48){ 
    count=0;
    digitalWrite(RSTN,LOW);
    digitalWrite(RSTN,HIGH);
    analogWrite(pinCONTROL_LH, 0);
    analogWrite(pinCONTROL_RH, 0);
    if (SerialUSB.available()>0){
      start_flag = SerialUSB.read();
    }
  }
  
  t_start = micros();
 
  while (start_flag!=48){


    if (millis() - tempo_teste > 40) {
      tempo_teste = millis();
      SerialUSB.print("#");
      SerialUSB.print((tempo));
      SerialUSB.print(",");
      SerialUSB.print(sensor1);//avv);
      SerialUSB.print(",");
      SerialUSB.print(sensor2);//T/100000.0);
      SerialUSB.print(",");
      SerialUSB.print(sensor3);
      SerialUSB.print(",");
      SerialUSB.print(sensor4);
      SerialUSB.print(",");
      SerialUSB.print(sensor5);
      SerialUSB.print(",");
      SerialUSB.print(sensor6);
      SerialUSB.print("@");
      SerialUSB.print(count);
      SerialUSB.print("\n");
    }


    // if (millis() - tempo_teste2 > 2000) {
    //   I_c = -I_c;
    //   tempo_teste2 = millis();
    // }



    // delay(2);
    // Para o ADC
    //Acquisition Bloc -----------------------------------
    sensor1 = anaRead(A0);
    sensor2 = anaRead(A1);
    sensor3 = anaRead(A2);
    sensor4 = anaRead(A3);
    sensor5 = anaRead(A4);
    sensor6 = anaRead(A5);
    //Bloc duration = 259us
    //---------------------------/-------------------------
  
    // Para o PID e CRTL IMPEDÂNCIA
    /** ----- 1. READ -----**/
    // Lê posição atual
    t_2 = t_1;
    t_1 = tempo;
    //t1=micros();
    tempo = micros()-t_start;
    read_pos();
    x_2 = x_1;
    x_1 = pos_encoder;
    pos_encoder = ((count)/36000.0)*3.14156;

    /** ----- 2. CALC POSIÇÃO REF -----**/

    // subtract the last reading:
    total = total - readings[readIndex];
    // read from the sensor:
    teste = sensor2;//sensor3 + sensor4 - 8192;
    teste2 = -(sensor6-4096);
    teste3 = -(sensor1-4096);
    readings[readIndex] = 1.0*teste + 0.0*teste2 + 0.0*teste3;//(sensor4 - 4096);

    //readings[readIndex] = (sensor3 - 4096)+(4096 - sensor2)/100.0;
    // add the reading to the total:
    total = total + readings[readIndex];
    // advance to the next position in the array:
    readIndex = readIndex + 1;

    // if we're at the end of the array...
    if (readIndex >= numReadings) {
    // ...wrap around to the beginning:
    readIndex = 0;
    }

    // calculate the average:
    average = total / numReadings;

    T = (average*100000.0/4096.0)*5*10*0.12*0.8; //T em [N.m]
    
    td_1 = (tempo - t_1)/1000000.0;
    td_2 = (t_1 - t_2)/1000000.0;

    a = I_c/(td_1*td_1);
    b = B_c/(td_1);

    x = (((T/100000.0) + (x_1*((2*a)+b)) - (x_2*a) - (K_c*x_0)) / (a+b-K_c))*1000.0;
    
    if (x > 180) {
      x = 180;
    }

    if (x < -270) {
      x = -270;
    }
  
    // subtract the last reading:
    totals = totals - readingss[readIndexs];;
    // read from the sensor:
    readingss[readIndexs] = x;
    // add the reading to the total:
    totals = totals + readingss[readIndexs];
    // advance to the next position in the array:
    readIndexs = readIndexs + 1;

    // if we're at the end of the array...
    if (readIndexs >= numReadingss) {
    // ...wrap around to the beginning:
    readIndexs = 0;
    }

    // calculate the average:
    averages = totals / numReadingss;

    x_2 = x_1;
    x_1 = avv;
    avv = averages/1000.0 * constante_multiplicativa_magica;

    myPid.setSetPoint(avv);

    /** ----- 3. CALC PID -----**/
    // Manda posição lida para o controlador
    myPid.addNewSample(pos_encoder);
  
    // Calcula erro baseado no setpoint definido
    err = myPid.calc_error();
  
    // Calcula ganho baseado nas constantes do controlador e no erro medido
    control = myPid.process();

   if (control>120){
     control = 120;
   } 

   if (control < -120) {
     control = -120;
   }


    /** ----- 4. ACT PID -----**/
    // Seleciona o sentido de rotação do motor 
    if (err < 0) {
      digitalWrite(pinCONTROL_RH,LOW);
      analogWrite(pinCONTROL_LH, control);
    } else {
      digitalWrite(pinCONTROL_LH,LOW);
      analogWrite(pinCONTROL_RH, control);
    }

    // Para o envio de informação
    //Send Information Bloc -------------------------------
    // SerialUSB.print("#");
    // SerialUSB.print((tempo));
    // SerialUSB.print(",");
    // SerialUSB.print(sensor1);//avv);
    // SerialUSB.print(",");
    // SerialUSB.print(sensor2);//T/100000.0);
    // SerialUSB.print(",");
    // SerialUSB.print(sensor3);
    // SerialUSB.print(",");
    // SerialUSB.print(sensor4);
    // SerialUSB.print(",");
    // SerialUSB.print(sensor5);
    // SerialUSB.print(",");
    // SerialUSB.print(sensor6);
    // SerialUSB.print("@");
    // SerialUSB.print(count);
    // SerialUSB.print("\n");
    //Bloc duration = 462us
    //---------------------------/-------------------------

    if (SerialUSB.available()>0){
      start_flag = SerialUSB.read();
    }
    //tempo total do bloco = 3 us
    //---------------------------/-------------------------

    // impedância sentido anti-horário
    if (start_flag == 50) { // número 2 na serial
      I_c = 0.000001;;
      constante_multiplicativa_magica = 0;
    }

    // impedância sentido horário
    if (start_flag == 51) { // número 3 na serial
      I_c = -0.000001;
      constante_multiplicativa_magica = 1;
    }

    // impedância no zero
    if (start_flag == 52) { // número 4 na serial
      constante_multiplicativa_magica = 0;
    }
  }
}

//##############################################################################
// Stripped-down fast analogue read anaRead()
// ulPin is the analog input pin number to be read.
////##############################################################################
uint32_t anaRead(uint32_t ulPin) {

  ADCsync();
  ADC->INPUTCTRL.bit.MUXPOS = g_APinDescription[ulPin].ulADCChannelNumber; // Selection for the positive ADC input

  ADCsync();
  ADC->CTRLA.bit.ENABLE = 0x01;             // Enable ADC

  ADC->INTFLAG.bit.RESRDY = 1;              // Data ready flag cleared

  ADCsync();
  ADC->SWTRIG.bit.START = 1;                // Start ADC conversion

  while ( ADC->INTFLAG.bit.RESRDY == 0 );   // Wait till conversion done
  ADCsync();
  uint32_t valueRead = ADC->RESULT.reg;

  ADCsync();
  ADC->CTRLA.bit.ENABLE = 0x00;             // Disable the ADC 
  ADCsync();
  ADC->SWTRIG.reg = 0x01;                    //  and flush for good measure
  return valueRead;
}
//##############################################################################

inline int digitalRead_fast(){
result = (PORT->Group[0].IN.reg & (PORT_PA14 | PORT_PA15 | PORT_PA16 | PORT_PA17 | PORT_PA18 | PORT_PA19 | PORT_PA20 | PORT_PA21));
return result;
}

void read_pos() {
  digitalWrite(EON,HIGH); //Disable OE
  
  //Read LSB
  digitalWrite(SEL1,HIGH); //LSB
  digitalWrite(EON,LOW); //Enable OE
  
  read_LSB();
  result_LSB = result_LSB_new;
  
  digitalWrite(SEL1,LOW); //MSB
  
  read_MSB();
  result_MSB = result_MSB_new;
  
  digitalWrite(EON,HIGH); //Disable OE

  count = result_LSB >> 14 | result_MSB >> 6;
}

void read_MSB(){
  result_MSB_old = digitalRead_fast();
  result_MSB_new = digitalRead_fast();

  if(result_MSB_new != result_MSB_old){
    read_MSB();
  }
}

void read_LSB(){
  result_LSB_old = digitalRead_fast();
  result_LSB_new = digitalRead_fast();

  if(result_LSB_new != result_LSB_old){
    read_LSB();
  }
}
