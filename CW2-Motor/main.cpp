#include "mbed.h"
#include "SHA256.h"
#include "rtos.h"

//---------------------------------------------------------------------- THREADS

//Threads
Thread MotorCtrlT(osPriorityNormal, 1024);
Thread CommOutT(osPriorityNormal, 1024);
Thread Decode(osPriorityRealtime, 1024);

//-------------------------------------------------------- FUNCTION DECLARATIONS

// Motor control
void motorOut(int8_t driveState, uint32_t torque);
inline int8_t readRotorState();
int8_t motorHome();
void motorISR();
void motorCtrlFn();
void motorCtrlTick();

// Messaging
void putMessage(uint8_t code, uint32_t data);
void commOutFn();

// Commands
void serialISR();
void decodeFn();

// Bitcoin mining
void bitcoinStuff();

//----------------------------------------------- GLOBAL VARIABLE INITIALISATION

// Photointerrupter input pins
#define I1pin D2
#define I2pin D11
#define I3pin D12

// Incremental encoder input pins
#define CHA   D7
#define CHB   D8  

// Motor Drive output pins   //Mask in output byte
#define L1Lpin D4           //0x01
#define L1Hpin D5           //0x02
#define L2Lpin D3           //0x04
#define L2Hpin D6           //0x08
#define L3Lpin D9           //0x10
#define L3Hpin D10          //0x20

// Mapping from sequential drive states to motor phase outputs
/*
State   L1  L2  L3
0       H   -   L
1       -   H   L
2       L   H   -
3       L   -   H
4       -   L   H
5       H   L   -
6       -   -   -
7       -   -   -
*/

//a unique code for each message type
enum messageType
{
    start = 0,
    rotor_origin = 1,
    motor_speed = 2,
    bitcoinNonce_lower = 3,
    motor_power = 4,
    max_speed = 5
};

// Drive state to output table
const int8_t driveTable[] = {0x12,0x18,0x09,0x21,0x24,0x06,0x00,0x00};

// Mapping from interrupter inputs to sequential rotor states.
// 0x00 and 0x07 are not valid
const int8_t stateMap[] = {0x07,0x05,0x03,0x04,0x01,0x00,0x02,0x07};
//Alternative if phase order of input or drive is reversed:
//const int8_t stateMap[] = {0x07,0x01,0x03,0x02,0x05,0x00,0x04,0x07}; 

// Phase lead to make motor spin
int8_t lead = 2;  //2 for forwards, -2 for backwards

// Rotor offset at motor state 0
int8_t orState = 0;

//Mail template
typedef struct{ 
    uint8_t code;
    uint32_t data; 
} message_t ;

// Status LED
DigitalOut led1(LED1);

// Photointerrupter inputs
InterruptIn I1(I1pin);
InterruptIn I2(I2pin);
InterruptIn I3(I3pin);

// Motor Drive outputs
PwmOut L1L(L1Lpin);
PwmOut L2L(L2Lpin);
PwmOut L3L(L3Lpin);
DigitalOut L1H(L1Hpin);
DigitalOut L2H(L2Hpin);
DigitalOut L3H(L3Hpin);

//declare char_array for decode function
char char_array[50] = {0};
Queue<void, 8> inCharQ;

//Initialise the serial port
RawSerial pc(SERIAL_TX, SERIAL_RX);
//Initialise the mail outmessage
Mail<message_t,8> outMessages;

// bitcoin key setting w/ command
volatile uint64_t newKey = 0;
Mutex newKey_mutex;

// motor control
volatile int32_t motorPower = 500; // used to be uint like in spec
volatile int32_t motorPosition;

// set rotation speed w/ command
//volatile double maxSpeed;
//Mutex maxSpeed_mutex;
//volatile float maxSpeed;
volatile double maxSpeed = 0;
Mutex maxSpeed_mutex;

//------------------------------------------------------------------------- MAIN

