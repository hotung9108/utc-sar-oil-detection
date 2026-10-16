function bw_dark = adaptive_thresholding(img, method, param)
% ADAPTIVE_THRESHOLDING Phan nguong thich nghi tach vet toi ung vien tren anh SAR
%
% CU PHAP:
%   bw_dark = adaptive_thresholding(img, method, param)
%
% DAU VAO:
%   img    : Anh xam da duoc loc nhieu (uint8 hoac double [0, 1])
%   method : 'sauvola' (mac dinh), 'statistical', hoac 'local_otsu'
%   param  : Cau truc hoac he so tham so:
%            - 'sauvola': param.window (mac dinh 35), param.k (mac dinh 0.25)
%            - 'statistical': k (nguong = mu_sea - k * std_sea, mac dinh 1.8)
%
% DAU RA:
%   bw_dark: Mat na nhi phan (logical) trong do pixel 1 la vung toi (ung vien dau)

    if nargin < 2 || isempty(method)
        method = 'sauvola';
    end

    img_d = im2double(img);

    switch lower(method)
        case 'sauvola'
            win = 35;
            k = 0.25;
            R = 0.5; % Gia tri R cho dải ảnh [0, 1]
            if nargin >= 3 && isstruct(param)
                if isfield(param, 'window'), win = param.window; end
                if isfield(param, 'k'), k = param.k; end
            end
            
            h = ones(win, win) / (win^2);
            l_mean = imfilter(img_d, h, 'symmetric');
            l_sq_mean = imfilter(img_d.^2, h, 'symmetric');
            l_std = sqrt(max(0, l_sq_mean - l_mean.^2));
            
            % Cong thuc nguong Sauvola: T = mean * (1 + k * (std / R - 1))
            T = l_mean .* (1 + k .* (l_std ./ R - 1));
            
            % Vet dau tren SAR bieu hien bang vung toi hon nguong
            bw_dark = (img_d < T);

        case 'statistical'
            k = 1.8;
            if nargin >= 3 && isnumeric(param)
                k = param;
            end
            
            % Tinh thong ke toan anh (gia thiet phan lon la nen bien)
            mu_sea = mean(img_d(:));
            sigma_sea = std(img_d(:));
            
            T = mu_sea - k * sigma_sea;
            bw_dark = (img_d < T);

        case 'local_otsu'
            win = 45;
            if nargin >= 3 && isnumeric(param)
                win = param;
            end
            % Su dung adaptthresh cua MATLAB Image Processing Toolbox
            T = adaptthresh(img_d, 0.4, 'NeighborhoodSize', [win win], 'Statistic', 'median');
            bw_dark = (img_d < T);

        otherwise
            error('Phuong phap khong hop le. Chon sauvola, statistical, hoac local_otsu.');
    end
end
