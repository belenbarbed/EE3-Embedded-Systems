# EE3-Embedded-Systems - CW2

### For Testing & Debugging

Sending commands to device through COM

    set /p x="command\r" <nul >\\.\COM9
    
Setup sending comm. parameters

    mode COM9 BAUD=9600 PARITY=n DATA=8

Reading from the device (without PuTTy)

    type COM9