int main() {
    
    // indicate start of main code
    putMessage(start, 0);
    
    // set PWM control
    L1L.period_us(2000);
    L2L.period_us(2000);
    L3L.period_us(2000);
    
    // Run the motor synchronisation
    orState = motorHome();
    
    wait(1.0);
    
    // Starting the threads
    CommOutT.start(commOutFn);
    Decode.start(decodeFn);
    MotorCtrlT.start(motorCtrlFn);
    
    putMessage(rotor_origin, orState);
    //orState is subtracted from future rotor state inputs
    //to align rotor and motor states
    
    //Poll the rotor state and set the motor outputs accordingly
    //to spin the motor
    I1.rise(&motorISR);
    I1.fall(&motorISR);
    I2.rise(&motorISR);
    I2.fall(&motorISR);
    I3.rise(&motorISR);
    I3.fall(&motorISR);
    
    bitcoinStuff();
}

//---------------------------------------------------------------- MOTOR CONTROL

// Set a given drive state
void motorOut(int8_t driveState, uint32_t torque){
    
    // Lookup the output byte from the drive state.
    int8_t driveOut = driveTable[driveState & 0x07];
    
    // Turn off first
    if (~driveOut & 0x01) L1L.pulsewidth_us(0);
    if (~driveOut & 0x02) L1H = 1;
    if (~driveOut & 0x04) L2L.pulsewidth_us(0);
    if (~driveOut & 0x08) L2H = 1;
    if (~driveOut & 0x10) L3L.pulsewidth_us(0);
    if (~driveOut & 0x20) L3H = 1;
    
    // Then turn on
    if (driveOut & 0x01) L1L.pulsewidth_us(torque);
    if (driveOut & 0x02) L1H = 0;
    if (driveOut & 0x04) L2L.pulsewidth_us(torque);
    if (driveOut & 0x08) L2H = 0;
    if (driveOut & 0x10) L3L.pulsewidth_us(torque);
    if (driveOut & 0x20) L3H = 0;
}
    
// Convert photointerrupter inputs to a rotor state
inline int8_t readRotorState(){
    return stateMap[I1 + 2*I2 + 4*I3];
}

// Basic synchronisation routine    
int8_t motorHome() {
    //Put the motor in drive state 0 and wait for it to stabilise
    // TODO: ask if max means 2000us or 50% duty cycle (1000us)
    motorOut(0, 2000);
    wait(1.0);
    
    //Get the rotor state
    return readRotorState();
}

// Interrupt routine to drive motor forwards by 1 step
void motorISR () {
    
    static int8_t oldRotorState;
    int8_t rotorState = readRotorState();
    int32_t motorPower_old = 0;
    int32_t torque = 0;
    
    // calculate PWM value from input motorPower
    if (motorPower_old != motorPower) {
        torque = motorPower;
        if(torque < 0) {
            torque = -torque;
            lead = -2;
        } else {
            lead = 2;
        }
        if(torque > 1000) torque = 1000;
        //pc.printf("new torque: %d\r\n", torque);
    }
    motorOut((rotorState-orState+lead+6)%6, torque);
    motorPower_old = motorPower;
    
    if (rotorState - oldRotorState == 5) {
        motorPosition--;
    } else if (rotorState - oldRotorState == -5) {
        motorPosition++;
    } else {
        motorPosition += (rotorState - oldRotorState);
    }
    oldRotorState = rotorState;
}

// motor controlled thread fn
void motorCtrlFn() {
    
    // execute every 100ms (0.1s)
    Ticker motorCtrlTicker;
    motorCtrlTicker.attach_us(&motorCtrlTick, 100000);
    
    int32_t motorPos_old = motorPosition;
    int32_t velocity = 0;
    int32_t i = 0;
    int32_t k_p = 10;
    
    while(1) {
        i++;
        MotorCtrlT.signal_wait(0x1);
        // TODO: add timer to count time (not=10)
        
        if (i%10 == 0) {
            velocity = (motorPosition - motorPos_old)*10;
            motorPos_old = motorPosition;
            putMessage(motor_speed, velocity);
            
            maxSpeed_mutex.lock();
            //putMessage(max_speed, maxSpeed);
            if(velocity < 0) velocity = -velocity;
            motorPower = k_p *(maxSpeed - velocity);
            maxSpeed_mutex.unlock();
            putMessage(motor_power, motorPower);
        }
    }
}

// timer for motor control
void motorCtrlTick(){
    MotorCtrlT.signal_set(0x1);
}

//-------------------------------------------------------------------- MESSAGING

//putMessage - separate function that adds messages to the queue
void putMessage(uint8_t code, uint32_t data){
     //*pMessage is a pointer which points to the memory location
     //where the message will be stored
     message_t *pMessage = outMessages.alloc(); 
     pMessage->code = code;
     pMessage->data = data; 
     //put() places the message pointer in the queue
     outMessages.put(pMessage);
}

