int pin1 = 13;
int pin2 = 4;

int pinA = 2;
int pinB = 3;

int i = 0;
int val = 0;

int Astate = 0;
int Bstate = 0;

volatile int state = LOW;

void setup()
{
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
  
  pinMode(pinA,INPUT);
  pinMode(pinB,INPUT);
  
  digitalWrite(2,HIGH);
  digitalWrite(3,HIGH);
  
  attachInterrupt(0, AChange, CHANGE);
  attachInterrupt(1, BChange, CHANGE);
  
  Serial.begin(115200); 
  
}

void AChange(){
   val = digitalRead(pinA);
   if (val == 0){
     if (Astate == 0){
        Serial.print("AP\n");
        ledOn();
        Astate = 1;
     }else{
       Astate = 1;
     }
   }else{
      if (Astate == 1){
       Serial.print("AR\n");
       ledOff();
       Astate = 0;
      }else{
        Astate = 0;
      }
   }
}

void BChange(){
   val = digitalRead(pinB);
   if (val == 0){
     if(Bstate == 0){
       Serial.print("BP\n");
       ledOn();
       Bstate = 1;
     }else{
       Bstate = 1;
     }
   }else{
     if(Bstate == 1){
      Serial.print("BR\n");
      ledOff();
      Bstate = 0;
     }else{
       Bstate = 0;
     }
   }
}

void ledOn(){
  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, HIGH);
}

void ledOff(){
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
}


void loop()
{
  i ++;
}

