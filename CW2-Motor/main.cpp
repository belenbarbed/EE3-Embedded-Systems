#include "mbed.h"
#include "SHA256.h"
#include "rtos.h"

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
    bitcoinNonce = 0
};

// Drive state to output table
const int8_t driveTable[] = {0x12,0x18,0x09,0x21,0x24,0x06,0x00,0x00};

// Mapping from interrupter inputs to sequential rotor states. 0x00 and 0x07 are not valid
const int8_t stateMap[] = {0x07,0x05,0x03,0x04,0x01,0x00,0x02,0x07};  
//const int8_t stateMap[] = {0x07,0x01,0x03,0x02,0x05,0x00,0x04,0x07}; //Alternative if phase order of input or drive is reversed

// Phase lead to make motor spin
const int8_t lead = 2;  //2 for forwards, -2 for backwards

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
//DigitalIn I1(I1pin);
//DigitalIn I2(I2pin);
//DigitalIn I3(I3pin);
InterruptIn I1(I1pin);
InterruptIn I2(I2pin);
InterruptIn I3(I3pin);

// Motor Drive outputs
DigitalOut L1L(L1Lpin);
DigitalOut L1H(L1Hpin);
DigitalOut L2L(L2Lpin);
DigitalOut L2H(L2Hpin);
DigitalOut L3L(L3Lpin);
DigitalOut L3H(L3Hpin);

//declare char_array for decode function
char char_array[100] = {0}; 

//Threads
Thread CommOutT;
Thread Decode;
Queue<void, 8> inCharQ;

//Initialise the serial port
RawSerial pc(SERIAL_TX, SERIAL_RX);
//Initialise the mail outmessage
Mail<message_t,16> outMessages;
//function prototype - take messages from the queue and print them on the serial port
void commOutFn();
// Set a given drive state

void motorOut(int8_t driveState){
    
    // Lookup the output byte from the drive state.
    int8_t driveOut = driveTable[driveState & 0x07];
    
    // Turn off first
    if (~driveOut & 0x01) L1L = 0;
    if (~driveOut & 0x02) L1H = 1;
    if (~driveOut & 0x04) L2L = 0;
    if (~driveOut & 0x08) L2H = 1;
    if (~driveOut & 0x10) L3L = 0;
    if (~driveOut & 0x20) L3H = 1;
    
    // Then turn on
    if (driveOut & 0x01) L1L = 1;
    if (driveOut & 0x02) L1H = 0;
    if (driveOut & 0x04) L2L = 1;
    if (driveOut & 0x08) L2H = 0;
    if (driveOut & 0x10) L3L = 1;
    if (driveOut & 0x20) L3H = 0;
}
    
// Convert photointerrupter inputs to a rotor state
inline int8_t readRotorState(){
    return stateMap[I1 + 2*I2 + 4*I3];
}

// Basic synchronisation routine    
int8_t motorHome() {
    //Put the motor in drive state 0 and wait for it to stabilise
    motorOut(0);
    wait(1.0);
    
    //Get the rotor state
    return readRotorState();
}

//SerialISR - retrieces a byte from the serial port(pc) and places on the queue 
void serialISR(){
    uint8_t newChar = pc.getc();
    inCharQ.put((void*)newChar);
}

//putMessage - separate function that adds messages to the queue
void putMessage(uint8_t code, uint32_t data){
     //*pMessage is a pointer which points to the memory location the message will be stored
     message_t *pMessage = outMessages.alloc(); 
     pMessage->code = code;
     pMessage->data = data; 
     //put() places the message pointer in the queue
     outMessages.put(pMessage);
}

// Interrupt routine to drive motor forwards by 1 step
void motorISR () {    
    int8_t intState = 0;
    int8_t intStateOld = 0;
    
    intState = readRotorState();
    if (intState != intStateOld) {
        intStateOld = intState;
        motorOut((intState-orState+lead+6)%6); //+6 to make sure the remainder is positive
    }
}


//commOutFn - take messages from the queue and print them on the serial port
void commOutFn(){
    
    while(1) {
        osEvent newEvent = outMessages.get();
        message_t *pMessage = (message_t*)newEvent.value.p;
        pc.printf("Message %d with data 0x%016x\n",
        pMessage->code,pMessage->data); outMessages.free(pMessage);
    }    
}
   
//thread to decode commands   
void decodeFn(){  
    int array_pos = 0;
    //attaching serialISR to the serial port(pc)
    pc.attach(&serialISR);
    while(1) {
    osEvent newEvent = inCharQ.get();
    uint8_t newChar = (uint8_t)newEvent.value.p; 
    
    //testing that we do not write past the end of the buffer is the incoming string is too long
    if(array_pos < sizeof(char_array) ){
        char_array[array_pos] = newChar; 
        array_pos++;
        
        if(newChar == '\r'){
            char_array[array_pos] = '\0';
            array_pos = 0;
            } //TEST HERE!
            
 //************PARSE HERE*****************       
        }  
    }    
}

void bitcoinStuff(){
    
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
    
    uint64_t i = *nonce;
    while (1) {
        *nonce = i;
        sha.computeHash(hash, sequence, 64);
        if ((hash[0] || hash[1]) == 0) {
            pc.printf("nonce found: %ul\n\r", *nonce);
            //
        }
        i++;
    }  
}


   
//Main
int main() {
    
    //Starting the thread
    CommOutT.start(commOutFn);
    
    pc.printf("Hello\n\r");
    
    //Run the motor synchronisation
    orState = motorHome();
    pc.printf("Rotor origin: %x\n\r",orState);
    //orState is subtracted from future rotor state inputs to align rotor and motor states
    
    //Poll the rotor state and set the motor outputs accordingly to spin the motor
    I1.rise(&motorISR);
    I1.fall(&motorISR);
    I2.rise(&motorISR);
    I2.fall(&motorISR);
    I3.rise(&motorISR);
    I3.fall(&motorISR);
    
    bitcoinStuff();

    //Need to test (instruction 6)
}
