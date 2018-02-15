# EE3-Embedded-Systems
Product Name : TrackIt.
Website Link :  Home:                  https://kivahussein.wixsite.com/trackit
                Technical aspects:     https://kivahussein.wixsite.com/trackit/behind-the-scenes-1
                Shop page:             https://kivahussein.wixsite.com/trackit/shop

It's scientifically proven that listening to music while running pushes the runner to cover longer distances (endurance) and run faster i.e a great motivator enhacing one's workout.

To solve for this, TrackIt. acts as your running buddy by detecting your tempo and playing music with a +/-5bpm range to match your pace.


How it works:

To calculate the bpm:
As a runner moves they create a rhythmic pulse which can be detected by accelerometer sensors. Examples of this motion are shown in the 
graphs folder of this repo. In order to detect accurately the BPM at which a runner moves we attached the accelerometer to their wrist
and plotted the values of the x-axis acceleration. This was then approximated as a square wave, upon which we used an algorithm to 
determine its periodicity. We implemented a finite state machine which, in state 1, the code waits for a rising edge pulse to go above a specified upper threshold. In state 2, having detected a rising edge, the code waits for the x acceleration value to drop below a specified lower threshold. In this way we have implemented a Schmitt trigger to detect periodicity. We have also implemented a mechanism to ignore noisy pulses, by setting the minimum possible value during which a pulse will be ignored after a pulse is detected. This prevents two close, noisy, consecutive pulses changing the BPM. 
Once the BPM value has been calculated this is passed to the Spotify API. 

To integrate with Spotify API:
We used the spotify API - Spotipy to look through a runner's favorite running playlist that includes songs of all and any tempos. It traverses through your favorite songs and extracts the track's audio features such as tempo, artist and more.
Once the program receives the input_bpm from the user it compares that to the extracted tempos from the tracks and plays the appropriate music in the right range within a +/-5bpm. This takes into account that humans wouldn't naturally run at exactly for example 150bpm but 148bpm or so.



Future Developments:

It would be able to integrate with other API, such as Google Play and iTunes API. We will also add other sensors such as temperature and humidity to keep track of your temperature and the moisture level of your skin as you run. This will be used to give an indicator of your fitness level. There is also the potential to add GPS sensors to keep track of your running location. All of these will fit into the wristband shown on the website. There is also the potential to use machine learning to keep track of the songs that motivate the runner the most by seeing how well a runner keeps up their speed when listening to particular songs. By using Spotify API it is also able to keep track of your preferred artists and suggest songs of the correct bpm based on your artist or genre preferences.  


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
