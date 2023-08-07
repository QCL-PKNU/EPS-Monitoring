#include <SoftwareSerial.h>

// uart
SoftwareSerial uart(12, 13); // RX: 12, TX: 13

// eps message buffer
String eps_msg_buf[64] = {
"SPD:+02.0,ANG:-0003,TRQ:+2442",
"SPD:+02.0,ANG:-0003,TRQ:+2442",
"SPD:+02.0,ANG:-0003,TRQ:+2442",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2442",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2440",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2441",
"SPD:+02.0,ANG:-0003,TRQ:+2442",
"EOF",
};

void setup() {
  Serial.begin(9600);

  // uart 
  uart.begin(57600);
}

int eps_msg_idx = 0;

void loop() {

  // eps message
  String eps_msg = eps_msg_buf[eps_msg_idx++];

  if(eps_msg == "EOF") {
    eps_msg_idx = 0;
    return;
  }

  byte eps_msg_bytes[64] = {0, };
  int eps_msg_len = eps_msg.length();
  
  eps_msg.getBytes(eps_msg_bytes, eps_msg_len+1);
  
  Serial.print(">> EPS Sensor Data: ");
  Serial.write(eps_msg_bytes, eps_msg_len+1);
  Serial.println();
  
  eps_msg_bytes[eps_msg_len] = 0x0A;
  uart.write(eps_msg_bytes, eps_msg_len+1);

  delay(200);
}
