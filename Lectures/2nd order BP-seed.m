clear
format short G
s=tf('s')

Ao=___;
wo=___;
alpha=___;

G=__________________________

opts = bodeoptions('cstprefs');
opts.FreqUnits = 'Hz';
opts.grid = 'on';
opts.PhaseWrapping = 'on';
opts.MagLowerLimMode = 'manual';
opts.MagLowerLim = -90;

bodeplot(G,{1e2,1e6},opts);
