%% This section just outputs the xyz points for Rhino to consume and give the center
%% Before, coming to this file, load calibration data as
%% data = dlmread('calibration.log');

dlmwrite('xyz_file.txt',data(:,1:3))

% go and find the center in Rhino, come back to matlab and say something
% like center = [1,2,3]

%% This guy will for all point locations calculate probeXYZ - center
%% relocate around center

dTipRxTxs = zeros(size(data,1),3);
for i = 1:size(data,1);
    dTipRxTxs(i,:) = data(i,1:3) - center;
end

% you may do the following to see if the last operation made sense
plot3(dTipRxTxs(:,1),dTipRxTxs(:,2),dTipRxTxs(:,3))

%% Now, we'll transform dTipRxTx to dTipRxRx, which, ideally should all be the same

dTipRxRxs = zeros(size(data,1),3);
for i = 1:size(data,1);
    quat = data(i,4:7);
    %quatInv = quatinv(quat);
    dTipRxRxs(i,:) = quatrotate(quat,dTipRxTxs(i,:));
end

plot3(dTipRxRxs(:,1),dTipRxRxs(:,2),dTipRxRxs(:,3));
figure;

plot(dTipRxRxs(:,1),'r');
hold on;
plot(dTipRxRxs(:,2),'g');
plot(dTipRxRxs(:,3),'b');
grid;

