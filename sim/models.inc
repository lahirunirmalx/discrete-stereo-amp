* small-signal and output device models for the stereo amp decks
* BC547B / BC557B: hFE 290 typ (datasheet 200-450 for B grade)
.model BC547B NPN(IS=1.8e-14 BF=290 NF=1 VAF=80 IKF=0.3 ISE=5e-14 NE=1.5 BR=8 RB=10 RE=0.2 RC=0.5 CJE=12p CJC=4p TF=0.4n TR=50n)
.model BC557B PNP(IS=1.8e-14 BF=250 NF=1 VAF=80 IKF=0.3 ISE=5e-14 NE=1.5 BR=8 RB=10 RE=0.2 RC=0.5 CJE=12p CJC=6p TF=0.6n TR=60n)
* BD139 / BD140: datasheet hFE 40 min at 150 mA, 100-250 for -16 grade; BF swept in decks
.model BD139 NPN(IS=4e-13 BF=120 NF=1 VAF=100 IKF=1.5 ISE=1e-12 NE=1.6 BR=5 RB=1 RE=0.08 RC=0.15 CJE=100p CJC=50p TF=8n TR=100n)
.model BD140 PNP(IS=4e-13 BF=100 NF=1 VAF=100 IKF=1.5 ISE=1e-12 NE=1.6 BR=5 RB=1 RE=0.08 RC=0.15 CJE=100p CJC=60p TF=10n TR=120n)
.model D1N4148 D(IS=2.5e-9 N=1.75 RS=0.6 CJO=4p TT=5n BV=100)
