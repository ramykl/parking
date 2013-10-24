void ultrasonic_setup() {

  //Sets up the sensors pins.
  pinMode(SensorOne.pin, INPUT);
  pinMode(SensorTwo.pin, INPUT);
  
  //Enables the rising edge interrupt for pin 2 (external interrupt 0)
  attachInterrupt(0, start_timer_1, RISING);
  //Enables the rising edge interrupt for pin 2 (external interrupt 0)
  //attachInterrupt(1, start_timer_2, RISING);
  Serial.print("Ultrasonic Setup Complete\n");
}


void start_timer_1() {
  /*
  start_timer_1 - on the rising edge of the external interrupt 0, begin the timer to
  calculate the pulse width of the ultrasonic sensor. Also sets up the falling edge interrupt. 
  
  Arguments: none
  Returns: null
  */
  SensorOne.timestamp = micros();
  detachInterrupt(0);
  attachInterrupt(0, end_timer_1, FALLING);
}


void end_timer_1(void) {
  /*
  end_timer_1 - on the falling edge of the external interrupt 0, end the timer and add the
  pusle width to the pRawData of SensorOne. Re-enables the rising edge interrupt.
  
  Arguments: none.
  Returns: null.
  */
  int pulseWidth = 0;
  pulseWidth = micros() - SensorOne.timestamp;
  SensorOne = add_element(SensorOne, pulseWidth);

  readingCounter++;

  detachInterrupt(0);
  attachInterrupt(0, start_timer_1, RISING);
}

void start_timer_2() {
  /*
  start_timer_2 - on the rising edge of the external interrupt 1, begin the timer to
  calculate the pulse width of the ultrasonic sensor. Also sets up the falling edge interrupt. 
  
  Arguments: none
  Returns: null
  */
  SensorTwo.timestamp = micros();

  detachInterrupt(1);
  attachInterrupt(1, end_timer_2, FALLING);
}


void end_timer_2(void) {
  /*
  end_timer_2 - on the falling edge of the external interrupt 1, end the timer and add the
  pusle width to the pRawData of SensorOne. Re-enables the rising edge interrupt.
  
  Arguments: none.
  Returns: null.
  */
  int pulseWidth = 0;
  pulseWidth = micros() - SensorTwo.timestamp;
  SensorTwo = add_element(SensorTwo, pulseWidth);
  
  readingCounter++;
  
  detachInterrupt(1);
  attachInterrupt(1, start_timer_2, RISING);
}

