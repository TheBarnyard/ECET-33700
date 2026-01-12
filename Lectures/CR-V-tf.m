clc
clear
 
s=tf('s')
R=1e3;
C=200e-9;
tau=R*C;
Ein=5/s;
 
 
G=tau*s/(tau*s+1)
Vout=Ein*G
 
ltiview('impulse',Vout)
