#include <WiFi.h>
#include <HTTPClient.h>
 
// Replace with your own network credentials
const char* ssid = "Dimpho";
const char* password = "zoey1104";
 
const char* serverEndpoint = 
"http://172.20.10.9:5000/data1"
;

const int ldrPin = 34;
int green = 14;
int red = 16;


const int User_Id = 221015566;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
 
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi..");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}

void loop() {

  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient httpClient;

    int rawValue = analogRead(ldrPin);
    

    //float lightIntensity = pow((ldrResistance / 1000.0), -1.4);
    float lux = map(rawValue, 0, 1023, 0, 1000); //adjust conversion factor as needed

    Serial.print("Light Intensity: ");
    Serial.print(lux);
    Serial.println("lux");

    // qualitatively determined thresholds
  if (lux < 100) {
    Serial.println(" => Dark"); 
    digitalWrite(red, HIGH); // switch on red LED
    digitalWrite(green, LOW); //switch off green LED
    

  } else {
    Serial.println(" => Light");
    digitalWrite(green, HIGH); // switch on red LED
    digitalWrite(red, LOW); //switch off red LED
  }
 



    String jsonData = "{\"User_Id\": " + String(User_Id) + ", \"light_intensity\": " + String(lux) + "}";

    httpClient.begin(serverEndpoint);
    httpClient.addHeader("Content-Type", "application/json");
    Serial.println(jsonData);
    int responseCode = httpClient.POST(jsonData);

    if (responseCode > 0) {
      String serverResponse = httpClient.getString();
      Serial.println(responseCode);
      Serial.println(serverResponse);

    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(responseCode);
    }

    httpClient.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(10000);
}