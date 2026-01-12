clear
format short G
s=tf('s')

AdB=8;
Ao=10^(AdB/20);
f3dB=1e3;
kLP1=0.753;
kLP2=0.687;
a2=1.447;

fo1=f3dB/kLP1;
wo1=2*pi*fo1;
tau1=1/wo1;

fo2=f3dB/kLP2;
wo2=2*pi*fo2;

G=(1/(tau1*s+1))*(Ao*wo2^2/(s^2+a2*wo2*s+wo2^2))

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e3,100e3},opts);
