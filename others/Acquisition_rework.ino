// **Impedance Control v5**
// Desenvolvido por: Lucas Cardoso
// Data: 05/05/2019
// PID baseado em: "teste_PID_v3"(baseado em: PID Class by Ivan Seidel - GitHub.com/ivanseidel)
// Utiliza arduino M0 PRO, USB conectado à porta nativa ("NATIVE PORT")
// Realiza a quadratura do encoder através do chip HCTL-2022 (utiliza o código "teste_chip_quad_encoder_v4")
// Controla o motor pela ponte H IBT_2
// Realiza leitura e conversão AD em alta velocidade através de acesso direto aos registradores (previamente desenvolvido em "Acquisition_v1")
// Utiliza jogo em python pela comunicação serial
// Versão 6: modificado por Ana

// Global preamble
#include "Arduino.h"
#include "wiring_private.h"

  //RESET - zera a leitura do encoder
  #define RSTN 0

  //Habilita/Desabilita leitura (CHIP DE QUADRATURA: pino ?)
  #define EON 2

  //Escolhe Byte para leitura - MSB: SEL1=0 / LSB: SEL1=1 (CHIP DE QUADRATURA: pino ?)
  #define SEL1 3

//Ativação do motor por PWM (PONTE H: pinos 8 (direita) e 9 (esquerda))
  #define pinCONTROL_RH 8
  #define pinCONTROL_LH 9

//##############################################################################
// Classe do controlador PID
// Baseado em: PID Class by Ivan Seidel (GitHub.com/ivanseidel)
//##############################################################################
class PID {
public:

  double error;
  double sample;
  double lastSample;
  double kP, kI, kD;
  double P, I, D;
  double pid;
  double setPoint;
  long lastProcess;

  PID(double _kP, double _kI, double _kD) {
    kP = _kP;
    kI = _kI;
    kD = _kD;
  }

  // 
  void addNewSample(double _sample) {
    sample = _sample;
  }

  void setSetPoint(double _setPoint) {
    setPoint = _setPoint; // posicao de referencia em rad
  }

  double calc_error() {
    error = setPoint - sample;
    return error;
  }

  double process() {
    // Implementação PID
    float deltaTime = (millis() - lastProcess) / 1000.0;
    lastProcess = millis();

    //P
    P = error * kP;

    //I
    I = I + (error * kI) * deltaTime;

    //D
    D = (lastSample - sample) * kD / deltaTime;
    lastSample = sample;


    // Soma tudo
    pid = (P + I + D); //fazia * 238 + 17

    return pid;
  }
};
//##############################################################################

// Wait for synchronization of registers between the clock domains
// ADC
static __inline__ void ADCsync() __attribute__((always_inline, unused));
static void ADCsync() {
  while (ADC->STATUS.bit.SYNCBUSY == 1)
    ;  //Just wait till the ADC is free
}

// Definição de variáveis
// Para o ADC
  uint32_t sensor1 = 0;
  uint32_t sensor2 = 0;
  uint32_t sensor3 = 0;
  uint32_t sensor4 = 0;
  uint32_t sensor5 = 0;
  uint32_t sensor6 = 0;
  
// Para a QUADRATURA
  unsigned long result_LSB_new;
  unsigned long result_LSB_old;
  unsigned long result_MSB_new;
  unsigned long result_MSB_old;
  unsigned long result_LSB;
  unsigned long result_MSB;
  unsigned long result;
  short encoder_count = 0;  // necessário ser short (16-bit) para que funcione a operação automática de complento de 2 e a variável seja lida como negativa quando msbit é HIGH
  int chipQuad_pins[] = { 4, 5, 11, 13, 10, 12, 6, 7 };

// Para o PID
  double err;
  double ganho;

// Para o CTRL DE IMPEDÂNCIA
  // Valores do controlador - Valores definidos pelo Lucas
  double I_c = 0.0013;
  double B_c = 0.00025;
  double K_c = 0.005;

// tempos para o calculo de impedancia em [s]
double t_0 = 0;                          // tempo inicial para calculo de impedancia
double t_i = 0;                          // tempo atual para calculo de impedancia
double t_i1 = -1 / 1000.0;               // tempo anterior para calculo de impedancia

// posicoes angulares em [rad]
double theta_i = 0;                      // angulo atual 
double theta_i1 = 0;                     // angulo anterior 
double theta_i2 = 0;                     // angulo anterior do anterior 
double theta_des = 0;                    // angulo desejado

// Comunicacao Serial
char serialFlag = '0';

// calculos de torque
double Tm;                               // torque medido
double Th;                               // torque humano
double Tact;                             // torque atuador
double PWM;                              // valor enviado por PWM proporcional ao torque
double maxTorqueMotor = 2.2;             // torque maximo do motor, vale 2.2 Nm

