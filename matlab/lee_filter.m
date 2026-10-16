function filtered_img = lee_filter(img, window_size, cu)
% LEE_FILTER Bo loc Lee giam nhieu dom (Speckle) tren anh SAR Sentinel-1
% 
% CU PHAP:
%   filtered_img = lee_filter(img, window_size, cu)
%
% DAU VAO:
%   img         : Anh xam dau vao (double hoac uint8, gia tri [0, 1] hoac [0, 255])
%   window_size : Kich thuoc cua so truot (thuong la 5 hoac 7, mac dinh: 5)
%   cu          : He so bien thien nhieu u (mac dinh: 0.523 cho anh SAR 1-look,
%                 hoac de trong de tu dong uoc luong tu phuong sai cuc bo)
%
% DAU RA:
%   filtered_img: Anh sau khi loc nhieu Lee, giu duoc bien vet dau sac net

    if nargin < 2 || isempty(window_size)
        window_size = 5;
    end

    was_uint8 = isa(img, 'uint8');
    img_double = im2double(img);

    % Tao kernel lay trung binh cuc bo
    h = ones(window_size, window_size) / (window_size^2);

    % Tinh trung binh cuc bo (mu_k)
    local_mean = imfilter(img_double, h, 'symmetric');

    % Tinh phuong sai cuc bo (sigma_k^2)
    local_sq_mean = imfilter(img_double.^2, h, 'symmetric');
    local_var = max(0, local_sq_mean - local_mean.^2);

    % He so bien thien tin hieu Ci = sigma_k / mu_k
    Ci = sqrt(local_var) ./ (local_mean + eps);

    % Neu khong truyen cu, uoc luong cu bang trung vi cua Ci o vung bien dong nhat
    if nargin < 3 || isempty(cu)
        cu = median(Ci(:)) * 0.5;
        if cu <= 0, cu = 0.523; end
    end

    % Tinh trong so Lee: W_k = max(0, 1 - (Cu^2 / Ci^2))
    weight = max(0, 1 - (cu^2) ./ (Ci.^2 + eps));
    weight = min(1, weight); % Gioi han trong doan [0, 1]

    % Uoc luong tin hieu goc: R_hat = mu_k + W_k * (I - mu_k)
    filtered_double = local_mean + weight .* (img_double - local_mean);
    filtered_double = max(0, min(1, filtered_double));

    if was_uint8
        filtered_img = im2uint8(filtered_double);
    else
        filtered_img = filtered_double;
    end
end
