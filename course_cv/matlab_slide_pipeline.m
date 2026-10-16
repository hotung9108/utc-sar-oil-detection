%% ==============================================================================
% CHƯƠNG TRÌNH PHÁT HIỆN VẾT DẦU TRÀN TRÊN ẢNH SAR (MATLAB)
% Chuẩn 100% giáo trình Xử lý ảnh - TS. Phan Thanh Toàn (ĐH Giao thông vận tải - UTC)
% Đề tài 18: Phát hiện vết dầu tràn trên biển từ ảnh SAR (Sentinel-1)
%
% CÁC CHƯƠNG ÁP DỤNG TRONG SLIDE:
% - Chương 3: Lọc trung vị medfilt2 khử nhiễu đốm speckle (Slide P104-106)
% - Chương 7: Phân vùng ngưỡng tối ưu Otsu graythresh & tính khả tách (Slide P48-55)
% - Chương 6: Hình thái học (imopen, imclose, imfill, bwareaopen)
%             và Trích xuất đường biên hình thái học beta(A) = A - (A - B) (Slide P16)
% - Chương 5: Gradient Sobel / Prewitt (imgradientxy) kiểm tra độ sắc nét biên (Slide P36-40)
% ==============================================================================

function matlab_slide_pipeline(input_folder, output_folder)
    if nargin < 1
        input_folder = '../data/sample';
    end
    if nargin < 2
        output_folder = '../outputs_slide_matlab';
    end

    fprintf('======================================================================\n');
    fprintf('CHƯƠNG TRÌNH COMPUTER VISION SAR (MATLAB - CHUẨN GIÁO TRÌNH UTC)\n');
    fprintf('Giảng viên: TS. Phan Thanh Toàn\n');
    fprintf('Thư mục đầu vào:  %s\n', input_folder);
    fprintf('Thư mục đầu ra:   %s\n', output_folder);
    fprintf('======================================================================\n');

    if ~exist(output_folder, 'dir')
        mkdir(output_folder);
    end

    % Lấy danh sách ảnh
    image_files = dir(fullfile(input_folder, '**', '*.jpg'));
    if isempty(image_files)
        image_files = dir(fullfile(input_folder, '**', '*.png'));
    end

    fprintf('Tìm thấy tổng cộng: %d ảnh.\n', length(image_files));

    total_detected = 0;
    tic;

    for i = 1:length(image_files)
        img_path = fullfile(image_files(i).folder, image_files(i).name);
        [~, fname, fext] = fileparts(img_path);

        % Xác định thư mục con tương ứng
        rel_folder = extractAfter(image_files(i).folder, input_folder);
        if isempty(rel_folder)
            target_out_dir = output_folder;
        else
            target_out_dir = fullfile(output_folder, rel_folder);
        end
        if ~exist(target_out_dir, 'dir')
            mkdir(target_out_dir);
        end

        % Đọc ảnh
        I_orig = imread(img_path);
        if size(I_orig, 3) == 3
            I_gray = rgb2gray(I_orig);
        else
            I_gray = I_orig;
        end

        % -----------------------------------------------------------------
        % BƯỚC 1: LỌC TRUNG VỊ KHỬ NHIỄU ĐỐM (CHƯƠNG 3 - Slide P104-106)
        % -----------------------------------------------------------------
        I_filtered = medfilt2(I_gray, [5 5]);

        % -----------------------------------------------------------------
        % BƯỚC 2: PHÂN NGƯỠNG TỐI ƯU OTSU (CHƯƠNG 7 - Slide P48-55)
        % -----------------------------------------------------------------
        [T_level, separability] = graythresh(I_filtered);
        
        % Vết dầu là vùng tối nên đảo nhị phân: I_filtered <= T_level * 255
        BW_dark = ~imbinarize(I_filtered, T_level);

        % -----------------------------------------------------------------
        % BƯỚC 3: HÌNH THÁI HỌC LÀM SẠCH VÀ LẤP LỖ (CHƯƠNG 6 - Slide P18, 20)
        % -----------------------------------------------------------------
        % Thành phần cấu trúc đĩa (Structuring Element B - Slide P7)
        se_open  = strel('disk', 2);
        se_close = strel('disk', 4);

        % Phép mở A o B loại bỏ nhiễu sóng nhỏ (Slide P18)
        BW_open = imopen(BW_dark, se_open);

        % Phép đóng A * B hàn gắn vết dầu nứt đoạn (Slide P20)
        BW_close = imclose(BW_open, se_close);

        % Lấp lỗ trống bên trong vệt dầu (Hole Filling)
        BW_filled = imfill(BW_close, 'holes');

        % Lọc vùng diện tích nhỏ (< 150 px)
        BW_area = bwareaopen(BW_filled, 150);

        % -----------------------------------------------------------------
        % BƯỚC 4: TÍNH TOÁN GRADIENT BIÊN (CHƯƠNG 5) & TRÍCH BIÊN (CHƯƠNG 6)
        % -----------------------------------------------------------------
        % Gradient Sobel theo Slide Chương 5 (trang 36-40)
        [Gx, Gy] = imgradientxy(double(I_filtered), 'sobel');
        G_mag = hypot(Gx, Gy);

        % Phân tích thành phần liên thông
        CC = bwconncomp(BW_area, 8);
        stats = regionprops(CC, 'Area', 'PixelIdxList');

        final_mask = false(size(I_gray));
        se_boundary = strel('disk', 1);

        for k = 1:CC.NumObjects
            if stats(k).Area >= 150 && stats(k).Area <= 120000
                single_mask = false(size(I_gray));
                single_mask(stats(k).PixelIdxList) = true;

                % Trích biên hình thái học beta(A) = A - (A - B) (Slide Chương 6 P16)
                eroded = imerode(single_mask, se_boundary);
                border_k = single_mask & ~eroded;

                % Vành đai nền lân cận bằng giãn nở
                se_annulus = strel('disk', 7);
                dilated = imdilate(single_mask, se_annulus);
                bg_annulus = dilated & ~single_mask;

                mean_blob = mean(double(I_filtered(single_mask)));
                mean_bg   = mean(double(I_filtered(bg_annulus)));
                contrast  = mean_bg - mean_blob;
                mean_grad = mean(G_mag(border_k));

                % Kiểm tra tiêu chí tương phản & độ dốc biên
                if contrast >= 12.0 && mean_grad >= 6.0
                    final_mask = final_mask | single_mask;
                end
            end
        end

        % -----------------------------------------------------------------
        % XUẤT ẢNH: VẼ ĐƯỜNG VIỀN MÀU ĐỎ ÔM SÁT VẾT DẦU (CHƯƠNG 6 P16)
        % -----------------------------------------------------------------
        % Tạo ảnh màu RGB 3 kênh từ ảnh gốc
        R = I_orig;
        G = I_orig;
        B = I_orig;
        if size(I_orig, 3) == 3
            R = I_orig(:,:,1);
            G = I_orig(:,:,2);
            B = I_orig(:,:,3);
        end

        if any(final_mask(:))
            % Trích biên toàn bộ vệt dầu beta(A) = A - (A - B)
            total_eroded = imerode(final_mask, se_boundary);
            total_border = final_mask & ~total_eroded;
            
            % Làm dày nét vẽ 2px cho rõ nét
            total_border = imdilate(total_border, strel('disk', 1));

            % Khử 2 pixel mép ngoài ảnh
            total_border(1:2, :) = false;
            total_border(end-1:end, :) = false;
            total_border(:, 1:2) = false;
            total_border(:, end-1:end) = false;

            % Đè màu ĐỎ (R=255, G=0, B=0) lên viền vệt dầu
            R(total_border) = 255;
            G(total_border) = 0;
            B(total_border) = 0;

            total_detected = total_detected + 1;
        end

        I_result = cat(3, R, G, B);
        out_filepath = fullfile(target_out_dir, [fname, fext]);
        imwrite(I_result, out_filepath);

        if mod(i, 20) == 0 || i == length(image_files)
            fprintf('  -> Đã xử lý %d/%d ảnh...\n', i, length(image_files));
        end
    end

    total_time = toc;
    fprintf('======================================================================\n');
    fprintf('HOÀN TẤT XỬ LÝ (MATLAB)!\n');
    fprintf('- Tổng số ảnh đã phân tích: %d\n', length(image_files));
    fprintf('- Số ảnh phát hiện có vết dầu: %d\n', total_detected);
    fprintf('- Thời gian thực thi: %.2f giây\n', total_time);
    fprintf('- Ảnh kết quả lưu tại: %s\n', output_folder);
    fprintf('======================================================================\n');
end
