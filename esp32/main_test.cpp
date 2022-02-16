#include <string.h>
#include "XBee.h"

#include <Arduino.h>
#include <driver/gpio.h>
#include <SoftwareSerial.h>
#define rxPin 14
#define txPin 13
SoftwareSerial mySerial(rxPin, txPin); 

/* GOAL 
Receives a ZigBee RX packet and sets a PWM value based on packet data.
Error led is flashed if an unexpected packet is received
*/

//instantiates the XBee library
XBee xbee = XBee();
//creates object instance "response" to process Xbee Packets
XBeeResponse response = XBeeResponse();
//creates object instance "rx" to process Xbee Series 2 API packets
ZBRxResponse rx = ZBRxResponse();
//creates object instance "msr" to process associate/disassociate packets (PAN membership)
ModemStatusResponse msr = ModemStatusResponse();
//creates object instance "txStatus" to process acknowledgements for sent Xbee Series 2 API packets
ZBTxStatusResponse txStatus = ZBTxStatusResponse();
 
//Declare some variables we'll need to hold received packet data so we can use it to transmit
//The two 32-bit halves of the 64-bit address
long XBee_Addr64_MS;
long XBee_Addr64_LS;
//The 16-bit address
int XBee_Addr16;
//We need a string to hold incoming data bytes from received packets.  I chose a 20 byte string as my
//  transmit needs are short.  make this at least 3 bytes longer than the longest data
//  block you'll receive.
char XBee_Data[20];
//We need to make sure we're not overwriting the string, so we'll name its length to use later
#define XBee_Data_len 20
//An integer varailbe for temporary use
int dummy;


// sed LED's to indicate activity and status.
int statusLed = 11;
int errorLed = 12;
int dataLed = 10;
// need a counter to bring in received data byte-by-byte (how the library delivers it)
int count=0;

void flashLed(int pin, int times, int wait) {
    
    for (int i = 0; i < times; i++) {
      digitalWrite(pin, HIGH);
      delay(wait);
      digitalWrite(pin, LOW);
      
      if (i + 1 < times) {
        delay(wait);
      }
    }
}

void setup() {
  //Set up and start the Software Serial port
  pinMode(rxPin, INPUT);
  pinMode(txPin, OUTPUT);
  // set the data rate for the SoftwareSerial port
  mySerial.begin(9600);
  Serial.begin(9600);
  //Set up the LED indicator pins
  pinMode(statusLed, OUTPUT);
  pinMode(errorLed, OUTPUT);
  pinMode(dataLed,  OUTPUT);
  
  //The Xbee Library starts the hardware serial port.
  xbee.setSerial(Serial);
  
  //This just signals that the setup phase is complete.
  flashLed(statusLed, 3, 50);
}