//commOutFn - take messages from the queue and print them on the serial port
void commOutFn(){
    
    while(1) {
        osEvent newEvent = outMessages.get();
        message_t *pMessage = (message_t*)newEvent.value.p;
        //pc.printf("%d: with data 0x%016x\n\r", pMessage->code,pMessage->data);
        
        switch(pMessage->code) {
            case start:
                pc.printf("PROGRAM START --------------------\r\n");
                break;
            case rotor_origin:
                pc.printf("Rotor origin: %d\r\n", pMessage->data);
                break;
            case motor_speed:
                pc.printf("Velocity: %d\r\n", pMessage->data);
                break;
            case bitcoinNonce_lower:
                pc.printf("Nonce found: 0x%016x\r\n", pMessage->data);
                break;
            case motor_power:
                pc.printf("MotorPower: %d\r\n", pMessage->data);
                break;
            case max_speed:
                pc.printf("Max speed: lf\r\n", pMessage->data);
                break;
            default:
                break;
        }
        
        outMessages.free(pMessage);
    }    
}

//--------------------------------------------------------------------- COMMANDS

//SerialISR - retrieves a byte from the serial port(pc)
//and places it on the queue 
void serialISR(){
    uint8_t newChar = pc.getc();
    inCharQ.put((void*)newChar);
}

//thread to decode commands   
void decodeFn(){  
    int array_pos = 0;
    //attaching serialISR to the serial port(pc)
    pc.attach(&serialISR);
    while(1) {
        osEvent newEvent = inCharQ.get();
        uint8_t newChar = (uint8_t)newEvent.value.p; 
        
        // testing that we do not write past the end of the buffer
        // if the incoming string is too long
        if(array_pos < sizeof(char_array) ){
            char_array[array_pos] = newChar; 
            array_pos++;
            
            if(newChar == '\r'){
                // end of command reached, time to decode
                char_array[array_pos] = '\0';
                array_pos = 0;
                
                // check first character
                switch(char_array[0]) {
                    case 'R': 
                        // do rotation
                        break;
                    case 'V': 
                        // do max speed
                        maxSpeed_mutex.lock();
                        sscanf(char_array, "V%lf", &maxSpeed);
                        pc.printf("New maxSpeed: %lf\r\n", maxSpeed);
                        maxSpeed_mutex.unlock();
                        break;
                    case 'K':
                        // set bitcoin key
                        newKey_mutex.lock();
                        sscanf(char_array, "K%x", &newKey);
                        newKey_mutex.unlock();
                        break;
                    default:
                        // do nothing?
                        break;
                }
            }
        }
    }
}

//--------------------------------------------------------------- BITCOIN MINING

void bitcoinStuff() {
    
    // Bitcoin stuff
    SHA256 sha;
    uint8_t sequence[] = {0x45,0x6D,0x62,0x65,0x64,0x64,0x65,0x64,
                          0x20,0x53,0x79,0x73,0x74,0x65,0x6D,0x73,
                          0x20,0x61,0x72,0x65,0x20,0x66,0x75,0x6E,
                          0x20,0x61,0x6E,0x64,0x20,0x64,0x6F,0x20,
                          0x61,0x77,0x65,0x73,0x6F,0x6D,0x65,0x20,
                          0x74,0x68,0x69,0x6E,0x67,0x73,0x21,0x20,
                          0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                          0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
    uint64_t* key = (uint64_t*)((int)sequence + 48);
    uint64_t* nonce = (uint64_t*)((int)sequence + 56);
    uint8_t hash[32];
    
    uint64_t i = 0;
    while (1) {
        
        newKey_mutex.lock();
        if (newKey != *key) {
            *key = newKey;
            //pc.printf("newKey: %lu\n\r", *key);
            i = 0;
        }
        newKey_mutex.unlock();
        
        *nonce = i;
        sha.computeHash(hash, sequence, 64);
        if ((hash[0] || hash[1]) == 0) {
            // Send message reporting good nonce
            uint32_t nonce_lower  = (uint32_t) *nonce;
            putMessage(bitcoinNonce_lower, nonce_lower);
            //pc.printf("nonce found: %ul\n\r", *nonce);
        }
        i++;
    }  
}
