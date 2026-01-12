clear
format short G
s=tf('s')
 
Ao=1.3;
f3dB=6100;

fo1=f3dB/2.146;
wo1=2*pi*fo1;
fo2=f3dB/1.057;
wo2=2*pi*fo2;

alpha1=1.088;
alpha2=0.224;
 
G=Ao*(wo1^2/(s^2+alpha1*wo1*s+wo1^2))*(wo2^2/(s^2+alpha2*wo2*s+wo2^2))

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e2,1e6},opts);


