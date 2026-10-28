#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Credenciais da sua rede Wi-Fi
const char* ssid = "Home Sweet Home";     
const char* password = "marisa99530";       

// IP do seu computador na rede (obtido via ipconfig)
const char* serverUrl = "http://192.168.15.97:5000/api/telemetria"; 

// Identificação do veículo
String vehicleId = "ESP32_MOTO_INDaiatuba";

void conectarWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("Conectando em ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);   

  unsigned long inicio = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - inicio) < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Conectado com sucesso!");
    Serial.print("IP do ESP32: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Falha ao conectar no Wi-Fi.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- Sistema IoT Iniciado ---");
  conectarWiFi();    
}

void loop() {
  // Garante que o Wi-Fi está conectado antes de tentar o envio
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
    delay(5000);
    return;
  }

  // Criação do cliente HTTP dentro do loop para evitar vazamento de memória
  HTTPClient http;
  
  Serial.println("Enviando telemetria para o servidor...");
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  // Coordenadas simuladas na região de Indaiatuba
  float latitude = -23.0910; 
  float longitude = -47.2180;
  int bateria = 85; 
  int rssi = WiFi.RSSI();

  // Montando o payload JSON
  String payload = "{\"vehicle_id\":\"" + vehicleId + 
                   "\",\"lat\":" + String(latitude, 6) + 
                   ",\"lng\":" + String(longitude, 6) + 
                   ",\"bateria\":" + String(bateria) + 
                   ",\"rssi\":" + String(rssi) + "}";

  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
    Serial.print("Sucesso! Código HTTP: ");
    Serial.println(httpResponseCode);
    String resposta = http.getString();
    Serial.println(resposta);
  } else {
    Serial.print("Erro de conexão HTTP. Código: ");
    Serial.println(httpResponseCode);
  }

  http.end(); // Fecha a conexão HTTP adequadamente

  // Pausa de 10 segundos antes do próximo envio
  delay(10000); 
}