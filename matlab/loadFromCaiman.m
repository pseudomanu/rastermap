% load spks and check out results
% ops.nC = 6, number of clusters to use 
% ops.iPC = 1:100, number of PCs to use 
% ops.isort = [], initial sorting, otherwise will be the top PC sort
% ops.useGPU = 0, whether to use the GPU
% ops.upsamp = 100, upsampling factor for the embedding position
% ops.sigUp = 1, % standard deviation for upsampling

%clear all;

ops.nC = 5;
ops.iPC = 1:50;
ops.isort = [];
ops.useGPU = 0;
ops.upsamp = 50;
ops.sigUp = 1;

load('D:\Analysis\2P\C57_J1M2\03042022\run2\results_caiman.mat','df_wo_bckgrnd','deconv_spk');
S_spk = deconv_spk;
S_df = df_wo_bckgrnd;

% full algorithm on df
[isort1_df, isort2_df, Sm_df] = mapTmap(S_df,ops);

% run map on df neurons without smoothing across time sorting
[iclustup_df, isort_df, Vout_df] = activityMap(S_df,ops);

figure;
subplot(4,1,1);
imagesc(zscore(S_df,1,2),[0,3])
title('original df raster');
subplot(4,1,2);
imagesc(zscore(S_df(isort_df,:),1,2),[0,3])
title('activityMap of df_f');
subplot(4,1,3);
imagesc(zscore(S_df(isort1_df,:),1,2),[0,3])
title('mapTmap of df_f wo smoothing in resorted time');
subplot(4,1,4);
imagesc(zscore(Sm_df,1,2),[0,3]);
title('mapTmap of df_f with smoothing in resorted time');

% full algorithm on spk
[isort1_spk, isort2_spk, Sm_spk] = mapTmap(S_spk,ops);

% run map in neurons without smoothing across time sorting
[iclustup_spk, isort_spk, Vout_spk] = activityMap(S_spk,ops);

figure;
subplot(4,1,1);
imagesc(zscore(S_spk,1,2),[0,3])
title('original spk raster');
subplot(4,1,2);
imagesc(zscore(S_spk(isort_spk,:),1,2),[0,3])
title('activityMap of spk');
subplot(4,1,3);
imagesc(zscore(S_spk(isort1_spk,:),1,2),[0,3])
title('mapTmap of spk wo smoothing in resorted time');
subplot(4,1,4);
imagesc(zscore(Sm_spk,1,2),[0,3]);
title('mapTmap of spk with smoothing in resorted time');

