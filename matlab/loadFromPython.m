% load from python spks and check out results

S = readNPY('D:\Analysis\2P\C57_J1M3\02112022\run1\suite2p\plane0\spks.npy');
iscell = readNPY('D:\Analysis\2P\C57_J1M3\02112022\run1\suite2p\plane0\iscell.npy');
S = S(logical(iscell(:,1)),:);

%% full algorithm
[isort1, isort2, Sm] = mapTmap(S);
figure;imagesc(Sm(:,:),[0,3])
figure;imagesc(zscore(S(isort1,:),1,2),[0,3])

%% run map in neurons without smoothing across time sorting
[iclustup, isort, Vout] = activityMap(S);
%%
figure;imagesc(zscore(S(isort,:), 1, 2), [0 3])
