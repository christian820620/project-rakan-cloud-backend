#include "secrets.h"
#include "WiFi.h"
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <cstring>

#include <WiFiClientSecure.h>

#include <LiquidCrystal.h>
#include <DHT.h>

//Define Pinouts
#define FAN_LED 17
#define HEAT_LED 18
#define AC_LED 19
#define DHTPIN 2
#define DHTTYPE DHT11

//Define AWS Topic
#define AWS_IOT_PUBLISH_TOPIC   "thermostat/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "thermostat/sub"
#define AWS_IOT_FAN_CONTROL     "thermostat/fan"
#define AWS_IOT_HEATAC_CONTROL  "thermostat/heatAC"

//Define LED On or Off for Heat/AC control
#define LED_ON 255
#define LED_OFF 0

//Global variable
int count = 0;
float humid;
float temp;
float hic;    //Heat index
float fan_speed_per;
int fan_speed = 100;  //Min 0->255 Max LED brightness to simulate fan speed
bool heat, ac;
char* humidity_display = new char[20];
char* temperature_display = new char[20];
char* fan_speed_display = new char[20];

//Setup WifiClientSecure
WiFiClientSecure net = WiFiClientSecure();
PubSubClient client(net);

//Define DHT and LCD pins
DHT dht(DHTPIN,DHTTYPE);
LiquidCrystal lcd(7,8,9,10,11,12);


//Connect online
void connectAWS() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  delay(5000);
  Serial.println("Connecting to Wifi");
  
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  //Configure to use AWS IoT Credentials
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  //Connect to MQTT Broker on AWS endpoint
  client.setServer(AWS_IOT_ENDPOINT, 8883);

  //Create message handler
  client.setCallback(messageHandler);

  delay(5000);
  Serial.println("Connecting to AWS IoT Core");

  while (!client.connect(THINGNAME))
  {
    Serial.print(".");
    delay(100);
  }

  if (!client.connected())
  {
    Serial.println("AWS IoT Timeout!");
    return;
  }

  //Subscribe to a topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
  client.subscribe(AWS_IOT_FAN_CONTROL);
  client.subscribe(AWS_IOT_HEATAC_CONTROL);
  Serial.println("AWS IoT Connected!");
}

//Output Message to AWS
void publishMessage()
{
  StaticJsonDocument<200> doc;
  doc["humidity"] = humid;
  doc["temperature"] = temp;
  doc["fan_speed_percent"] = fan_speed_per;
  doc["heat"] = heat;
  doc["ac"] = ac;
  doc["ID"] = count;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer); //print to client

  client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

//Handle income message
void messageHandler(char* AWS_topic, byte* payload, unsigned int length)
{
  Serial.print("Incoming: ");
  Serial.println(AWS_topic);
  char* topic = AWS_topic;

  StaticJsonDocument<200> doc;
  deserializeJson(doc, payload);
  const char* message = doc["message"];

  //Match topic
  if (strcmp(topic, "thermostat/fan") == 0)
  {
    fan_speed = doc["fan speed"];
    fan_speed_control(fan_speed);
  }
  else if (strcmp(topic, "thermostat/heatAC") == 0)
  {
    int toggle_heat = doc["heat set"];   //ON or OFF
    int toggle_ac   = doc["ac set"];
    heatAC_control(toggle_heat, toggle_ac);
  }
  Serial.println(message);
}

//Control fan speed
void fan_speed_control(int speed)
{
  if (speed > 255)
  {
    fan_speed = 255;
  }
  else if (fan_speed < 0)
  {
    fan_speed = 0;
  }
  analogWrite(FAN_LED,fan_speed);     //Set LED brightness
}

//Heat and AC control for corresponding LEDs
void heatAC_control(int toggle_heat, int toggle_ac)
{
  if (toggle_heat >= 1)
  {
    heat = true;
    analogWrite(HEAT_LED,LED_ON);
  }
  else
  {
    heat = false;
    analogWrite(HEAT_LED,LED_OFF);
  }

  if (toggle_ac >= 1)
  {
    ac = true;
    analogWrite(AC_LED,LED_ON);
  }
  else
  {
    ac = false;
    analogWrite(AC_LED,LED_OFF);
  }
}


//Setup
void setup() {
  lcd.clear();
  lcd.begin(16,2);
  lcd.print("Thermostat");

  pinMode(FAN_LED,OUTPUT);
  analogWrite(FAN_LED,fan_speed);

  pinMode(HEAT_LED,OUTPUT);
  analogWrite(HEAT_LED,LED_OFF);
  heat = false;

  pinMode(AC_LED,OUTPUT);
  analogWrite(AC_LED,LED_ON);
  ac = true;

  Serial.begin(115200);
  connectAWS();

  dht.begin();
  delay(1000);
}

void loop() {
  //Read Humidity & Temperature
  humid = dht.readHumidity();
  temp = dht.readTemperature(true);
  //Increase count to keep track of loop
  if (count >= 10)
  {
    count = 0;
  }
  count++;

  //Check if DHT fails to read
  if (isnan(humid) || isnan(temp)){
    lcd.setCursor(0, 0);
    lcd.print("DHT failed read");
    return;
  }
  //Compute Heat Index
  hic = dht.computeHeatIndex(temp,humid,true);

  //Create message for display
  sprintf(humidity_display, "Humid: %.2f%%   ", humid);
  Serial.println(humidity_display);
  sprintf(temperature_display, "Temp:  %.2fF  ",temp);
  Serial.println(temperature_display);

  //Print message on LCD
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(humidity_display);
  lcd.setCursor(0, 1);
  lcd.print(temperature_display);

  //Calculate fan speed and create message
  fan_speed_per = (fan_speed/255.0f)*100.0f;
  sprintf(fan_speed_display, "Fan speed: %.1f%%", fan_speed_per);
  Serial.println(fan_speed_display);

  delay(5000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(fan_speed_display);  

  //Send to AWS
  publishMessage();
  client.loop();
  delay(2000);
}
