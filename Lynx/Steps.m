function [ X_steps, Y_steps] = Steps( A, Coordinates, alpha, beta )
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
% 
% A = AdjaecnyGenerator(9, 3);
% Coordinates = rand(2,size(A,1))*100;
% alpha = 0.00015;
% beta = 0.00015;
sizes = sum(A)

%distance (i,j) value contains the euclidian distance beteen the i'th and j'th
%arguments.
Distances = zeros(size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        Distances(i,j) = sqrt(sum((Coordinates(:,i)-Coordinates(:,j)).^2)) - 20;
    end
end

%Xdirections (i,j) value contains the X factor of the vector pointing
%from the i'th argument to the j'th argument.
Xdirections = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        Xdirections(i,j) = Coordinates(1,j) - Coordinates(1,i);
    end
end

%Ydirections (i,j) value contains the Y factor of the vector pointing
%from the i'th argument to the j'th argument.
Ydirections = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        Ydirections(i,j) = Coordinates(2,j) - Coordinates(2,i);
    end
end

%X_to_steps is a row vector, in which every value(i),
%contains the sum of the X steps to all the connected Vertices.
%It is comptuted as so:
%The X factor of the vector between the two vertices * the distance between
%them * the strength of their connection * a constant.
X_to_steps = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        X_to_steps(i,j) = (Xdirections(i,j) * Distances(i,j) * A(i,j) - 1) * alpha;
    end
end


X_to_steps = sum(X_to_steps') ./ sizes;

%The same for the Y steps:
Y_to_steps = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        Y_to_steps(i,j) = Ydirections(i,j) * Distances(i,j) * A(i,j) * alpha;
    end
end

Y_to_steps = sum(Y_to_steps') ./ sizes;

%X_from_steps is a row vector, in which every value(i),
%contains the sum of the X steps from all the not-connected Vertices.
%It is comptuted as so:
%(-100) (negative because it is repulsive) * The X factor of the vector
%between the two vertices * 1 / (the distance +10) * constant
% 
%then * wether they are connected or not * a constant.

X_from_steps = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        if A(i,j) ==0
        X_from_steps(i,j) = (-100) * Xdirections(i,j) / (Distances(i,j) + 10) * beta;
        end
    end
end
X_from_steps = sum(X_from_steps') ./ sizes;


Y_from_steps = zeros (size(A));
for i = 1:size(A)
    for j = i+1:size(A)
        if A(i,j) == 0
        Y_from_steps(i,j) = (-100) * Ydirections(i,j) / (Distances(i,j)+10)* beta;
        end
    end
end
Y_from_steps = sum(Y_from_steps') ./ sizes;


X_steps = X_from_steps + X_to_steps;

Y_steps = Y_from_steps + Y_to_steps;


end

