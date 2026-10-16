%% MAIN_DETECTION_DEMO.M
% Demo quy trinh phat hien vet dau tran tu anh SAR Sentinel-1 bang Computer Vision thuan tuy
% De tai: De 18. Phat hien vet dau tran tren bien tu anh SAR (NASA #6) - UTC
% Ap dung giam sat bien ngoai khoi mien Trung Viet Nam

clear; clc; close all;

%% 1. KHOI TAO DUONG DAN VA CHON ANH KIEM THU
project_root = fileparts(pwd);
if ~exist(fullfile(pwd, 'lee_filter.m'), 'file')
    % Neu dang dung o root
    matlab_dir = fullfile(pwd, 'matlab');
    addpath(matlab_dir);
    data_sample_dir = fullfile(pwd, 'data', 'sample', 'Class_1');
else
    % Neu dang dung trong thu muc matlab/
    addpath(pwd);
    data_sample_dir = fullfile(project_root, 'data', 'sample', 'Class_1');
end

% Tim anh kiem thu trong data/sample/Class_1
img_files = dir(fullfile(data_sample_dir, '*.jpg'));
if isempty(img_files)
    % Thu tim trong data/Class_1/
    img_files = dir(fullfile(project_root, 'data', 'Class_1', '*.jpg'));
end

if isempty(img_files)
    error('Khong tim thay anh trong thu muc du lieu. Vui long kiem tra data/');
end

% Chon anh mau dau tien
test_img_path = fullfile(img_files(1).folder, img_files(1).name);
fprintf('>>> Dang xu ly anh: %s\n', img_files(1).name);
raw_img = imread(test_img_path);
if size(raw_img, 3) > 1
    raw_img = rgb2gray(raw_img);
end

%% 2. BUOC 1: LOC NHIEU DOM SAR (LEE FILTER) & TANG CUONG TUONG PHAN (CLAHE)
fprintf('1. Dang loc nhieu dom bang Lee Filter...\n');
filtered_img = lee_filter(raw_img, 5, 0.52);

fprintf('2. Dang tang cuong tuong phan voi CLAHE (adapthisteq)...\n');
enhanced_img = adapthisteq(filtered_img, 'ClipLimit', 0.02, 'Distribution', 'rayleigh');

%% 3. BUOC 2: PHAN NGUONG THICH NGHI TIM VUNG TOI (ADAPTIVE THRESHOLDING)
fprintf('3. Dang phan nguong thich nghi tach vung toi ung vien...\n');
param.window = 35;
param.k = 0.22;
bw_dark = adaptive_thresholding(enhanced_img, 'sauvola', param);

%% 4. BUOC 3: TINH CHINH HINH THAI HOC (MORPHOLOGICAL CLEANUP)
fprintf('4. Dang xu ly hinh thai hoc (opening, closing, hole fill, bwareaopen)...\n');
min_area = 50;      % Bo cac dom nhieu nho hon 50 pixels
close_radius = 3;   % Han gan vet dut quang
bw_clean = morphological_cleanup(bw_dark, min_area, close_radius);

%% 5. BUOC 4: TRICH XUAT DAC TRUNG & KHOANH VUNG VET DAU HEURISTIC
fprintf('5. Dang trich xuat dac trung va danh gia quy tac nhan dien...\n');
rules.min_area = 60;
rules.min_elongation = 1.8;
rules.min_damping = 1.20;
rules.min_complexity = 1.6;

[candidates, labeled_img] = extract_features(enhanced_img, bw_clean, rules);

% In bang ket qua dac trung ra Command Window
fprintf('\n================== KET QUA PHAN TICH CAC UNG VIEN ==================\n');
fprintf('%-5s %-8s %-12s %-12s %-10s %-12s\n', 'Blob', 'Area', 'Elongation', 'Complexity', 'Damping', 'Ket_Luan');
fprintf('--------------------------------------------------------------------\n');

detected_oil_count = 0;
for i = 1:length(candidates)
    c = candidates(i);
    status = 'Look-alike / Nen';
    if c.IsSuspectedOil
        status = 'SUSPECTED OIL';
        detected_oil_count = detected_oil_count + 1;
    end
    fprintf('#%-4d %-8d %-12.2f %-12.2f %-10.2f %-12s\n', ...
        i, c.Area, c.Elongation, c.Complexity, c.DampingRatio, status);
end
fprintf('--------------------------------------------------------------------\n');
fprintf('Tong so vet dau nghi van phat hien: %d / %d blobs.\n\n', detected_oil_count, length(candidates));

%% 6. TRUC QUAN HOA 4 BUOC XU LY
figure('Name', 'Ket Qua Phat Hien Vet Dau Tran Tu Anh SAR (CV thuan tuy)', ...
       'Position', [100, 100, 1100, 800], 'Color', 'w');

% Panel 1: Anh SAR goc
subplot(2, 2, 1);
imshow(raw_img);
title('1. Anh SAR Sentinel-1 Goc (400x400)', 'FontSize', 12, 'FontWeight', 'bold');

% Panel 2: Sau loc Lee & CLAHE
subplot(2, 2, 2);
imshow(enhanced_img);
title('2. Sau Loc Lee (5x5) & CLAHE Rayleigh', 'FontSize', 12, 'FontWeight', 'bold');

% Panel 3: Mat na phan nguong & Morphology
subplot(2, 2, 3);
imshow(bw_clean);
title(sprintf('3. Mat Na Nhi Phan (Sauvola + Morphology, N=%d)', length(candidates)), ...
      'FontSize', 12, 'FontWeight', 'bold');

% Panel 4: Khoanh vung vet dau phat hien tren anh goc
subplot(2, 2, 4);
imshow(raw_img);
hold on;
title(sprintf('4. Phat Hien: %d Vet Dau Nghi Van', detected_oil_count), ...
      'FontSize', 12, 'FontWeight', 'bold');

% Chi ve duy nhat duong vien do quanh vet dau nghi van
boundaries = bwboundaries(bw_clean);
for i = 1:length(candidates)
    c = candidates(i);
    if c.IsSuspectedOil && i <= length(boundaries)
        b = boundaries{i};
        plot(b(:,2), b(:,1), 'r-', 'LineWidth', 2);
    end
end
hold off;

fprintf('>>> Hoan tat xu ly va ve bieu do truc quan 4 buoc!\n');