// Para a MÉDIA MÓVEL de força
const int numReadingsForce = 10;         // tamanho da média móvel
double readingsForce[numReadingsForce];  // vetor com medidas para cálculo da média móvel
int readIndexForce = 0;                  // indice da medida atual de força
double totalForce = 0;                   // soma total dos valores medidos
double averageForce = 0;                 // média
double maxLoadCell = 24.517;             // valor maximo da celula de carga em [N]
double lc = 0.12;                        // valor do comprimento l_c em [m]

// Tempos
double deltat = 0;                       // tempo entre as leituras em [s]
unsigned long tempoSerial = 0;           // controle do tempo para mandar dados pela serial
unsigned long tempo_inicio = 0;          // controle do tempo de início de cada atividade

bool flagStopMotor = true;
double pi = 3.141592653589793;

// PID(kD, kI, kP) - TODO: consertar os valores - como? não sei
PID myPid(100, 0, 1000);

void setup() {
  SerialUSB.begin(2000000);  //inicia a comunicação serial

  //###################################################################################
  // ADC setup stuff
  //###################################################################################
  ADCsync();
  ADC->INPUTCTRL.bit.GAIN = ADC_INPUTCTRL_GAIN_DIV2_Val;  // Gain select as 2X
  ADCsync();
  ADC->REFCTRL.bit.REFSEL = ADC_REFCTRL_REFSEL_INTVCC1_Val;  //  1/2 VDDANA

  // As 4 linhas de código acima fazem: multiplica o ganho da referência por 2 e utiliza referência como 3.3V / 2 = 1.65V.
  // Com ganho 2, temos que a referência do ADC será justamente VDDANA, ou seja, 3.3V

  ADCsync();
  ADC->AVGCTRL.reg = 0x12;  //13-bit
  ADCsync();
  ADC->SAMPCTRL.reg = 0x0;  //sample length in 1/2 CLK_ADC cycles Default is 3F

  //Control B register
  int16_t ctrlb = 0x410;  // Control register B hibyte = prescale, lobyte is resolution and mode
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
  // Inicializa vetor para a média móvel da força
  //###################################################################################
  for (int i = 0; i < numReadingsForce; i++) {
    readingsForce[i] = 0.0;
  }

  pinMode(EON, OUTPUT);
  pinMode(SEL1, OUTPUT);

  pinMode(RSTN, INPUT);
  digitalWrite(RSTN, HIGH);
  pinMode(pinCONTROL_LH, OUTPUT);
  pinMode(pinCONTROL_RH, OUTPUT);
}

