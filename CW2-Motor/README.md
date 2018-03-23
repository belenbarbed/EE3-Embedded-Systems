# EE3-Embedded-Systems - CW2

### Current Questions about CW2
 
  - What is Er? 
     -> Needs changing from Er = noRotations - ((motorPosition - motorPos_old)/6) to noRotations - motorPosition
     -> Also Ed says update all "old" values at end of function
     -> Don't create Er_old, calculate it from motorPos_old? 
  - How do we calculate dEr?
     -> Potentially add timer instead of wait
     -> Change to Er - Er_old, we had it the wrong way round
  - Are position and velocity control meant to be in different places?
     -> See end of spec for how to decide which is more important, can both be in same place though
  - Is Kp common to both control loops?
     -> Can be, but may be better to have two with different values
  - Should velocity control be made more accurate (eg. PD rather than P controller)?
     -> Nah. Mess around with kp, he's not expecting much

### For Testing & Debugging (for Windows)

Sending commands to device through PuTTy

    in Terminal, set "local echo" and "local line editing" to force on
