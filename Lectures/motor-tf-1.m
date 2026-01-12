clc
clear
 
s=tf('s')
tau=0.3;  %motor's time constant
m=2.78;   %motors "gain" in (rev/sec)/V

Gmotor=m/(tau*s+1);  %motor's first order lag transfer function
Ein=12/s;   %input step
 
W=Ein*Gmotor;  %motor's speed

 
ltiview('impulse',W)
