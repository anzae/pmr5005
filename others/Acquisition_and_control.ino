// **Acquisition and Control v3**
// Desenvolvido por: Lucas Cardoso
// Data: 15/01/2019
// PID baseado em: "teste_PID_v3"(baseado em: PID Class by Ivan Seidel - GitHub.com/ivanseidel)
// Utiliza arduino M0 PRO, USB conectado à porta nativa ("NATIVE PORT") 
// Realiza a quadratura do encoder através do chip HCTL-2022 (utiliza o código "teste_chip_quad_encoder_v4")
// Controla o motor pela ponte H IBT_2
// Realiza leitura e conversão AD em alta velocidade através de acesso direto aos registradores (previamente desenvolvido em "Acquisition_v1")
// Utiliza programa Matlab "teste_jogo6"

// Global preamble
#include "Arduino.h"
#include "wiring_private.h"

//##############################################################################
// Classe do controlador PID
// Baseado em: PID Class by Ivan Seidel (GitHub.com/ivanseidel)
////##############################################################################
class PID{
  public:
  
  double error;
  double sample;
  double lastSample;
  double kP, kI, kD;      
  double P, I, D;
  double pid;
  double setPoint;
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
    pid = abs(((P + I + D)/1)*243)+12;//setPoint
    
    return pid;
  }
};


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

// Para o PID
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
double err;
double control;

// Outros
unsigned long inicio = 0;
unsigned long fim = 0;


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

PID myPid(1, 0, 0);


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
  // PID setup stuff
  //###################################################################################
   for (int pin = 0; pin < 8; pin++) {
    pinMode(chipQuad_pins[pin], INPUT);
  }

  pinMode(EON,OUTPUT);
  pinMode(SEL1,OUTPUT);
  pinMode(RSTN,INPUT);
  digitalWrite(RSTN,HIGH);
  pinMode(pinCONTROL_LH, OUTPUT);
  pinMode(pinCONTROL_RH, OUTPUT);
  
  myPid.setSetPoint(30);
}

void loop() {
  while (start_flag==48){ // 48 é o zero do ASCII
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
  
  while (start_flag==49){ // 49 é ASCII para 1

    // Para o ADC
    //Acquisition Bloc -----------------------------------
    sensor1 = anaRead(A0);
    sensor2 = anaRead(A1);
    sensor3 = anaRead(A2);
    sensor4 = anaRead(A3);
    sensor5 = anaRead(A4);
    sensor6 = anaRead(A5);
    tempo = micros();
    //Bloc duration = 259us
    //---------------------------/-------------------------

  
    // Para o PID
    /** ----- 1. READ -----**/
    // Lê posição atual
    read_pos();
    pos_encoder = ((count*0.005)/180)*3.14156;//((count)/200.0)*3.14156; <- para outro motor com encoder diferente
    // pos_encoder = count;


    /** ----- 2. CALC -----**/
    // Manda posição lida para o controlador
    myPid.addNewSample(pos_encoder);
  
    // Calcula erro baseado no setpoint definido
    err = myPid.calc_error();
  
    // Calcula ganho baseado nas constantes do controlador e no erro medido
    control = myPid.process();


    /** ----- 3. ACT -----**/
  
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
    SerialUSB.print("#");
    SerialUSB.print((tempo-t_start));
    SerialUSB.print(",");
    SerialUSB.print(sensor1);
    SerialUSB.print(",");
    SerialUSB.print(sensor2);
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
    //Bloc duration = 462us
    //---------------------------/-------------------------

    if (SerialUSB.available()>0){
      start_flag = SerialUSB.read();
    }
    //tempo total do bloco = 3 us
    //---------------------------/-------------------------

  // min 1fps + block duration + folga
  delay(40);

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
  //delay(25);
  //delay(5);

  
  //Read LSB
  digitalWrite(SEL1,HIGH); //LSB
  digitalWrite(EON,LOW); //Enable OE

  
  read_LSB();
  result_LSB = result_LSB_new;
  
  digitalWrite(SEL1,LOW); //MSB
  
  read_MSB();
  result_MSB = result_MSB_new;
  
  digitalWrite(EON,HIGH); //Disable OE
  //delay(5);

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
