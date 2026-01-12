clc
clear
 
s=tf('s')
R=100;
L=33E-3;
tau=L/R;
Ein=5/s;
 
 
G=__________
Vout=Ein*G
 
ltiview('impulse',Vout)
