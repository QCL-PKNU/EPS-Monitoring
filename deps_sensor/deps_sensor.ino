#include <SoftwareSerial.h>

// uart
SoftwareSerial uart(12, 13); // RX: 12, TX: 13

// eps message buffer
String eps_msg_buf[64] = {
"SPD:+00.0,ANG:-0099,TRQ:+2732,CUR:+07.0",
"SPD:+00.0,ANG:-0099,TRQ:+2775,CUR:+07.8",
"SPD:+00.0,ANG:-0099,TRQ:+2722,CUR:+06.6",
"SPD:+00.0,ANG:-0099,TRQ:+2740,CUR:+06.9",
"SPD:+00.0,ANG:-0099,TRQ:+2769,CUR:+07.4",
"SPD:+00.0,ANG:-0101,TRQ:+2750,CUR:+06.9",
"SPD:+00.0,ANG:-0102,TRQ:+2784,CUR:+07.3",
"SPD:+00.0,ANG:-0102,TRQ:+2807,CUR:+07.8",
"SPD:+00.0,ANG:-0102,TRQ:+2793,CUR:+07.6",
"SPD:+00.0,ANG:-0103,TRQ:+2815,CUR:+08.1",
"SPD:+00.0,ANG:-0103,TRQ:+2811,CUR:+08.1",
"SPD:+00.0,ANG:-0103,TRQ:+2888,CUR:+09.9",
"SPD:+00.0,ANG:-0103,TRQ:+2871,CUR:+09.5",
"SPD:+00.0,ANG:-0103,TRQ:+2845,CUR:+09.0",
"SPD:+00.0,ANG:-0107,TRQ:+2920,CUR:+10.4",
"SPD:+00.0,ANG:-0110,TRQ:+2920,CUR:+10.5",
"SPD:+00.0,ANG:-0111,TRQ:+2956,CUR:+11.4",
"SPD:+00.0,ANG:-0111,TRQ:+2984,CUR:+11.9",
"SPD:+00.0,ANG:-0111,TRQ:+2964,CUR:+11.6",
"SPD:+00.0,ANG:-0113,TRQ:+2986,CUR:+12.2",
"SPD:+00.0,ANG:-0113,TRQ:+2995,CUR:+12.5",
"SPD:+00.0,ANG:-0117,TRQ:+3134,CUR:+15.2",
"SPD:+00.0,ANG:-0118,TRQ:+3127,CUR:+15.0",
"SPD:+00.0,ANG:-0119,TRQ:+3134,CUR:+15.2",
"SPD:+00.0,ANG:-0119,TRQ:+3116,CUR:+14.7",
"SPD:+00.0,ANG:-0123,TRQ:+3197,CUR:+16.4",
"SPD:+00.0,ANG:-0126,TRQ:+3230,CUR:+16.9",
"SPD:+00.0,ANG:-0125,TRQ:+3243,CUR:+17.0",
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
