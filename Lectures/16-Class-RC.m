clc
clear
s=tf('s')

R=1000;
C=0.5e-6;
tau=R*C
wo=1/tau
fo=wo/(2*pi)

G=tau*s/(tau*s+1);


opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e2,1e6},opts);
