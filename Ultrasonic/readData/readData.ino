
// Test code for Adafruit GPS modules using MTK3329/MTK3339 driver
//
// This code shows how to listen to the GPS module in an interrupt
// which allows the program to have more 'freedom' - just parse
// when a new NMEA sentence is available! Then access data when
// desired.
//
// Tested and works great with the Adafruit Ultimate GPS module
// using MTK33x9 chipset
//    ------> http://www.adafruit.com/products/746
// Pick one up today at the Adafruit electronics shop 
// and help support open source hardware & software! -ada

#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>


// If you're using a GPS module:
// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// If using software serial (sketch example default):
//   Connect the GPS TX (transmit) pin to Digital 3
//   Connect the GPS RX (receive) pin to Digital 2
// If using hardware serial (e.g. Arduino Mega):
//   Connect the GPS TX (transmit) pin to Arduino RX1, RX2 or RX3
//   Connect the GPS RX (receive) pin to matching TX1, TX2 or TX3

// If you're using the Adafruit GPS shield, change 
// SoftwareSerial mySerial(3, 2); -> SoftwareSerial mySerial(8, 7);
// and make sure the switch is set to SoftSerial

// If using software serial, keep these lines enabled
// (you can change the pin numbers to match your wiring):
SoftwareSerial mySerial(5, 4);

Adafruit_GPS GPS(&mySerial);
// If using hardware serial (e.g. Arduino Mega), comment
// out the above six lines and enable this line instead:
//Adafruit_GPS GPS(&Serial1);


// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences. 
#define GPSECHO  true

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prsddsdfsototype keeps Arduino 0023 happy

// A constant declaring the nubmer of ultrasonic sensors used.
int number_of_sensors = 1;

/*
Each sensor has:
  a pin number
  the number of elements in pRawData.
  an array of raw data readings.
  a timestamp corresponding to the pulse of the sensor.
*/
struct Sensor{
  int pin;
  int length;
  uint32_t* pRawData;
  uint32_t timestamp;
};

/*
The sensors can only be on digital pins 2 and 3. These are the only
pins with external interrupts that can be attached to them. 
*/
Sensor SensorOne = { 
  2, 0, NULL, millis()};
Sensor SensorTwo = { 
  3, 0, NULL, millis()};
  
//The number of ultrasonic sensor 
//readings that are yet to be read printed
int readingCounter = 0; 

void setup() {
  GPS_setup();
  ultrasonic_setup();
}

void loop() {
  GPS_main();

  // If enough data is ready to print.
  if (readingCounter >= number_of_sensors) { 
    Serial.print(readingCounter);
    Serial.print(SensorOne.length);
    Serial.print('\t');
    readingCounter -= number_of_sensors;
    print_data();
  }

}


struct Sensor add_element(Sensor sensor, uint32_t value) {
  /*
  Sensor add_element - adds an element to the pRawData array in a sensor.
  
  Arguments:
    sensor - the sensor whos pRawData array will be appened.
    value - the value which will be appended to pRawData
    
  Returns:
    sensor - the modified sensor data.
  */

  sensor.length++;
  sensor.pRawData = (uint32_t*)realloc(sensor.pRawData,sensor.length*sizeof(uint32_t));
  sensor.pRawData[sensor.length -1] = value;
  return sensor;
}

struct Sensor remove_first_element(Sensor sensor) {
    /*
  Sensor remove_first_element - removes the first element from the pRawData array in a sensor.
  
  Arguments:
    sensor - the sensor whos pRawData array will be appened.
    
  Returns:
    sensor - the modified sensor data.
  */
  
  // Moves the next element to the previous position.
  for(int i = 0; i < (sensor.length -1); i++) {
    sensor.pRawData[i] = sensor.pRawData[i+1];
  }
  
  uint32_t* tmp = (uint32_t*)realloc(sensor.pRawData, (sensor.length - 1)*sizeof(uint32_t));
  sensor.length--;
  if (tmp == NULL && sensor.length > 1) {
    Serial.println("ERROR: No memory available.");
  }

  sensor.pRawData = tmp;
  return sensor;

}


void print_data() {
  /*
  print_data - a function responisble for printing all relevant data.
  
  Arguments: none
  Returns: null
  */
  
  uint32_t timer1 = 0;
  uint32_t timer2 = 0;

  if(SensorOne.length > 0 ) {
    timer1 = SensorOne.pRawData[0];
    SensorOne = remove_first_element(SensorOne);
  }

  if (SensorTwo.length > 0) {
    timer2 = SensorTwo.pRawData[0];
    SensorTwo = remove_first_element(SensorTwo);
  }

  // Prints the GPS' time data
  Serial.print("\t");
  Serial.print(GPS.hour, DEC); 
  Serial.print(':');
  Serial.print(GPS.minute, DEC); 
  Serial.print(':');
  Serial.print(GPS.seconds, DEC); 
  Serial.print("\t");

  // Prints the GPS date data.
  //Serial.print(GPS.day, DEC); Serial.print('/');
  //Serial.print(GPS.month, DEC); Serial.print("/20");
  //Serial.print(GPS.year, DEC);
  //Serial.print("\t");

  // Fix is a boolean of if the GPS has locked onto enough satelites.
  Serial.print((int)GPS.fix);
  Serial.print("\t");
  Serial.print((int)GPS.fixquality);
  Serial.print("\t");    

  // Prints the Location data from the GPS
  //Serial.print("Location: ");
  //Serial.print(GPS.latitude, 4); 
  //Serial.print(GPS.lat);
  //Serial.print("\t");
  //Serial.print(GPS.longitude, 4); 
  //Serial.print(GPS.lon);
  //Serial.print("\t");
  //Serial.print("Altitude: "); 
  //Serial.print(GPS.altitude);
  //Serial.print("\t");


  // Prints the GPS' speed data (speed is in knots)
  //Serial.print("Speed (knots): "); 
  //Serial.print(GPS.speed);
  //Serial.print("\t");
  //Serial.print("Speed (km/h): "); 
  Serial.print(GPS.speed*1.852);
  Serial.print("\t");

  // Prints the angle w.r.t horizontal. 
  //Serial.print("Angle: "); 
  Serial.print(GPS.angle);
  Serial.print("\t");


  //Serial.print("Satellites: "); 
  Serial.print((int)GPS.satellites);
  Serial.print("\t");

  // The distance to the object in cm accoring to sensor1
  Serial.print(timer1*2.54/147);
  Serial.print("\t");
  // The distance to the object in cm accoring to sensor2
  Serial.print(timer2*2.54/147);
  Serial.print("\n");

}
