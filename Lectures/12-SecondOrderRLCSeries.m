clc
clear
s=tf('s')
R1=3.3e3;
R2=1.68e3;
R3=820;
L=33e-3;
C=47e-9;
G_over=(1/(L*C))/(s^2+(R1/L)*s+(1/(L*C)))
G_critical=(1/(L*C))/(s^2+(R2/L)*s+(1/(L*C)))
G_under=(1/(L*C))/(s^2+(R3/L)*s+(1/(L*C)))
ltiview(G_under)

S=stepinfo(G_under,'SettlingTimeThreshold', 0.05)