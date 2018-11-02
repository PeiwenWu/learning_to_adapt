#!/bin/bash

. path.sh
. cmd.sh

# TODO: Use locking script to obtain GPU
export CUDA_VISIBLE_DEVICES=2
export TF_CPP_MIN_LOG_LEVEL=2

ali="exp/kaldi_tdnn_subset/align_train_cleaned_hires_split_01/"

data="data/train_cleaned_hires_split_01/"
utt2spk=$data/utt2spk
pdfs="ark:ali-to-pdf $ali/final.mdl ark:'gunzip -c $ali/ali.*.gz |' ark,t:- |"
left_context=-16
right_context=12
lda="lda.txt"
output="exp/tdnn_am_850_dataset_api/"


num_splits=1000
if [ ! -d $data/keras_train_split ]; then
    mkdir $data/keras_train_split

    sort -R $data/feats.scp > $data/keras_train_split/feats.scp
    split --additional-suffix .scp --numeric-suffixes -n l/$num_splits -a 4 $data/keras_train_split/feats.scp $data/keras_train_split/feats_

    mkdir $data/keras_val_split
    mv $data/keras_train_split/feats_09*.scp $data/keras_val_split
fi


mkdir -p $output
python2.7 steps/nnet3/train.py $data/keras_train_split $data/keras_val_split $utt2spk "$pdfs" $left_context $right_context $lda $output