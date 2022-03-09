#include <Arduino.h>
#include <driver/gpio.h>
#include <ArduinoJson.h>

#define LED_PIN GPIO_NUM_18
#define RX_PIN 14
#define TX_PIN 13
int incomingByte = 0; // for incoming serial data
String message;

// change to pointer list after implement
char* deviceFuncList[] = {"set_device_parameter", "get_device_state", "get_device_parameter","soft_reboot"};
char* timeFuncList[] = {"set_clock"};
char* ledFuncList[] = {"Set_single_led","Set_led_mode","Set_parameter","Set_spot","Set_gravity"};
char* infoFuncList[] = {"get_ball_type","get_led_type","get_led_status","get_attitude","get_gps_position","get_battery","get_temperature","get_motion"};


//SoftwareSerial xbeeSerial(RX_PIN, TX_PIN); 

void setup()
{
    Serial.begin(115200);
    Serial2.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
    // Configure serial2 port for connecting to Xbee3 module
    // leave some init time
    for (uint8_t t = 4; t > 0; t--) {
        Serial.printf("[SETUP] WAIT %d...\n", t);
        Serial.flush();
        delay(500);
    }
    Serial.println("Setup complete.");

}

char* func_selector(int func_cate, int func_id)
{
    switch (func_cate) {
    case 0:
        return deviceFuncList[func_id];
    case 1:
        return timeFuncList[func_id];
    case 2:
        return ledFuncList[func_id];
    case 3:
        return infoFuncList[func_id];
    
}
}

void loop()
{

    if (Serial2.available())  {
        message = Serial2.readString();
        // print serial2 message to serial debug interface
        
        // check if command, use single quotes
        if (message.charAt(0) == '{') {
        Serial.println("Received a command");
        }

        Serial.print("message = " + message);

        DynamicJsonDocument payload(255);
        // received payload, deserialize the JSON document
        DeserializationError error = deserializeJson(payload, message);

        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            Serial.println(error.f_str());
        }
        else
        {
            Serial.println("parse JSON success");
        }
        // read from json format
        int func_cate = payload["category"];
        int func_id = payload["id"];
        JsonArray func_params = payload["params"].as<JsonArray>();
        char* func_selected = func_selector(func_cate,func_id);
        Serial.println((String)"Command to execute: "+func_selected);
        Serial.println((String)"num of params: "+func_params.size());

        
        if(strcmp(func_selected, "get_temperature") == 0){
            DynamicJsonDocument response(200);
            response["category"] = func_cate;
            response["id"] = func_id;
            
            DynamicJsonDocument content(50);
            JsonArray array = content.to<JsonArray>();
            array.add(25.1);

            response["response"] = content;
            serializeJson(response, Serial2);
            Serial.println("Response sent");
        }
        
    }

}


