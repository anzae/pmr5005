unsigned int start_flag = 48;  //indica o início do experimento - arduíno inicía coleta de dados
long t;
int s1;
int s2;
int s3;
int s4;
int s5;
int s6;
int encoder;

uint32_t tempo = 0;
unsigned long t_start = 0;

void setup() {
  // put your setup code here, to run once:
  SerialUSB.begin(2000000);  //inicia a comunicação serial
  SerialUSB.write("open port serial");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (SerialUSB.available() > 0) {
    start_flag = SerialUSB.read();
  }
  t_start = micros();

  while (start_flag == 49) {  // 48 é 0 em ASCII
    // simula medidas dos sensores
    s1 = random(0, 200);
    s2 = random(0, 200);
    s3 = random(0, 200);
    s4 = random(0, 200);
    s5 = random(0, 200);
    s6 = random(0, 200);
    encoder = random(0, 600) - 300;
    tempo = micros();

    // simula o envio dos dados
    SerialUSB.print("#");
    SerialUSB.print((tempo-t_start));
    SerialUSB.print(",");
    SerialUSB.print(s1);
    SerialUSB.print(",");
    SerialUSB.print(s2);
    SerialUSB.print(",");
    SerialUSB.print(s3);
    SerialUSB.print(",");
    SerialUSB.print(s4);
    SerialUSB.print(",");
    SerialUSB.print(s5);
    SerialUSB.print(",");
    SerialUSB.print(s6);
    SerialUSB.print("@");
    SerialUSB.print(encoder);
    SerialUSB.print("\n");
    delay(500);
  }


}