function [candidates, labeled_img] = extract_features(img, bw_clean, rules)
% EXTRACT_FEATURES Trich xuat dac trung hinh thai & cuong do va phan loai Heuristic
%
% CU PHAP:
%   [candidates, labeled_img] = extract_features(img, bw_clean, rules)
%
% DAU VAO:
%   img         : Anh goc / da loc nhieu (uint8 hoac double [0, 1])
%   bw_clean    : Mat na ung vien sau khi tinh chinh hinh thai hoc
%   rules       : Cau truc chua nguong quy tac (tuy chon):
%                 - min_area (mac dinh 60 px)
%                 - min_elongation (mac dinh 2.0)
%                 - min_damping (mac dinh 1.25)
%                 - min_complexity (mac dinh 1.8)
%
% DAU RA:
%   candidates  : Struct array chua danh sach cac vet loang cung dac trung:
%                 Area, Perimeter, Elongation, Complexity, Solidity,
%                 MeanIntensity, DampingRatio, BorderGradient, IsSuspectedOil
%   labeled_img : Ma tran danh nhan Connected Components

    if nargin < 3
        rules = struct();
    end
    if ~isfield(rules, 'min_area'), rules.min_area = 60; end
    if ~isfield(rules, 'min_elongation'), rules.min_elongation = 2.0; end
    if ~isfield(rules, 'min_damping'), rules.min_damping = 1.25; end
    if ~isfield(rules, 'min_complexity'), rules.min_complexity = 1.8; end

    img_d = im2double(img);
    
    % Tinh gradient toan anh (Sobel) de danh gia do sac net cua bien
    [Gx, Gy] = imgradientxy(img_d, 'sobel');
    Gmag = sqrt(Gx.^2 + Gy.^2);

    % Trich xuat cac Connected Components
    cc = bwconncomp(bw_clean, 8);
    props = regionprops(cc, 'Area', 'Perimeter', 'MajorAxisLength', ...
                        'MinorAxisLength', 'BoundingBox', 'Centroid', ...
                        'Solidity', 'PixelIdxList');

    labeled_img = labelmatrix(cc);
    num_blobs = cc.NumObjects;
    candidates = repmat(struct('Area', 0, 'Perimeter', 0, 'Elongation', 0, ...
                               'Complexity', 0, 'Solidity', 0, 'MeanIntensity', 0, ...
                               'BgMean', 0, 'DampingRatio', 0, 'BorderGradient', 0, ...
                               'BoundingBox', [0 0 0 0], 'Centroid', [0 0], ...
                               'IsSuspectedOil', false), num_blobs, 1);

    se_annulus = strel('disk', 6);

    for i = 1:num_blobs
        p = props(i);
        candidates(i).Area = p.Area;
        candidates(i).Perimeter = p.Perimeter;
        candidates(i).BoundingBox = p.BoundingBox;
        candidates(i).Centroid = p.Centroid;
        candidates(i).Solidity = p.Solidity;

        % 1. Do thuon dai (Elongation = Truc chinh / Truc phu)
        if p.MinorAxisLength > 0
            candidates(i).Elongation = p.MajorAxisLength / p.MinorAxisLength;
        else
            candidates(i).Elongation = 1.0;
        end

        % 2. Do phuc tap bien (Boundary Complexity / Circularity)
        if p.Area > 0
            candidates(i).Complexity = (p.Perimeter^2) / (4 * pi * p.Area);
        else
            candidates(i).Complexity = 1.0;
        end

        % 3. Cuong do trung binh cua vet
        slick_vals = img_d(p.PixelIdxList);
        candidates(i).MeanIntensity = mean(slick_vals);

        % 4. Tao vanh khan nen bien (Annulus background) bang Dilation
        blob_mask = false(size(img_d));
        blob_mask(p.PixelIdxList) = true;
        dilated_mask = imdilate(blob_mask, se_annulus);
        annulus_mask = dilated_mask & ~bw_clean; % Chi lay nen bien xung quanh

        if any(annulus_mask(:))
            bg_mean = mean(img_d(annulus_mask));
        else
            bg_mean = mean(img_d(:));
        end
        candidates(i).BgMean = bg_mean;

        % Ti so suy giam tan xa nguoc (Damping Ratio = nen / vet)
        candidates(i).DampingRatio = bg_mean / (candidates(i).MeanIntensity + eps);

        % 5. Gradient trung binh doc theo bien vet
        blob_perimeter = bwperim(blob_mask);
        if any(blob_perimeter(:))
            candidates(i).BorderGradient = mean(Gmag(blob_perimeter));
        else
            candidates(i).BorderGradient = 0;
        end

        % Quy tac phat hien Heuristic (CV-based decision rule):
        % Vệt dầu: Diện tích đủ lớn, suy giảm tương phản rõ rệt,
        % và có dạng thon dài (vệt tàu) HOẶC biên uốn lượn phức tạp (sóng vò nát)
        is_large = (candidates(i).Area >= rules.min_area);
        is_dark = (candidates(i).DampingRatio >= rules.min_damping);
        is_slick_shape = (candidates(i).Elongation >= rules.min_elongation) || ...
                         (candidates(i).Complexity >= rules.min_complexity);

        candidates(i).IsSuspectedOil = (is_large && is_dark && is_slick_shape);
    end
end
