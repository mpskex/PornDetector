clear();
data = textread('prob.mat');
sz = size(data);
t = zeros(1,sz(2));
f = zeros(1,sz(2));
ti = 1;
fi = 1;
for i = 1:length(data)
    if data(i,1) == 1
        t(ti, :) = data(i, :);
        ti = ti + 1;
    else
        f(fi, :) = data(i, :);
        fi = fi + 1;
    end
end
tX = t(:, 2);
tY = t(:, 3);
tZ = t(:, 5);
fX = f(:, 2);
fY = f(:, 3);
fZ = f(:, 5);
scatter3(tX, tY, tZ, 'b', '<');
hold on;
scatter3(fX, fY, fZ, 'r', 'o');