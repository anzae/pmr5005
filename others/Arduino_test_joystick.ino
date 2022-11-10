/*
  Arquivo para testar o funcionamento do Game PMR5005
  Possui um joystick analógico com a seguinte conexão ao Arduino UNO:
    eixo X: A0
    eixo Y: A1
    eixo Z: 2
  No joystick específico, após o mapeamento, o valor neutro era 1, por isso a correção.
  Os valores dos sensores são aleatórios.
  O delay é um valor próximo ao FPS.
*/

#define VX A0
#define VY A1
#define Z 2

int vx;
int S1, S2, S3, S4, S5, S6;
unsigned long t;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000);
  pinMode(VX, INPUT);
  pinMode(VY, INPUT);
  pinMode(Z, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  t = millis();
  vx = map(analogRead(VX), 0, 1023, -300, 300) - 1;
  S1 = (int)random(-8192, 8192);
  S2 = (int)random(-8192, 8192);
  S3 = (int)random(-8192, 8192);
  S4 = (int)random(-8192, 8192);
  S5 = (int)random(-8192, 8192);
  S6 = (int)random(-8192, 8192);

  Serial.print("#");
  Serial.print(t);
  Serial.print(",");
  Serial.print(S1);
  Serial.print(",");
  Serial.print(S2);
  Serial.print(",");
  Serial.print(S3);
  Serial.print(",");
  Serial.print(S4);
  Serial.print(",");
  Serial.print(S5);
  Serial.print(",");
  Serial.print(S6);
  Serial.print("@");
  Serial.println(vx);

  delay(50);
}
