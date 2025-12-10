#include <WiFi.h>
#include <WebServer.h>

const char* ssid     = "NOME_DO_WIFI";
const char* password = "SENHA_DO_WIFI";
const char* AUTH_TOKEN = "seu_token_aqui";

const int gatePin = 5;  
WebServer server(80);

void openGate() {
  String auth = server.header("Authorization");
  if (!auth.startsWith("Bearer ")) {
    server.send(401, "application/json", "{"status":"error","msg":"no auth"}");
    return;
  }
  String token = auth.substring(7);
  if (token != AUTH_TOKEN) {
    server.send(403, "application/json", "{"status":"error","msg":"invalid token"}");
    return;
  }
  digitalWrite(gatePin, HIGH);
  delay(500);
  digitalWrite(gatePin, LOW);
  server.send(200, "application/json", "{"status":"ok","message":"Portão aberto"}");
}

void setup() {
  Serial.begin(115200);
  pinMode(gatePin, OUTPUT);
  digitalWrite(gatePin, LOW);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  server.on("/open", HTTP_POST, openGate);
  server.begin();
}
void loop() { server.handleClient(); }
