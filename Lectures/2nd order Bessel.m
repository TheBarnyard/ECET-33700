clear
format short G
s=tf('s')

Ao=1;
fo=1E3;
wo=2*pi*fo;
zeta=0.866;

G=Ao*wo^2/(s^2+2*zeta*wo*s+wo^2)

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e2,100e3},opts);
