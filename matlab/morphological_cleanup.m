function bw_clean = morphological_cleanup(bw_raw, min_area, close_radius)
% MORPHOLOGICAL_CLEANUP Tinh chinh mat na nhi phan bang hinh thai hoc toan hoc
%
% CU PHAP:
%   bw_clean = morphological_cleanup(bw_raw, min_area, close_radius)
%
% DAU VAO:
%   bw_raw       : Mat na nhi phan ban dau (logical)
%   min_area     : Dien tich toi thieu (pixels) de giu lai (mac dinh: 50)
%   close_radius : Ban kinh phan tu cau truc dia de dong vet nut (mac dinh: 3)
%
% DAU RA:
%   bw_clean     : Mat na sau khi khu nhieu, lap lo va lien ket cac mang vet dau

    if nargin < 2 || isempty(min_area)
        min_area = 50;
    end
    if nargin < 3 || isempty(close_radius)
        close_radius = 3;
    end

    % 1. Phep Opening nhe (3x3) de loai bo cac dom nhieu don le do song bien
    se_open = strel('disk', 1);
    bw_opened = imopen(bw_raw, se_open);

    % 2. Phep Closing de han gan cac doan vet dau bi dut quang boi nhieu dom
    se_close = strel('disk', close_radius);
    bw_closed = imclose(bw_opened, se_close);

    % 3. Lap day cac lo trong (Hole filling) ben trong vet dau
    bw_filled = imfill(bw_closed, 'holes');

    % 4. Loai bo cac vung co dien tich qua nho (area filtering)
    bw_clean = bwareaopen(bw_filled, min_area);

    % 5. Loai bo cac blob cham sat vao bien anh (anh huong boi vien artifact)
    bw_clean = imclearborder(bw_clean, 4);
    
    % Neu xoa bien lam mat het, quay ve bw_clean truoc khi xoa bien
    if ~any(bw_clean(:)) && any(bw_filled(:))
        bw_clean = bwareaopen(bw_filled, min_area);
    end
end
