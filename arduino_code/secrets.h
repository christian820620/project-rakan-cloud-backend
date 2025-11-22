//This is a blueprint for secrets.h
//Fill these in yourself
#include <pgmspace.h>

#define SECRET
#define THINGNAME "Smart-Thermostat"

const char WIFI_SSID[] = "";            //Wifi name
const char WIFI_PASSWORD[] = "";        //Wifi password
const char AWS_IOT_ENDPOINT[] = "";     //AWS IoT Endpoint address

//Aws Root CA 1
static const char AWS_CERT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
-----END CERTIFICATE-----
)EOF";

//Device Certificate
static const char AWS_CERT_CRT[] PROGMEM = R"KEY(
-----BEGIN CERTIFICATE-----
-----END CERTIFICATE-----
)KEY";

//Device Private Key
static const char AWS_CERT_PRIVATE[] PROGMEM = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----
)KEY";
