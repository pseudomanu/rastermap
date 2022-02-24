% load from python spks and check out results

load('D:\Analysis\2P\C57_J1M3\02112022\run4to6\results_caiman.mat','df_wo_bckgrnd');
S = df_wo_bckgrnd;

%% full algorithm
[isort1, isort2, Sm] = mapTmap(S);
%imagesc(Sm(:,:),[0,5])

%% run map in neurons without smoothing across time sorting
[iclustup, isort, Vout] = activityMap(S);
%%
figure;
subplot(2,1,1);
imagesc(zscore(S,1,2),[0 3]);
subplot(2,1,2);
imagesc(zscore(S(isort,:), 1, 2), [0 3]);
