#include <LiquidCrystal.h>

// Initialize LCD (RS, E, D4, D5, D6, D7)
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

String trackName = "";
String artistName = "";

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.print("Waiting for");
  lcd.setCursor(0, 1);
  lcd.print("Spotify...");
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    int separatorIndex = data.indexOf('|');
    if (separatorIndex > 0) {
      trackName = data.substring(0, separatorIndex);
      artistName = data.substring(separatorIndex + 1);
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(trackName);
      lcd.setCursor(0, 1);
      lcd.print(artistName);
    }
  }
}