void loop() {
    
    xbee.readPacket();
    
    if (xbee.getResponse().isAvailable()) {
      
      //If it's a Zigbee Receive packet (API ID 0x90)...
      if (xbee.getResponse().getApiId() == ZB_RX_RESPONSE) {
        
        //Populate our "rx" object with info from the received packet (Data, Addresses, etc)
        xbee.getResponse().getZBRxResponse(rx);
            
        //Flash an LED if receipt was acknowleged to the sending node, or maybe not    
        if (rx.getOption() == ZB_PACKET_ACKNOWLEDGED) {
            // the sender got an ACK
            flashLed(statusLed, 1, 10);
        } else {
            // we got it (obviously) but sender didn't get an ACK
            flashLed(errorLed, 2, 20);
        }
        // set dataLed PWM to value of the first byte in the data
        digitalWrite(dataLed, HIGH);
        
        //Here I'm extracting some of the information I'll need to create a packet to reply back to the
        //  sender.
        //This one obtains the upper 32-bit word of the 64-bit address.  The 64-bit address is the 802.15.4 MAC
        //  layer address (i.e, the "burned in" one).
        XBee_Addr64_MS=(uint32_t(rx.getFrameData()[0]) << 24) + (uint32_t(rx.getFrameData()[1]) << 16) + (uint16_t(rx.getFrameData()[2]) << 8) + rx.getFrameData()[3];
        //This one obtains the lower 32-bit word...
        XBee_Addr64_LS=(uint32_t(rx.getFrameData()[4]) << 24) + (uint32_t(rx.getFrameData()[5]) << 16) + (uint16_t(rx.getFrameData()[6]) << 8) + rx.getFrameData()[7];
        //Send the two parts of the address to the software serial port
        mySerial.print("Addr64 MS: ");
        mySerial.print(XBee_Addr64_MS,HEX);
        mySerial.print('\n');
        mySerial.print("Addr64 LS: ");
        mySerial.print(XBee_Addr64_LS,HEX);
        mySerial.print('\n');
        //Now we extract the 16-bit address.  This is the Zigbee Network address of the node in the PAN, analogous to
        //  an IP address in TCP/IP. 
        XBee_Addr16=rx.getRemoteAddress16();
        mySerial.print("Addr16: ");
        
        mySerial.print(rx.getRemoteAddress16(),HEX);
        mySerial.print('\n');
        
        mySerial.print("DataLength: ");
        mySerial.print(rx.getDataLength(),DEC);
        mySerial.print('\n');
        //Need to make sure we don't overrun the string.  Enforce it's length
        if (rx.getDataLength()>=XBee_Data_len) {dummy=XBee_Data_len;}
        else                                  {dummy=rx.getDataLength();}
        //Now we read the data.  Note that we read from the start of the buffer to position DataLength-1.
        mySerial.print("Data: ");
        for (count=0;count<=dummy-1;count++)
        {
          mySerial.print(rx.getData(count));
          XBee_Data[count]=rx.getData(count);
        }
        
        XBee_Data[dummy]='\0';
        mySerial.print('\n');
        
        //Now we'll send data what we received to the node that sent it
        //Create a 64-bit address data structure from the extracted address
        XBeeAddress64 XBee_Addr64 = XBeeAddress64(XBee_Addr64_MS, XBee_Addr64_LS);
        // pack data together
        ZBTxRequest zbTx = ZBTxRequest(XBee_Addr64, XBee_Addr16, ZB_BROADCAST_RADIUS_MAX_HOPS, ZB_TX_UNICAST, (uint8_t*) XBee_Data, strlen(XBee_Data), xbee.getNextFrameId());
        //Send the packet
        xbee.send(zbTx);
        
        // flash TX indicator
        flashLed(statusLed, 1, 100);
    
        //Now we figure out if the destination node received the packet...
        // after sending a tx request, we expect a status response
        // wait up to half second for the status response
        if (xbee.readPacket(500)) {
 
    	    if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
    	       xbee.getResponse().getZBTxStatusResponse(txStatus);
    	    	
    	       // get the delivery status, the fifth byte
               if (txStatus.getDeliveryStatus() == SUCCESS) {
                	// success.  time to celebrate
                 	flashLed(statusLed, 5, 50);
               } else {
                	// the remote XBee did not receive our packet. is it powered on?
                 	flashLed(errorLed, 3, 500);
               }
            }      
        } else {
          // local XBee did not provide a timely TX Status Response -- should not happen
          flashLed(errorLed, 2, 50);
        }
        //*****END OF DATA PACKET PROCESSING******

      //*****This part detects associate/disassociate packets*****
      } else if (xbee.getResponse().getApiId() == MODEM_STATUS_RESPONSE) {
        xbee.getResponse().getModemStatusResponse(msr);
        
        
        if (msr.getStatus() == ASSOCIATED) {
          // yay this is great.  flash led
          flashLed(statusLed, 10, 10);
        } else if (msr.getStatus() == DISASSOCIATED) {
          // this is awful.. flash led to show our discontent
          flashLed(errorLed, 10, 10);
        } else {
          // another status
          flashLed(statusLed, 5, 10);
        }
      } else {
      	// not something we were expecting
        flashLed(errorLed, 1, 25);    
      }
    }
}