void loop() {
  while (serialFlag == '0') {
    encoder_count = 0;
    digitalWrite(RSTN, LOW);
    digitalWrite(RSTN, HIGH);
    analogWrite(pinCONTROL_LH, 0);
    analogWrite(pinCONTROL_RH, 0);
    if (SerialUSB.available() > 0) {
      serialFlag = SerialUSB.read();
      tempo_inicio = millis();
    }
  }

  t_0 = millis() / 1000.0;

  while (serialFlag != '0') {

    // Para o ADC
    //Acquisition Bloc -----------------------------------
    sensor1 = anaRead(A0);
    sensor2 = anaRead(A1);
    sensor3 = anaRead(A2);
    sensor4 = anaRead(A3);
    sensor5 = anaRead(A4);
    sensor6 = anaRead(A5);
    //---------------------------/-------------------------

    // Para o PID e CRTL IMPEDÂNCIA

    /** ----- 1. READ ENCODER -----**/

    read_pos(); // reads encoder and saves to encoder_count variable
    
    // tempos em [s]
    t_i1 = t_i;
    t_i = (millis()/1000.0 - t_0);
    
    // angulos em rad
    theta_i2 = theta_i1;
    theta_i1 = theta_i;
    theta_i = (encoder_count / 1000.0) * pi;

    /** ----- 2. CALC POSIÇÃO REF -----**/

    // calcula media movel dos valores da celula de carga
    totalForce -= readingsForce[readIndexForce];
    readingsForce[readIndexForce] = map(sensor3, -4096, 4096, -maxLoadCell, maxLoadCell); 
    totalForce += readingsForce[readIndexForce];
    readIndexForce ++;
    if (readIndexForce >= numReadingsForce) readIndexForce = 0;
    averageForce = totalForce / (numReadingsForce / 1.0); // force result to be double

    // Torque aplicado pelo usuario
    Th = averageForce * lc;  
    deltat = t_i - t_i1;

    // torque do motor
    Tm = I_c * (theta_i - theta_i2) / (deltat * deltat) + B_c * (theta_i - theta_i1) + K_c * (theta_des - theta_i)
    Tact = Tm - Th;
    PWM = map(Tm, 0, maxTorqueMotor, 0, 255);

    /** ----- 3. CALC PID -----**/
    // Manda posição lida para o controlador
    myPid.addNewSample(theta_i);

    // Recebimento na serial de comandos para o motor
    // modo motor desligado
    if (serialFlag == '6') {
      flagStopMotor = true;
    }

    // setpoint = media dos valores medidos (original do Lucas)
    else if (serialFlag == '7') {
      theta_des = theta_i;
      flagStopMotor = false;
    }

    // setpoint = 45 graus - sentido horário
    else if (serialFlag == '8') {  
      theta_des = pi/4;
      flagStopMotor = false;
    }

    // impedância sentido anti-horário
    else if (serialFlag == '9') { 
      //setpoint = -45 graus
      theta_des = -pi/4;
      flagStopMotor = false;
    }

    else {
      // sem flag, motor persegue o zero
      theta_des = 0;
      flagStopMotor = false;
    }

    // Faz o setpoint como o theta desejado
    myPid.setSetPoint(theta_des);

    // Calcula erro baseado no setpoint definido
    err = myPid.calc_error();

    // Calcula ganho baseado nas constantes do controlador e no erro medido
    ganho = myPid.process();

    /** ----- 4. ACT PID -----**/
    if (flagStopMotor) {
      analogWrite(pinCONTROL_RH, 0);
      analogWrite(pinCONTROL_LH, 0);
    }
    
    // Seleciona o sentido de rotação do motor
    else if (err < 0 ) {
      analogWrite(pinCONTROL_RH, 0);
      analogWrite(pinCONTROL_LH, PWM * ganho);
    } 
    else {
      analogWrite(pinCONTROL_LH, 0);
      analogWrite(pinCONTROL_RH, PWM * ganho);
    }

    // Para o envio de informação
    //Send Information Bloc -------------------------------
    
    // Envia informações a cada 40ms
    if (millis() - tempoSerial >= 40) {
      tempoSerial = millis();
      SerialUSB.print("#");
      SerialUSB.print(tempoSerial-tempo_inicio);
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
      SerialUSB.print(encoder_count);
      SerialUSB.print("\n");
    }

    // Reset na atividade
    if (SerialUSB.available() > 0) {
      serialFlag = SerialUSB.read();
      tempo_inicio = 0;
    }
    delay(2);
  }
}

//##############################################################################
// Stripped-down fast analogue read anaRead()
// ulPin is the analog input pin number to be read.
////##############################################################################
uint32_t anaRead(uint32_t ulPin) {

  ADCsync();
  ADC->INPUTCTRL.bit.MUXPOS = g_APinDescription[ulPin].ulADCChannelNumber;  // Selection for the positive ADC input

  ADCsync();
  ADC->CTRLA.bit.ENABLE = 0x01;  // Enable ADC

  ADC->INTFLAG.bit.RESRDY = 1;  // Data ready flag cleared

  ADCsync();
  ADC->SWTRIG.bit.START = 1;  // Start ADC conversion

  while (ADC->INTFLAG.bit.RESRDY == 0)
    ;  // Wait till conversion done
  ADCsync();
  uint32_t valueRead = ADC->RESULT.reg;

  ADCsync();
  ADC->CTRLA.bit.ENABLE = 0x00;  // Disable the ADC
  ADCsync();
  ADC->SWTRIG.reg = 0x01;  //  and flush for good measure
  return valueRead;
}
//##############################################################################

inline int digitalRead_fast() {
  result = (PORT->Group[0].IN.reg & (PORT_PA14 | PORT_PA15 | PORT_PA16 | PORT_PA17 | PORT_PA18 | PORT_PA19 | PORT_PA20 | PORT_PA21));
  return result;
}

void read_pos() {
  digitalWrite(EON, HIGH);  //Disable OE

  //Read LSB
  digitalWrite(SEL1, HIGH);  //LSB
  digitalWrite(EON, LOW);    //Enable OE

  read_LSB();
  result_LSB = result_LSB_new;

  digitalWrite(SEL1, LOW);  //MSB

  read_MSB();
  result_MSB = result_MSB_new;

  digitalWrite(EON, HIGH);  //Disable OE

  encoder_count = result_LSB >> 14 | result_MSB >> 6;
}

void read_MSB() {
  result_MSB_old = digitalRead_fast();
  result_MSB_new = digitalRead_fast();

  if (result_MSB_new != result_MSB_old) {
    read_MSB();
  }
}

void read_LSB() {
  result_LSB_old = digitalRead_fast();
  result_LSB_new = digitalRead_fast();

  if (result_LSB_new != result_LSB_old) {
    read_LSB();
  }
}
