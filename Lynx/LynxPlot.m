function [ p ] = LynxPlot( A, coordinates )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

% %         A = AdjaecnyGenerator(12, 3)
% %         coordinates = rand(2,size(A,1))*100
clf;
sizes = sum(A)';
Links = [];

for i= 1:size(A,1)
    for j = i+1:size(A,1)
        if A(i,j) > 0 
            l = [coordinates(1,i);coordinates(1,j);coordinates(2,i);coordinates(2,j);A(j,i)];
            Links = [Links,l];
        end
    end
end
limits = coordinates';
edges  = [min(limits(:,1)-10) max(limits(:,1)+10) min(limits(:,2)-10) max(limits(:,2)+10)];
for i = 1:size(Links,2)
plot (Links(1:2,i),Links(3:4,i),'r','linewidth', Links(5,i)/10);
axis(edges);
hold on;
end
scatter (coordinates(1,:), coordinates(2,:), sizes,'filled');

p = 1;


end

