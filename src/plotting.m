fileID = fopen('../data/data_wrist_180_x.txt', 'r');
all = fscanf(fileID, '%f');
[peaks, idx] = findpeaks(all);

figure(1)
hold on
plot(all)
hold off
title('X acceleration')
xlabel('time (400th of second)')

% size = length(all)/3;
% x = zeros(size);
% y = zeros(size);
% z = zeros(size);
% 
% %for i = 1:length(all)
% i = 1;
% while (i < length(all))
%     
%     val = mod(i,3);
%     switch val
%         case 0 % is z
%             z(i/3) = all(i);
%         case 1 % is x
%             x((i+2)/3) = all(i);
%         case 2 % is y
%             y((i+1)/3) = all(i);
%         otherwise
%             % do nothing
%     end
%     i = i+1;
% end
% 
% figure(1)
% hold on
% plot(x)
% plot(y)
% plot(z)
% hold off
% title('XYZ acceleration')
% xlabel('time (100th of second)')
% legend('x', 'y', 'z')