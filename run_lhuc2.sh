#!/bin/bash

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

nj=4
dir=exp/G2KHAA30d
configs=$dir/configs
mkdir -p $configs
rm -rf $configs/*
for lr in 0.4 0.5 0.6; do
    for epochs in 1 3 5; do
        name="lhuc_${lr}_${epochs}"
        echo "{\"lr\": $lr, \"epochs\": $epochs}" > $configs/$name.json
        echo -e "${name}\t${configs}/${name}.json" >> $configs/experiments.scp
    done
done

mkdir -p $configs/split${nj}
for job in `seq 1 $nj`; do
    utils/split_scp.pl -j $nj $((job-1)) $configs/experiments.scp $configs/split${nj}/$job.scp
done

#for dataset in dev2010 tst2010 tst2011; do
for dataset in train_S_KR_CSTT_Appliance_Jeolla_1st2nd; do
    data=data/${dataset}
    pdfs=data/ali_S_KR_CSTT_Appliance_Jeolla_1st2nd/
    frames=1000
    model=exp/G2KHAA30d/
    graph=exp/graph_G2aKARCHL0Wb2th46c/
    decode_dir=$dir/decode_${dataset}

    ln -s $model/final.mdl $decode_dir/final.mdl
    ln -s data/lang $decode_dir/lang
    #ln -s `pwd`/local/scoring/stms/ted.${dataset}.en-fr.en.norm.stm $decode_dir/stm

    echo "Decoding: $dataset"
    steps/create_splits_by_spk.sh $data
    $train_cmd JOB=1:$nj $decode_dir/log/experiments.JOB.log \
        steps/run_experiments.sh LHUC $configs/split${nj}/JOB.scp $data $pdfs $frames $model $graph $decode_dir

    echo
    echo "Best result $dataset"
    grep "Percent Total Error" $decode_dir/*/*/best_wer | sed 's/:.*= */ /;s/%.*/%/;' | sort -n -k2,2 | head -n 1
done;
