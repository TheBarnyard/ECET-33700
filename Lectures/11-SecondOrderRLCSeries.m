clc
clear
s=tf('s')
A=1;
z=0.5;
fo=2e3;
w=2*pi*fo;
tau=1/w;

G=A*w^2/(s^2+2*z*w*s+w^2)

ltiview(G)

S=stepinfo(G,'SettlingTimeThreshold', 0.05)