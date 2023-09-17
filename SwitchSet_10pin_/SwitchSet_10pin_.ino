#include <Bridge.h>
#define defaultState LOW

void setup() {
    pinMode(13,OUTPUT);
    pinMode(2,OUTPUT);
    digitalWrite(2, defaultState);    
    pinMode(3,OUTPUT);
    digitalWrite(3, defaultState);
    pinMode(4,OUTPUT);
    digitalWrite(4, defaultState);    
    pinMode(5,OUTPUT);    
    digitalWrite(5, defaultState);
    pinMode(6,OUTPUT);    
    digitalWrite(6, defaultState);
    pinMode(7,OUTPUT);
    digitalWrite(7, defaultState);
    pinMode(8,OUTPUT);    
    digitalWrite(8, defaultState);
    pinMode(9,OUTPUT);        
    digitalWrite(9, defaultState);
    pinMode(10,OUTPUT);        
    digitalWrite(10, defaultState);
    pinMode(11,OUTPUT);        
    digitalWrite(11, defaultState);

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
            if (defaultState == HIGH){
                if (valueInt > 0) valueInt=0; else valueInt=1;  // on/off reverse
            }
            digitalWrite(i+1, valueInt);        
            Bridge.put(StrBuf, "");
        }
    }
}
