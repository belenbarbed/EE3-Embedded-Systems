# EE3-Embedded-Systems
Product Name : TrackIt.

It's scientifically proven that listening to music while running pushes the runner to cover longer distance (endurance) and faster i.e a great motivator enhacing one's workout.

To solve for this, TrackIt. acts as your running buddy but detecting your tempo and playing music with a +/-5bpm range to match your pace.


How it works:

To calculate the bpm:





To intergrate with Spotify API




Future Developments:

It would be able to intergrate with other API
## Sensor Analysis

1. What does it do?

    It's a 3D linear accelerometer, also includes temperature sensor.

2. What is the power supply voltage?

    According to doc: 1.71V to 3.6V, needs an independent I/O voltage supply of 1.8V.
      
    Other sources (adafruit): 3-5V for Vin.
    
    We will use 3.3V for safety.
      
3. What is the control flow?
      
    - Does it need enabling or configuring?
            
        Yes.
            
    - Does it measure automatically on demand?
      
        Automatically.
         
    - How do you configure it?
    
        It needs to set the refresh rate, resolution, BDU (block data update), range and enable axis.
        
    - How do you request a measurement?
    
        You don't.
        
    - How do you read back the result?
    
        Each of the axis readings are stored in two registers each: X in 0x28(L) and 0x29(H), Y in 0x2A(L) and 0x2B(H), Z in 0x2C(L) and 0x2D(H). For the temperature, we read 0x0C (needs enabling).
        
    - What conversion is needed to make the result meaningful?
    
        The accelerometer readings are always in m/s^2. The temp reading must be divided by 256.
