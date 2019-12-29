SRCDIR=.
AMSCRIPT=${SRCDIR}/am_steps
LEXICONDIR=${SRCDIR}/Lexicons
LEXICONPHONES=${SRCDIR}/lexicon_phones
TRNDIR=${SRCDIR}/Trns
CONFIGDIR=${SRCDIR}/Configs
AMDIR=${SRCDIR}/AMs
G2P=${SRCDIR}/G2P
TMPDIR=${SRCDIR}/tmpdir
FEATUREDIR=${SRCDIR}/features
ALIGNDIR=${SRCDIR}/alignments


if [ -d /home/huser/kaldi-181025 ]; then
	#export KALDI_ROOT=/home/huser/kaldi-191223
	export KALDI_ROOT=/home/huser/kaldi-181025
else
	export KALDI_ROOT=/mnt/kaldi_bin
fi
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh 
export PATH=$PWD/utils/:$KALDI_ROOT/src/bin:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/src/fstbin/:$KALDI_ROOT/src/gmmbin/:$KALDI_ROOT/src/featbin/:$KALDI_ROOT/src/lm/:$KALDI_ROOT/src/sgmmbin/:$KALDI_ROOT/src/sgmm2bin/:$KALDI_ROOT/src/fgmmbin/:$KALDI_ROOT/src/latbin/:$KALDI_ROOT/src/nnetbin:$KALDI_ROOT/src/nnet2bin/:$KALDI_ROOT/src/kwsbin:$KALDI_ROOT/src/online2bin/:$KALDI_ROOT/src/ivectorbin/:$KALDI_ROOT/src/lmbin/:$KALDI_ROOT/src/nnet3bin/:$PWD:$PATH
export LC_ALL=C
