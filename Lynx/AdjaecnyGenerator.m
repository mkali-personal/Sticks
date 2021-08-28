function [ A, Clusters ] = AdjaecnyGenerator( Size, NumOfClusters )
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

% Size = 8;
% NumOfClusters = 4;

v = rand([Size,1]);
A = v*v';
Clusters = zeros(size(v));


for c = 1: NumOfClusters
    for g = 1+((Size/NumOfClusters)*(c-1)):(((Size/NumOfClusters)*(c)))
        Clusters(g) = c;
        for h = 1+((Size/NumOfClusters)*(c-1)):(((Size/NumOfClusters)*(c)))
            A(g,h) = A(g,h) * 100;
        end
    end
end
A = round(A);


end

