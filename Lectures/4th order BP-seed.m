clear
format short G
s=tf('s')

Ao=1;
fo1=_____;
fo2=_____;
wo1=2*pi*fo1;
wo2=2*pi*fo2;
alpha=____;

G1=alpha*wo1*s/(s^2+alpha*wo1*s+wo1^2)
G2=alpha*wo2*s/(s^2+alpha*wo2*s+wo2^2)
G=G1*G2*Ao

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e2,1e6},opts);
