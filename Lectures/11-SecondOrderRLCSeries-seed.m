clc
clear
s=tf('s')
R=___;
L=___;
C=___;
G=(1/(L*C))/(s^2+(R/L)*s+(1/(L*C)))
ltiview(G)

S=stepinfo(G,'SettlingTimeThreshold', 0.05)