clear
format short G
s=tf('s')

AodB=10;
Ao=10^(AodB/20)
fo1=1.5E3;
wo1=2*pi*fo1;
Q1=3;
alpha1=1/Q1;

fo2=2.5E3;
wo2=2*pi*fo2;
Q2=3;
alpha2=1/Q2;

G1=Ao*(alpha1*wo1*s/(s^2+alpha1*wo1*s+wo1^2))
G2=Ao*(alpha1*wo1*s/(s^2+alpha1*wo1*s+wo1^2))*(alpha2*wo2*s/(s^2+alpha2*wo2*s+wo2^2))

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G2,{1e2,1e5},opts);
