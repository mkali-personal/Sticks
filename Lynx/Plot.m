A = AdjaecnyGenerator(8, 4);
% A = [A, ones(size(A(:,1)))*50];
% A = [A; ones(size(A(1,:)))*50];
Coordinates = rand(2,size(A,1))*100;
%Atriu = triu(A);

for p = 1:300
[ Xsteps, Ysteps] = Steps( A, Coordinates, 0.00025, 0.00025 );

Coordinates (1,:) = Coordinates (1,:) + Xsteps*10;
Coordinates (2,:) = Coordinates (2,:) + Ysteps*10;
LynxPlot(A,Coordinates);
drawnow;
end

