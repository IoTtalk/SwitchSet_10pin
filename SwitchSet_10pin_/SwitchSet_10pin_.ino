#include <Bridge.h>

void setup() {
    pinMode(13,OUTPUT);
    pinMode(2,OUTPUT);
    digitalWrite(2, HIGH);    
    pinMode(3,OUTPUT);
    digitalWrite(3, HIGH);
    pinMode(4,OUTPUT);
    digitalWrite(4, HIGH);    
    pinMode(5,OUTPUT);    
    digitalWrite(5, HIGH);
    pinMode(6,OUTPUT);    
    digitalWrite(6, HIGH);
    pinMode(7,OUTPUT);
    digitalWrite(7, HIGH);
    pinMode(8,OUTPUT);    
    digitalWrite(8, HIGH);
    pinMode(9,OUTPUT);        
    digitalWrite(9, HIGH);
    pinMode(10,OUTPUT);        
    digitalWrite(10, HIGH);
    pinMode(11,OUTPUT);        
    digitalWrite(11, HIGH);

    Bridge.begin();   // Pins 0 and 1 should be avoided as they are used by the Bridge library.
}

void loop() {
    char pin13[2];
    char StrBuf[11];
    char valueStr[21];
    int  valueInt;

    Bridge.get("Reg_done",  pin13, 2);
    digitalWrite(13, atoi(pin13));    

    String StringTemp = "";
    for(int i=1; i<=10; i++){
        StringTemp = "Switch-O" + String(i);
        StringTemp.toCharArray(StrBuf, StringTemp.length()+1);
        Bridge.get(StrBuf,  valueStr, 3);
        if (strcmp(valueStr,"") != 0){
            valueInt = atoi(valueStr);                  
            //Serial.print(StrBuf); Serial.print(": "); Serial.println(valueStr);
            if (valueInt > 0) valueInt=0; else valueInt=1;  // on/off reverse
            digitalWrite(i+1, valueInt);        
            Bridge.put(StrBuf, "");
        }
    }
}
