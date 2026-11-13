"""Editable Vietnamese report content; measurements are injected at build time.

One topic per section. The builder emits the same content to PDF, Word and LaTeX.
"""

import re


def paragraph(text):
    return {"type": "paragraph", "text": text}


def equation(label, text, latex):
    return {"type": "equation", "label": label, "text": text, "latex": latex}


def table(caption, rows, bold_cells=()):
    return {"type": "table", "caption": caption, "rows": rows, "bold_cells": list(bold_cells)}


def figure(caption, path):
    return {"type": "figure", "caption": caption, "path": path}


def algorithm(caption, lines):
    return {"type": "algorithm", "caption": caption, "text": lines}


def sections(data):
    P, E, T, F, A = paragraph, equation, table, figure, algorithm
    pages = []

    def section(ch, title, *items):
        pages.append({"chapter": ch, "title": title, "items": list(items)})

    section(
        1,
        "1.1. Bối cảnh, mục tiêu và phạm vi đã đăng ký",
        P(
            "Bài tập lớn được thực hiện theo tài liệu “ds btl xla VÀ HƯỚNG DẪN” của học phần Xử lý ảnh tại UTC [1]. Phạm vi đã được người dùng xác nhận đăng ký là kết hợp tăng cường, lọc ảnh và xử lý biên trên dữ liệu SAR. Đề tài 18 trong tài liệu liên quan NASA chỉ được dùng để định hướng lựa chọn dữ liệu, không kéo theo yêu cầu phân lớp bằng machine learning hoặc deep learning."
        ),
        P(
            "Ứng dụng minh họa là quan sát các vùng tối có thể liên quan đến dầu trên mặt biển. Trong giám sát vùng ven biển Việt Nam, việc làm rõ cấu trúc ảnh có thể hỗ trợ người phân tích xem xét vùng đáng chú ý. Tuy nhiên, vùng lặng gió, màng sinh học và các yếu tố quan sát khác cũng có thể tạo vùng tối. Hai tổng quan [2], [3] cho thấy cần phân biệt bước phát hiện dark spot với bước xác định bản chất của đối tượng."
        ),
        P(
            "Mục tiêu học thuật là hiểu, cài đặt và kiểm chứng phép biến đổi ảnh. Hệ thống không được mô tả như một công cụ xác nhận sự cố tràn dầu. Mọi diện tích trong báo cáo được tính bằng pixel hoặc phần trăm ảnh đã resize; không chuyển sang km² khi chưa có thông tin độ phân giải mặt đất. Dữ liệu JPEG trong dự án không được mặc nhiên xem là ảnh bức xạ SAR đã hiệu chuẩn."
        ),
        T(
            "Bảng 1.1. Phạm vi kết quả",
            [
                ["Thực hiện", "Không suy diễn từ kết quả"],
                ["Lọc, tăng cường, biên, vùng tối", "Không xác nhận thành phần hóa học là dầu"],
                [
                    "Đối chiếu tính toán với thư viện",
                    "Không gọi so khớp thư viện là accuracy nhận diện",
                ],
                ["Đánh giá theo nhãn lớp có sẵn", "Không báo IoU/Dice khi chưa có mask chuẩn"],
            ],
        ),
    )

    section(
        1,
        "1.2. Phát biểu bài toán và tiêu chí nghiệm thu",
        P(
            "Đầu vào là một ma trận ảnh xám 8-bit hữu hạn, không rỗng. Demo hỗ trợ tệp ảnh thông dụng, giải mã và đổi kích thước thành 400×400; kích thước này giữ thời gian tương tác và tham số diện tích nhất quán. Thuật toán NumPy được kiểm tra thêm trên ảnh nhỏ, ảnh hằng, ảnh có kích thước không chia hết cho lưới CLAHE và cấu trúc chạm mép."
        ),
        P(
            "Đầu ra gồm ảnh sau lọc, ảnh sau tăng tương phản, ảnh hiển thị sau làm nét, bản đồ biên, mask vùng tối khi dùng phân đoạn hình thái và các thống kê. Với Sobel, Canny hoặc LoG, bản đồ biên không được dùng như mask diện tích dầu. API pipeline trả mask=None trong các trường hợp này để tránh diễn giải sai ở giao diện."
        ),
        T(
            "Bảng 1.2. Mục tiêu đo được",
            [
                ["Mã", "Tiêu chí"],
                [
                    "M1",
                    "Lõi lọc, tăng cường, biên, hình thái và metrics không import thư viện xử lý ảnh đối chứng",
                ],
                [
                    "M2",
                    "Có ví dụ số và bảng so sánh tất cả thuật toán/chỉ số đang trình bày; ghi MSE và sai số lớn nhất",
                ],
                ["M3", "Demo Streamlit chạy ảnh mẫu và đổi phương pháp; tải PNG/JSON"],
                ["M4", "Một lệnh tái tạo bảng, ảnh, môi trường và phân tích ca lỗi"],
                [
                    "M5",
                    "Phân công TV1–TV5, báo cáo, slide và mẫu đánh giá chéo; không giả dữ liệu nhóm",
                ],
            ],
        ),
        P(
            "Không đặt một ngưỡng accuracy nhận diện dầu tùy ý sau khi đã nhìn kết quả. Khả năng phát hiện vùng tối được trình bày trung thực ở chương 4. Thời gian xử lý được đo trên môi trường cụ thể, không cam kết thời gian thực trên mọi máy. Ngưỡng số học dùng trong kiểm chứng được khai báo theo kiểu phép toán trước khi tổng hợp kết quả."
        ),
    )

    section(
        1,
        "1.3. Hướng tiếp cận và vị trí của hệ thống",
        T(
            "Bảng 1.3. Các phương pháp được chọn và đánh đổi",
            [
                ["Nguồn/phương pháp", "Vai trò", "Đánh đổi"],
                ["Lee [4]", "Khử đốm bằng thống kê cục bộ", "Phụ thuộc mô hình L và cửa sổ"],
                ["CLAHE [5]", "Tăng tương phản theo tile", "Có thể làm nổi kết cấu nền"],
                ["Canny [6]", "Làm mảnh và nối biên", "Biên mạnh không đồng nghĩa dầu"],
                ["Otsu [7]", "Tách nhóm mức xám", "Một ngưỡng khó xử lý nền phức tạp"],
                [
                    "Kuan [8], Frost [9]",
                    "Phương án lọc so sánh",
                    "Chi phí và cách tham số hóa khác nhau",
                ],
            ],
        ),
        P(
            "Theo các phép toán nền tảng trong [10], nhóm tổ chức bài toán thành các bước có thể kiểm chứng độc lập. Bộ lọc thay đổi phân bố nhiễu và độ sắc của chuyển tiếp; tăng cường thay đổi phân bố mức xám; biên và hình thái biến ảnh thành cấu trúc hình học. Việc chia nhỏ giúp tìm đúng bước gây lỗi thay vì chỉ nhìn đường viền cuối."
        ),
        P(
            "Điểm điều chỉnh của dự án là giữ ảnh sau lọc trước CLAHE làm tham chiếu cho phân đoạn và đo tương phản. Làm nét phục vụ quan sát, không đi ngược vào mask vùng tối. Các quy tắc chọn ảnh phân đoạn, giảm ngưỡng khi vùng tối lớn và lọc theo diện tích vẫn là heuristic; báo cáo không gán chúng cho một tiêu chuẩn NASA khi chưa có nguồn chứng minh."
        ),
        P(
            "OpenCV [11] và SciPy [12] được sử dụng trong phần đối chứng. Đối với phương pháp không có một API tương đương trực tiếp trong bộ thư viện đang dùng, báo cáo ghi rõ phép ghép các hàm nền tảng. Cách này kiểm tra tính toán của công thức đã chọn, nhưng không chứng minh toàn bộ mô hình là bản tái hiện độc lập của một công trình nghiên cứu."
        ),
    )

    section(
        2,
        "2.1. Biến đổi điểm, histogram và CLAHE",
        P(
            "Ảnh được xem là hàm rời rạc I(y,x). Histogram h(k) đếm số pixel ở mức k và p(k)=h(k)/N là phân bố mức xám. Biến đổi log kéo giãn các mức thấp, trong khi HE ánh xạ theo phân bố tích lũy. Bản cài HE dùng CDF-min để đối chiếu OpenCV, không nhầm với ví dụ giáo trình dùng trực tiếp CDF chưa trừ giá trị đầu."
        ),
        E(
            "2.1",
            "s = round[255 ln(1+r) / ln(1+r_max)]",
            r"s=\operatorname{round}\left(255\frac{\ln(1+r)}{\ln(1+r_{\max})}\right)",
        ),
        E(
            "2.2",
            "HE(k) = round[255 (CDF(k) − CDF_min)/(N − CDF_min)]",
            r"HE(k)=\operatorname{round}\left(255\frac{CDF(k)-CDF_{\min}}{N-CDF_{\min}}\right)",
        ),
        P(
            "Ảnh hằng được giữ nguyên trong HE vì mẫu số CDF-min bằng 0 và không tồn tại thông tin tương phản để phân bố lại. CLAHE [5] chia ảnh thành các tile cùng kích thước sau đệm phản xạ. Mỗi histogram được cắt ở max(floor(clip·tile_area/256),1), rồi phân phối phần dư bằng thương nguyên và phần dư rải cách đều. LUT được nội suy song tuyến từ các tile lân cận."
        ),
        P(
            "Lưới là số tile, không phải kích thước cửa sổ theo pixel. Clip lớn cho phép histogram tập trung hơn và thường tăng tác động tương phản; ảnh gốc không thay đổi ý nghĩa vật lý vì được ánh xạ lại. Nội suy giảm đường ráp tile nhưng không bảo đảm loại bỏ kết cấu nhiễu. Kiểm chứng phải thống nhất thứ tự grid (hàng,cột) của code và (cột,hàng) của OpenCV."
        ),
    )

    section(
        2,
        "2.2. Lọc không gian và lọc thích nghi SAR",
        P(
            "Box lấy trung bình cửa sổ; Gaussian dùng trọng số giảm theo khoảng cách; Median lấy trung vị nên xử lý nhiễu xung khác với phép trung bình. Bilateral nhân trọng số không gian với trọng số chênh mức xám. Bản Bilateral của dự án dùng footprint vuông, trong khi OpenCV có footprint khác; vì thế phép đối chiếu được ghi là so sánh biến thể."
        ),
        E(
            "2.3",
            "w(p,q) = exp[−||p−q||²/(2σ_s²)] exp[−(I_p−I_q)²/(2σ_r²)]",
            r"w(p,q)=e^{-\|p-q\|^2/(2\sigma_s^2)}e^{-(I_p-I_q)^2/(2\sigma_r^2)}",
        ),
        P(
            "Để dẫn xuất trực giác Lee, xét ước lượng tuyến tính cục bộ R̂=μ+K(I−μ). Trong mô hình nhiễu nhân với số look L, phương sai nhiễu được xấp xỉ bằng μ²/L. Phần phương sai có thể quy cho tín hiệu được ước lượng là max(σ²−μ²/L,0). Chia cho phương sai quan sát cho hệ số K ở công thức 2.4. Đây là xấp xỉ thống kê được cài, không bảo đảm đúng cho mọi JPEG SAR."
        ),
        E(
            "2.4",
            "K = clip(1 − μ²/(Lσ²),0,1); R̂ = μ + K(I−μ)",
            r"K=\operatorname{clip}\left(1-\frac{\mu^2}{L\sigma^2},0,1\right),\quad \hat R=\mu+K(I-\mu)",
        ),
        P(
            "Kuan dùng C_i²=σ²/μ², C_u²=1/L và trọng số clip((1−C_u²/C_i²)/(1+C_u²),0,1). Bản được đặt tên Frost trong dự án dùng trọng số exp(−a·CV·distance); đây là biến thể trọng số đã nêu rõ, không tuyên bố tương đương mọi công thức Frost trong tài liệu. Cửa sổ càng rộng càng có nguy cơ trộn nền và vệt; L càng lớn làm mô hình giả định nhiễu tương đối nhỏ hơn."
        ),
    )

    section(
        2,
        "2.3. Lọc đồng hình và làm nét",
        P(
            "Lọc đồng hình chuyển sang miền log, biến đổi Fourier, nhân bộ lọc rồi biến đổi ngược và lấy exp. NumPy FFT được dùng như phép toán số; bộ lọc miền tần số được tự xây dựng theo công thức. Đây không phải bài tự cài DFT/FFT cơ số hai. Phạm vi đề kết hợp không được tự mở rộng sang yêu cầu riêng của đề Fourier nếu chưa đăng ký."
        ),
        E(
            "2.5",
            "H(u,v) = (γ_H−γ_L)[1−exp(−cD²/D₀²)] + γ_L",
            r"H(u,v)=(\gamma_H-\gamma_L)(1-e^{-cD^2/D_0^2})+\gamma_L",
        ),
        E(
            "2.6",
            "f_sharp = f + k(f − blur(f)); f_lap = f − α∇²f",
            r"f_{sharp}=f+k(f-\operatorname{blur}(f)),\quad f_{lap}=f-\alpha\nabla^2 f",
        ),
        P(
            "D₀ điều khiển khoảng chuyển tiếp; γ_L và γ_H điều chỉnh các dải thấp/cao. Bản cài chuẩn hóa kết quả về 0–255, nên độ sáng trung bình có thể thay đổi mạnh. Unsharp và high-boost bổ sung phần chi tiết cao tần; khi k lớn, cả biên thật và nhiễu còn lại đều được tăng cường. Laplacian có thể tạo viền vượt mức quanh chuyển tiếp sáng–tối."
        ),
        P(
            "Pipeline vì thế tách ảnh hiển thị sau làm nét khỏi ảnh đưa vào phân đoạn. Đây là một quyết định dữ liệu: mask được tính trước làm nét và phải không đổi khi chỉ sửa hệ số sharpening. Kiểm thử hồi quy thực hiện đúng phép thay đổi đó. Các kết quả làm nét được đối chiếu bằng phép ghép blur hoặc Laplacian thư viện với cùng công thức đại số, cùng cách làm tròn và clip uint8."
        ),
    )

    section(
        2,
        "2.4. Gradient, LoG và Canny",
        P(
            "Sobel và Prewitt xấp xỉ đạo hàm theo hai trục; Roberts dùng chênh lệch chéo 2×2. Độ lớn gradient phản ánh mức thay đổi cường độ, không xác định chất liệu của đối tượng. Các thành phần Gx, Gy được giữ ở float64. Chỉ ảnh hiển thị độ lớn mới được làm tròn và giới hạn về 8-bit."
        ),
        E(
            "2.7",
            "G = √(Gx²+Gy²); θ = atan2(Gy,Gx)",
            r"G=\sqrt{G_x^2+G_y^2},\quad \theta=\operatorname{atan2}(G_y,G_x)",
        ),
        P(
            "LoG sử dụng kernel lấy mẫu, trừ trung bình để tổng trọng số gần 0, sau đó dò đổi dấu giữa các cặp lân cận đối diện. Sai số triệt tiêu số học rất nhỏ được đặt bằng 0 trước khi xét dấu; nếu không, vùng bằng phẳng có thể tạo dấu âm/dương do làm tròn. Ngưỡng chênh lệch của cặp phải được giữ giống nhau trong code và đối chứng."
        ),
        P(
            "Canny [6] gồm Gaussian, gradient, triệt tiêu không cực đại, ngưỡng kép và hysteresis. NMS so độ lớn theo hướng gradient; tọa độ y của ảnh tăng xuống dưới nên các cặp chéo phải được chọn nhất quán. Pixel yếu chỉ được giữ khi nối 8-láng giềng đến pixel mạnh. Kết quả của NMS lượng tử bốn hướng có thể khác OpenCV ở cách xử lý bằng nhau và mép ảnh; số liệu so sánh được giữ, không ép kết luận bằng 0."
        ),
        T(
            "Bảng 2.1. Những điểm cần kiểm tra ở bộ dò biên",
            [
                ["Điều kiện", "Hệ quả mong đợi"],
                ["Ảnh hằng, ngưỡng bằng 0", "Không tạo toàn ảnh thành biên"],
                ["Gradient lớn hơn 255", "NMS vẫn dùng float, không bão hòa"],
                ["Biên chéo", "Cặp lân cận đúng hướng theo hệ tọa độ ảnh"],
            ],
        ),
    )

    section(
        2,
        "2.5. Otsu, hình thái và tương phản vùng/nền",
        P(
            "Otsu [7] chọn t làm cực đại phương sai giữa hai lớp I≤t và I>t. Với histogram nhiều đỉnh hoặc nền có cấu trúc, hai lớp mức xám không nhất thiết trùng với dầu và biển. Hệ số η đo khả năng tách histogram; η cao không phải chứng cứ rằng nhãn vật lý đúng."
        ),
        E(
            "2.8",
            "σ_B²(t)=ω₀ω₁(μ₀−μ₁)²; η=σ_B²(t*)/σ_T²",
            r"\sigma_B^2(t)=\omega_0\omega_1(\mu_0-\mu_1)^2,\quad \eta=\sigma_B^2(t^*)/\sigma_T^2",
        ),
        P(
            "Opening là erosion rồi dilation; closing là dilation rồi erosion. Các phần tử cấu trúc được tạo bằng NumPy và được mô tả theo bán kính pixel. Closing có thể nối vệt đứt nhưng cũng gộp các đốm nền gần nhau. Gán nhãn 8-liên thông tạo các vùng để đo diện tích và tính tương phản với vòng nền lân cận."
        ),
        E(
            "2.9",
            "β(A)=A ∖ (A⊖B); C_R=(μ_nền−μ_vùng)/μ_nền",
            r"\beta(A)=A\setminus(A\ominus B),\quad C_R=\frac{\mu_{nen}-\mu_{vung}}{\mu_{nen}}",
        ),
        P(
            "C_R ở đây là tương phản, không phải 4πA/P² là độ tròn. Mọi vùng, kể cả vùng lớn hơn 1.200 pixel, phải đạt ngưỡng người dùng chọn. Không có vòng nền thì không đo được tương phản và vùng không được giữ. Biên β(A) bao gồm mép ngoài và mép lỗ trong mask; nhiều vòng đỏ nhỏ không nhất thiết là nhiều vùng dầu riêng biệt."
        ),
    )

    section(
        2,
        "2.6. Chỉ số định lượng và ví dụ số",
        T(
            "Bảng 2.2. Chỉ số và giới hạn diễn giải",
            [
                ["Chỉ số", "Công thức", "Giới hạn"],
                [
                    "ENL",
                    "μ²/σ² trên ROI",
                    "ROI cố định chưa chắc đồng nhất; 999 là sentinel khi σ²≈0",
                ],
                [
                    "SSI",
                    "(std_f/mean_f)/(std_o/mean_o)",
                    "Độ biến thiên toàn ảnh, không riêng nhiễu",
                ],
                ["RMS", "std(I)", "Tăng cả tương phản nền lẫn vệt"],
                ["Entropy", "−Σp log₂p", "Không phải chất lượng phân đoạn"],
                ["AMBE", "|mean_f−mean_o|", "Độ lệch sáng, không đo đúng biên"],
                ["EPI", "Σ|∇²f|/Σ|∇²o|", "Cả nhiễu và biên cùng ảnh hưởng"],
            ],
        ),
        P(
            "Các chỉ số được dùng để mô tả đánh đổi, không cộng thành một điểm chất lượng tùy ý. Ví dụ ENL rất lớn có thể do ROI gần hằng sau lọc, nhưng việc làm phẳng đó cũng có thể xóa chi tiết. Khi phương sai ROI bằng 0, code dùng giá trị quy ước 999; không diễn giải 999 là số look vật lý đo được. So sánh trên cùng ảnh và ROI là điều kiện tối thiểu."
        ),
        T("Bảng 2.3. Ví dụ tính tay được chạy trên hàm thật", data["hand_table"]),
        P(
            "Ví dụ HE dùng ma trận 4×4 gồm bốn mức 0,1,2,3, mỗi mức bốn lần. CDF là 4,8,12,16; trừ CDF_min=4 và chia 12 cho LUT 0,85,170,255. Ví dụ Lee dùng nền 100, tâm 200, cửa sổ 3×3: tổng 1.000, trung bình 111,111; phương sai 80000/81 nhỏ hơn μ²/4 nên K=0 và kết quả làm tròn là 111. Hai ví dụ này đã kiểm chứng bằng NumPy; mã và số đo đầy đủ ở phụ lục."
        ),
    )

    section(
        2,
        "2.7. Công thức các phép toán nền tảng",
        P(
            "Bổ sung công thức cho các toán tử của [10]. Với cửa sổ Ω có k² phần tử, kernel Gaussian được chuẩn hóa có tổng bằng 1. σ lớn làm trọng số trải rộng hơn; Box là trường hợp trọng số đều. Median là thống kê thứ tự, không phải tích chập tuyến tính."
        ),
        E(
            "2.10",
            "g(i)=exp(−i²/(2σ²))/Σ_j exp(−j²/(2σ²)); G(i,j)=g(i)g(j)",
            r"g(i)=\frac{e^{-i^2/(2\sigma^2)}}{\sum_j e^{-j^2/(2\sigma^2)}},\quad G(i,j)=g(i)g(j)",
        ),
        E(
            "2.11",
            "Box(p)=Σ_{q∈Ωp} I(q)/k²; Median(p)=median{I(q):q∈Ωp}",
            r"Box(p)=\frac{1}{k^2}\sum_{q\in\Omega_p}I(q),\quad Median(p)=\operatorname{median}_{q\in\Omega_p}I(q)",
        ),
        P(
            "Đặt p_ij là mẫu ở hàng i, cột j trong cửa sổ 3×3. Hai thành phần Sobel dùng hệ số dưới đây; Prewitt thay hệ số 2 bằng 1 ở cả hai công thức. Hướng y dương xuống dưới. Roberts dùng cửa sổ 2×2 và tính độ lớn theo công thức 2.7."
        ),
        E(
            "2.12",
            "Gx=(p02+2p12+p22)−(p00+2p10+p20)",
            r"G_x=(p_{02}+2p_{12}+p_{22})-(p_{00}+2p_{10}+p_{20})",
        ),
        E(
            "2.13",
            "Gy=(p20+2p21+p22)−(p00+2p01+p02)",
            r"G_y=(p_{20}+2p_{21}+p_{22})-(p_{00}+2p_{01}+p_{02})",
        ),
        E("2.14", "Roberts: Gx=p11−p00; Gy=p10−p01", r"G_x=p_{11}-p_{00},\quad G_y=p_{10}-p_{01}"),
        P(
            "Với ảnh nhị phân A và tập vị trí B của kernel, erosion lấy AND, dilation lấy OR. Opening ghép erosion rồi dilation; closing ghép theo chiều ngược lại. Phần tử đĩa bán kính r gồm các offset i²+j²≤r²; r tăng loại hoặc nối các cấu trúc lớn hơn."
        ),
        E(
            "2.15",
            "(A⊖B)(p)=AND_{b∈B}A(p+b); (A⊕B)(p)=OR_{b∈B}A(p−b)",
            r"(A\ominus B)(p)=\bigwedge_{b\in B}A(p+b),\quad (A\oplus B)(p)=\bigvee_{b\in B}A(p-b)",
        ),
    )

    section(
        3,
        "3.1. Kiến trúc, dữ liệu và trách nhiệm TV1–TV5",
        P(
            "Kiến trúc tách phần giao diện khỏi hàm xử lý. Streamlit giải mã ảnh, nhận tham số và hiển thị; process_image nhận ma trận và PipelineConfig bất biến rồi trả kết quả. Không import framework web vào thuật toán lõi. Các wrapper ở src/ giữ tương thích với đường dẫn cũ, nhưng mỗi thuật toán chỉ có một bản triển khai trong thư mục của vai trò phụ trách."
        ),
        T(
            "Bảng 3.1. Phân công module",
            [
                ["Vai trò", "Module chính", "Trách nhiệm"],
                ["TV1", "src/tv1, streamlit_app.py", "Pipeline, validation, giao diện và tích hợp"],
                ["TV2", "src/tv2", "Ví dụ số, registry đối chiếu và xuất bảng"],
                ["TV3", "src/tv3", "Lọc, log/HE/CLAHE, đồng hình"],
                ["TV4", "src/tv4", "Làm nét, biên, Otsu/hình thái, liên thông"],
                ["TV5", "src/tv5, reproduce.py", "Chỉ số, dữ liệu, thực nghiệm, tái lập"],
            ],
        ),
        F("Hình 3.1. Luồng dữ liệu của pipeline và nhánh ảnh tham chiếu.", "pipeline.png"),
        P(
            "Hình 3.1 cho thấy nhánh trước CLAHE được giữ riêng. Làm nét không thay đổi đầu vào phân đoạn. Giao diện hiển thị rõ kết quả nào là ảnh quan sát, bản đồ biên hoặc mask ứng viên; không biến số pixel biên thành diện tích vùng. Phân công trên là trách nhiệm từ phiên bản hiện tại, không xác nhận tác giả lịch sử."
        ),
    )

    section(
        3,
        "3.2. Cài đặt lọc không gian và bộ lọc SAR",
        A(
            "Thuật toán 3.1. Các bộ lọc cục bộ (đầu vào I, cửa sổ lẻ k; đầu ra J)",
            "1. Kiểm tra ảnh hữu hạn, k lẻ; chuyển float trước phép trừ/nhân.\n2. Đệm reflect-101; tính moment bằng tổng tích lũy cho Box, Lee, Kuan.\n3. Box: J ← mean cửa sổ. Gaussian: hai lượt kernel 1D chuẩn hóa.\n4. Median: J ← trung vị cửa sổ.\n5. Bilateral: trọng số ← Gauss(khoảng cách) × Gauss(chênh mức xám).\n6. Lee: tính K; Kuan: tính W từ Ci², Cu²; nội suy giữa mean và pixel.\n7. Frost biến thể: trọng số exp(−a·CV·distance), chuẩn hóa tổng.\n8. Round, clip 0..255 và chuyển uint8.",
        ),
        P(
            "Tổng tích lũy tránh lặp lại phép cộng cho mọi cửa sổ. Gaussian được tách theo hai chiều vì kernel là tích của hai kernel 1D. Median và Bilateral dùng sliding_window_view để biểu diễn cửa sổ; các phép nhân trung gian vẫn có thể cần O(Nk²) bộ nhớ, dù view tự nó không sao chép dữ liệu. Demo giới hạn k đến 9 để tránh chi phí không kiểm soát."
        ),
        T(
            "Bảng 3.2. Chi phí nhóm lọc với N=H×W",
            [
                ["Phương pháp", "Thời gian", "Bộ nhớ bổ sung"],
                ["Box/Lee/Kuan", "O(N)", "O(N)"],
                ["Gaussian tách", "O(Nk)", "O(N)"],
                ["Median", "Phụ thuộc chọn trung vị từng cửa sổ", "Có thể O(Nk²)"],
                ["Bilateral/Frost biến thể", "O(Nk²)", "O(Nk²) trung gian"],
            ],
        ),
        P(
            "Code yêu cầu sigma và số look dương; cửa sổ phải lẻ. Trong đối chiếu, quy tắc biên của thư viện được đặt tương ứng. Khác biệt ở vùng mép do dùng reflect thay vì nearest không được bỏ qua bằng cách chỉ cắt vùng giữa và tuyên bố khớp toàn ảnh."
        ),
    )

    section(
        3,
        "3.3. Cài đặt biến đổi điểm, CLAHE và đồng hình",
        A(
            "Thuật toán 3.2. Log, HE và CLAHE (đầu vào I và tham số; đầu ra J)",
            "1. Log: tạo LUT log1p cho 256 mức theo r_max, tra LUT cho từng pixel.\n2. HE: đếm histogram; cộng dồn CDF; xử lý riêng ảnh hằng.\n3. CLAHE: đệm để kích thước chia hết cho lưới; tạo histogram mỗi tile.\n4. Cắt histogram; chia lượng dư thành thương nguyên và phần dư.\n5. Tạo LUT uint8 từ CDF với cùng quy tắc làm tròn.\n6. Tính trọng số giữa tâm tile; nội suy bốn LUT cho từng pixel.\n7. Trả ảnh kích thước gốc, không trả phần đệm.",
        ),
        A(
            "Thuật toán 3.3. Lọc đồng hình (đầu vào I, γL, γH, c, D₀; đầu ra J)",
            "1. L ← log(1+I).\n2. F ← FFT2(L); dịch gốc tần số về tâm.\n3. Tạo H(u,v) từ khoảng cách tới tâm và các tham số.\n4. Z ← phần thực của IFFT2(F×H) sau dịch ngược.\n5. J ← exp(Z)−1; chuẩn hóa min/max về 0..255; xử lý ảnh hằng.",
        ),
        P(
            "Log và HE cần O(N+256) thời gian, bảng ánh xạ nhỏ. CLAHE cần O(N+256T) với T là số tile và thêm O(256T+N) bộ nhớ cho LUT, tọa độ và ảnh nội suy. Đồng hình dùng FFT có chi phí xấp xỉ O(N log N), bộ nhớ O(N) số phức. NumPy FFT được coi là phép toán số nền tảng; thuật toán lọc và ghép các bước do nhóm cài."
        ),
        P(
            "Lưới 1×1 và ảnh không chia hết cho lưới là hai ca dễ gây chia cho 0 hoặc sai nội suy. Kiểm thử so trực tiếp với cv2.createCLAHE cả các ca đó. Không dùng kết quả CLAHE như bằng chứng rằng tín hiệu tối mới xuất hiện là đối tượng mới trong cảnh."
        ),
    )

    section(
        3,
        "3.4. Cài đặt làm nét và các toán tử biên",
        A(
            "Thuật toán 3.4. Làm nét và gradient (đầu vào I; đầu ra ảnh làm nét/biên)",
            "1. Unsharp/high-boost: blur I; tính mask=I−blur; J=I+k·mask.\n2. Laplacian sharpen: tính tổng bốn láng giềng−4I; J=I−α·L.\n3. Roberts: tính hai chênh lệch chéo trên cửa sổ 2×2.\n4. Prewitt/Sobel: tích chập tương quan với hai kernel đạo hàm.\n5. G ← hypot(Gx,Gy), θ ← atan2(Gy,Gx).\n6. Sobel enhancement: cộng 0,5G vào I để quan sát.\n7. Chỉ round/clip ảnh hiển thị; giữ Gx,Gy float để xử lý tiếp.",
        ),
        A(
            "Thuật toán 3.5. LoG và zero crossing",
            "1. Lấy bán kính ceil(3σ); tạo kernel LoG rồi trừ mean kernel.\n2. Tương quan ảnh đã đệm reflect với kernel.\n3. Đặt đáp ứng |L|<10⁻⁹ bằng 0 để bỏ đổi dấu do triệt tiêu số học.\n4. Xét bốn cặp đối diện; giữ khi tích âm và chênh lệch vượt ngưỡng.\n5. Trả bản đồ nhị phân 0/255.",
        ),
        P(
            "Đạo hàm kernel cố định có O(N) thời gian và O(N) bộ nhớ. LoG tổng quát có O(Nk²), với k phụ thuộc sigma. Khi so với filter2D, cần chỉ rõ anchor của kernel Roberts 2×2; nếu để anchor khác nhau, biên có thể lệch một pixel dù công thức kernel giống nhau. Đầu ra biên bị cắt về 255 chỉ là biểu diễn hiển thị, không thay cho độ lớn gradient dùng bên trong Canny."
        ),
    )

    section(
        3,
        "3.5. Cài đặt Canny và kiểm soát sai khác",
        A(
            "Thuật toán 3.6. Canny tự cài (I, low, high, σ → biên nhị phân)",
            "1. Nếu thiếu ngưỡng: lấy ngưỡng từ median ảnh; kiểm tra 0≤low≤high.\n2. Làm mịn Gaussian 5×5; tính Sobel float và góc hướng.\n3. Lượng tử góc thành 0°,45°,90°,135°.\n4. NMS: giữ pixel không nhỏ hơn hai láng giềng theo đúng hướng.\n5. Mạnh: nms>0 và nms≥high; yếu: nms>0 và low≤nms<high.\n6. Đưa pixel mạnh vào hàng đợi.\n7. Duyệt BFS, nối pixel yếu 8-láng giềng chưa thăm.\n8. Trả các pixel mạnh hoặc yếu đã nối thành ảnh 0/255.",
        ),
        P(
            "Hysteresis duyệt mỗi pixel tối đa một lần, nên thời gian O(N) sau bước gradient và bộ nhớ O(N) cho ảnh trạng thái/hàng đợi. NMS được vector hóa bằng các lát ảnh đệm. Bản cũ đưa độ lớn đã clip uint8 vào NMS; điều này làm các gradient lớn bão hòa bằng nhau và có thể giữ những vị trí không phải cực đại. Phiên bản hiện tại dùng hypot(Gx,Gy) float."
        ),
        P(
            "Đối chứng OpenCV dùng ảnh đã được làm mịn giống nhau, bật L2gradient và cùng cặp ngưỡng. Tuy nhiên, quy tắc so sánh bằng nhau, lượng tử góc, cách xử lý mép của hai phiên bản không được giả định tương đương. Bảng xuất vì vậy giữ MSE, sai số lớn nhất, tỷ lệ pixel khớp và F1 biên chính xác vị trí để mô tả khác biệt; không tính các hàng này là PASS."
        ),
        P(
            "Một phép kiểm tra tối thiểu là ảnh hằng ở ngưỡng 0 phải trả ảnh biên rỗng. Quy tắc nms>0 tránh biến mọi pixel bằng 0 thành cạnh mạnh. Kiểm tra ngưỡng đảo ngược phải báo lỗi thay vì âm thầm tạo đầu ra không có nghĩa."
        ),
    )

    section(
        3,
        "3.6. Phân đoạn, liên thông và lọc ứng viên",
        A(
            "Thuật toán 3.7. Otsu, hình thái và phân đoạn vùng tối",
            "1. Otsu: histogram→xác suất→moment tích lũy→t cực đại phương sai giữa lớp.\n2. Chọn ảnh tăng cường hoặc reference theo tỷ lệ tối và η; ghi đây là heuristic.\n3. Nếu bật thích ứng và vùng tối >35%, giảm t theo chênh mean hai lớp.\n4. Mask ← I≤t; ảnh hằng cho mask rỗng.\n5. Erosion/dilation: AND/OR các lát dịch theo kernel; ghép thành opening/closing.\n6. Gán nhãn run-length union-find; lọc diện tích nhỏ.\n7. Lấy vòng nền dilation(mask)−mask; đo CR trên reference.\n8. Giữ mọi vùng đạt min_contrast; không có vòng nền thì bỏ.\n9. β(A) ← A−erosion(A); xuất vùng, diện tích, centroid, bounding box.",
        ),
        A(
            "Thuật toán 3.8. Gán nhãn 8-liên thông bằng các đoạn chạy",
            "1. Mỗi hàng: tìm các đoạn foreground liên tiếp [left,right].\n2. Tạo nhãn cho đoạn; nối với đoạn hàng trước có khoảng cách ≤1 pixel.\n3. Union-find hợp nhất nhãn tương đương, nén đường đi.\n4. Ánh xạ root thành nhãn liên tục; đếm diện tích bằng bincount.\n5. Chỉ dựng mask metadata cho vùng qua min_area; không thay ma trận nhãn.",
        ),
        P(
            "Ngưỡng Otsu được tính trong O(N+256), morphology O(N|B|). Gán nhãn theo đoạn có chi phí quét O(N) cộng hợp nhất các đoạn giao nhau; dựng mask cho K vùng được giữ có thể tốn O(KN) thời gian/bộ nhớ. Việc bỏ metadata cho vùng nhỏ giúp giảm chi phí thực tế, nhưng không được tuyên bố toàn pipeline O(N) khi K tăng. Đây là giới hạn cần nêu trong thiết kế."
        ),
    )

    section(
        3,
        "3.7. Kiểm chứng, xử lý lỗi và tích hợp Streamlit",
        P(
            "TV2 tổ chức registry gồm tên phép toán, hàm tự cài, hàm tham chiếu, mô tả quy tắc biên và giới hạn sai số. Ba nhóm được tách rõ: API trực tiếp; phép ghép primitive thư viện; biến thể mô tả. Các ca gồm ảnh đen, trắng, hằng, ramp, checkerboard, đường chéo, nhiễu có seed, xung đơn và 10 ảnh mẫu. Khi có FAIL ở nhóm có giới hạn, lệnh tái tạo kết quả dừng với mã lỗi."
        ),
        T(
            "Bảng 3.3. Quy tắc đối chứng",
            [
                ["Nhóm", "Ví dụ", "Diễn giải"],
                [
                    "Trực tiếp",
                    "HE, CLAHE, Sobel, Otsu, morphology",
                    "Cùng tham số, dtype và border",
                ],
                [
                    "Phép ghép",
                    "Lee/Kuan/Frost, homomorphic, sharpen",
                    "Kiểm tra công thức bằng primitive; không có API toàn thuật toán tương đương",
                ],
                ["Biến thể", "Bilateral, Canny", "Giữ sai khác và phân tích; không tính là PASS"],
            ],
        ),
        P(
            "Kiểm thử hồi quy còn kiểm tra phân hoạch liên thông so OpenCV, tham số không hợp lệ, endpoint của Otsu, ảnh hằng và bất biến mask khi đổi làm nét. Kiểm tra AST phát hiện import thư viện đối chứng trong các module lõi TV3/TV4/metrics TV5. Đây là hàng rào kiến trúc, không thay thế đọc mã hoặc chứng minh toán học."
        ),
        P(
            "Streamlit có các tab kết quả ảnh, chỉ số, bảng đối chứng và phân công. Người dùng chọn ảnh mẫu hoặc tải tệp, thay bộ lọc và tham số, tải PNG/JSON. AppTest kiểm tra luồng mặc định, đổi Canny và quay lại morphology, chọn ảnh 00013; đó là kiểm tra hành vi giao diện, không phải chứng nhận tương thích mọi trình duyệt. Những ảnh lỗi giải mã hoặc tham số không hợp lệ được thông báo thay vì trả kết quả giả."
        ),
    )

    section(
        4,
        "4.1. Môi trường và quy trình tái lập",
        T("Bảng 4.1. Môi trường của lần đo", data["environment_table"]),
        P(
            "Các số liệu trong chương này được đọc từ file CSV/JSON sau khi chạy reproduce.py, không gõ lại bằng tay. Manifest lưu commit nền, trạng thái working tree, SHA-256 của mã nguồn, seed và cấu hình pipeline. Khi working tree có sửa đổi, chỉ ghi commit là chưa đủ tái lập; hash nguồn giúp nhận diện đúng trạng thái đã đo."
        ),
        P(
            "Một lệnh chạy toàn bộ gồm ví dụ số, đối chiếu thư viện, thực nghiệm bộ mẫu và đánh giá hai lớp dataset. Tùy chọn --samples-only phục vụ phát triển nhưng phải được ghi rõ là phạm vi hạn chế. Thời gian từng ảnh được đo bằng đồng hồ đơn điệu; benchmark dataset dùng nhiều process nên số mili giây có ảnh hưởng tranh chấp tài nguyên, không được coi là độ trễ một yêu cầu độc lập trên máy nhàn rỗi."
        ),
        T(
            "Bảng 4.2. Lệnh và sản phẩm",
            [
                ["Lệnh", "Sản phẩm"],
                ["uv sync --locked --all-extras", "Môi trường Python theo uv.lock"],
                ["uv run python reproduce.py", "CSV, JSON, ảnh chẩn đoán trong results/"],
                [
                    "uv run --extra dev python -m pytest tests -q",
                    "Kiểm thử hồi quy và ranh giới thư viện",
                ],
                ["uv run streamlit run streamlit_app.py", "Demo tương tác tại localhost:8501"],
            ],
        ),
    )

    section(
        4,
        "4.2. Dữ liệu, nhãn và thiết kế thí nghiệm",
        T(
            "Bảng 4.3. Tập ảnh trong dự án",
            [
                ["Tập", "Số ảnh", "Vai trò"],
                ["Class_0", "3.695", "Đánh giá mức ảnh theo nhãn thư mục"],
                ["Class_1", "1.843", "Đánh giá mức ảnh theo nhãn thư mục"],
                ["Mẫu demo", "10", "5 dầu + 5 biển; chạy khảo sát và đối chứng"],
                ["Ảnh tổng hợp", "8", "Điều kiện biên và kiểm chứng số học"],
            ],
        ),
        P(
            "Nguồn [13] được xác định từ kaggle/metadata/dataset_metadata.xml: CSIRO, David Blondeau-Patissier, ngày 15/12/2022, DOI 10.25919/4v55-dn16. Metadata mô tả chip Sentinel-1 xám JPEG 400×400, nhãn 0 là biển sạch/look-alike và 1 có dầu. Tệp license.html đi kèm ghi CC BY-SA 4.0. Tên bộ dữ liệu có nhắc ML/DL nhưng việc dùng các ảnh cho thí nghiệm xử lý ảnh không yêu cầu huấn luyện mô hình."
        ),
        P(
            "Metadata công bố 5.630 ảnh (3.725 lớp 0, 1.905 lớp 1); repo có 5.538 ảnh khác nhau, thiếu 30 ảnh lớp 0 và 62 ảnh lớp 1. Không có checksum gốc để giải thích chênh lệch. Ảnh 400×400 lưu RGB, pipeline đọc xám. Ngoài hai lớp chính, kaggle/data/sample có 10 bản sao trùng byte: 5.548 đường dẫn nhưng 5.538 ảnh khác nhau, không đếm lặp khi đánh giá. Cả 10 ảnh demo cũng khớp byte với dataset; đây là tập con khảo sát, không phải tập đánh giá độc lập. Chưa có mask pixel hoặc định danh cảnh để kiểm tra chồng lấn giữa các chip."
        ),
        P(
            "Thí nghiệm A hỏi các bộ lọc thay đổi biến thiên và thành phần biên ra sao. Thí nghiệm B khảo sát CLAHE theo clip 1–5 và grid 4/8/16. Thí nghiệm C thêm nhiễu Gauss σ=10,20,30 cùng ảnh sạch để quan sát độ nhạy của bộ dò biên. Thí nghiệm D phân tích 00013 và toàn bộ năm ảnh biển mẫu. Thí nghiệm E đo sự có mặt của vùng ứng viên trên toàn bộ hai lớp."
        ),
        P(
            "Không có bước huấn luyện và không tối ưu tham số trên một tập test rồi gọi đó là đánh giá độc lập. Các thí nghiệm nhỏ dùng cùng 10 ảnh nên chỉ hỗ trợ nhận xét trên bộ mẫu, không đại diện mọi điều kiện SAR. Nhiễu Gauss được dùng như điều kiện bất lợi có thể tái lập, không thay thế mô hình speckle nhân của dữ liệu gốc."
        ),
    )

    section(
        4,
        "4.3. Kết quả đối chiếu: lọc và tăng cường",
        T("Bảng 4.4. Sai số lớn nhất và MSE trung bình trên 18 ca", data["comparison_a"]),
        P(
            "Bảng 4.4 phân biệt so trực tiếp API và đối chiếu bằng primitive. Các phép Box, Gaussian, Median đặt border tương ứng trước khi so. Gaussian cho phép sai khác một mức xám do thứ tự tính và làm tròn. HE cần riêng trường hợp hằng; CLAHE cần thống nhất giới hạn histogram, phần dư và nội suy. Sự giống nhau của các phép biến đổi này không chứng minh chúng cải thiện phân đoạn dầu."
        ),
        P(
            "Lee, Kuan và Frost biến thể được tính lại bằng moment/shift của SciPy và công thức đã trình bày. Đây là đối chứng cấu thành: nếu cả hai cùng dùng một giả định mô hình không phù hợp dữ liệu thì vẫn có thể khớp số học. Homomorphic dùng scipy.fft làm đối chứng chuỗi biến đổi. Bilateral dùng footprint khác nên được giữ ở trạng thái DESCRIPTIVE, không nâng ngưỡng tùy ý để đổi thành PASS."
        ),
        P(
            "Các giá trị trong bảng là tổng hợp của sai số từng ca; bảng per_case.csv giữ lại cả ảnh tổng hợp lẫn ảnh thật. Có thể truy ngược một sai khác tới ảnh, phương pháp và thông số. Báo cáo không chỉ chọn ảnh khớp đẹp để trình bày."
        ),
    )

    section(
        4,
        "4.4. Kết quả đối chiếu: biên, hình thái và metrics",
        T("Bảng 4.5. Đối chiếu nhóm biên và hình thái", data["comparison_b"]),
        T("Bảng 4.6. Đối chiếu sáu chỉ số định lượng", data["comparison_metrics"]),
        P(
            "Sobel/Prewitt so cả Gx và Gy ở float thay vì chỉ ảnh độ lớn bão hòa. Roberts đặt anchor rõ cho kernel 2×2. LoG đặt đáp ứng gần zero bằng 0 ở cả hai phép tính để tránh khác dấu do triệt tiêu số học. Otsu chọn ngưỡng đầu tiên đạt cực đại và kiểm tra I≤t; hai điều này tránh sai khác endpoint bị che bởi ảnh xám hiển thị."
        ),
        P(
            "Nhãn thành phần liên thông có thể khác thứ tự đánh số mà vẫn mô tả cùng phân hoạch. Bộ kiểm tra hồi quy xác nhận ánh xạ một-một giữa các vùng; bảng đo dùng diện tích vùng tại từng pixel như một đại lượng bất biến theo ID. Với erosion/dilation, giá trị ngoài ảnh được đặt rõ ràng để không so hai quy ước khác nhau."
        ),
        P(
            "Canny vẫn là đối chiếu biến thể, không có lời kết luận “khớp tuyệt đối”. Sáu metrics cũng có đối chứng riêng, nhưng chúng chỉ đo các đặc tính đã định nghĩa. MSE=0 của entropy hoặc EPI không có nghĩa đường biên đúng với thực tế. Tổng số PASS/DESCRIPTIVE trong toàn bộ registry được báo trên bảng tổng hợp kèm theo."
        ),
    )

    section(
        4,
        "4.5. So sánh bộ lọc: giảm biến thiên và mất chi tiết",
        T(
            "Bảng 4.7. SSI và EPI, trung bình ± độ lệch chuẩn trên 10 ảnh",
            data["filters_table"],
            data["filters_best"],
        ),
        P(
            "Bảng 4.7 in đậm SSI trung bình nhỏ nhất và EPI trung bình gần 1 nhất trong các bộ lọc (loại hàng ảnh gốc khỏi xếp hạng). Đó là hai tiêu chí riêng, không phải kết luận một bộ lọc tối ưu đồng thời cho khử nhiễu và phân đoạn."
        ),
        P(
            "SSI nhỏ hơn 1 cho thấy hệ số biến thiên toàn ảnh giảm so ảnh đầu vào. EPI gần 1 có nghĩa tổng đáp ứng Laplacian được giữ theo định nghĩa của chỉ số; nó không tách được biên thật khỏi nhiễu. Vì vậy không thể chọn bộ lọc tốt nhất chỉ từ một cột. Khi SSI giảm đồng thời EPI giảm nhiều, cần xem vùng chuyển tiếp trước khi kết luận lợi ích."
        ),
        P(
            "Kết quả bộ mẫu cho thấy Lee, Kuan và Box có các giá trị gần nhau trong cấu hình khảo sát. Điều này phù hợp với cơ chế khi trọng số thích nghi nhỏ: kết quả tiến gần trung bình cục bộ. Không có căn cứ nói Lee luôn bảo toàn biên tốt nhất. Median và Gaussian cho đánh đổi khác, tùy phân bố cường độ và kết cấu của từng ảnh."
        ),
        P(
            "ENL có thể tăng rất mạnh khi ROI góc trên trở nên gần hằng. Đây là dấu hiệu cần xem lại ROI, không phải bằng chứng số look vật lý tăng tương ứng. Bảng nguồn giữ ENL và thời gian để người đọc kiểm tra; thời gian đang đo toàn pipeline với cùng cấu hình phân đoạn, không phải chỉ thời gian riêng kernel lọc. Độ lệch chuẩn lớn cần được giữ lại, không chỉ báo trung bình."
        ),
    )

    section(
        4,
        "4.6. Khảo sát CLAHE và độ nhạy tham số",
        F(
            "Hình 4.1. AMBE và entropy trung bình theo clip và grid trên bộ mẫu.",
            "clahe_survey.png",
        ),
        P(
            "Hình 4.1 giúp trả lời tham số CLAHE thay đổi độ sáng và phân bố mức xám như thế nào. Mỗi điểm được tổng hợp từ cùng 10 ảnh. Clip và grid là hai yếu tố khác nhau: clip điều chỉnh cắt histogram, grid thay đổi kích thước vùng thống kê. Tăng entropy sau biến đổi không tự chứng minh vùng dầu được tách tốt hơn."
        ),
        T("Bảng 4.8. Một số cấu hình tại clip=2", data["clahe_table"]),
        P(
            "Mask cuối có thể ít thay đổi giữa hai cấu hình khi quy tắc chọn ảnh phân đoạn chuyển sang reference trước CLAHE. Vì thế cần báo cả ảnh tăng cường, tỷ lệ vùng ứng viên và ảnh thực sự được dùng để phân đoạn, không suy luận từ histogram hiển thị duy nhất. Không chọn thông số dựa vào vẻ đẹp của một ảnh rồi coi đó là tối ưu trên toàn dataset."
        ),
    )

    section(
        4,
        "4.7. Điều kiện bất lợi: nhiễu và mật độ biên",
        F("Hình 4.2. Mật độ biên theo mức nhiễu Gauss, trung bình trên bộ mẫu.", "edge_noise.png"),
        P(
            "Hình 4.2 cho biết mỗi phương pháp phản ứng thế nào khi đầu vào thay đổi. Mật độ biên là tỷ lệ pixel khác 0 trong bản đồ biên; không phải precision/recall vì chưa có nhãn biên chuẩn. Một phương pháp trả rất ít biên có thể đã bỏ sót đối tượng, còn nhiều biên có thể do nền hoặc nhiễu. Cần đối chiếu đồng thời ảnh và chỉ số."
        ),
        P(
            "Nhiễu được sinh bằng bộ sinh số giả ngẫu nhiên với seed 2026. Mỗi ảnh ở mỗi mức có một realization; phương pháp biên được chạy trên cùng ảnh nhiễu ở mức đó để so sánh công bằng. Độ lệch chuẩn hiện tại là giữa các ảnh, không phải khoảng tin cậy trên nhiều lần sinh nhiễu. Nếu cần kết luận ổn định theo nhiễu, cần lặp nhiều seed và tách hai nguồn biến thiên."
        ),
        P(
            "Việc tự thêm Gauss là điều kiện thử kiểm soát được, không nói ảnh SAR gốc chỉ có nhiễu Gauss. Kết quả được dùng để giải thích hạn chế của đạo hàm và ngưỡng hóa, đúng mục tiêu phân tích điều kiện bất lợi của học phần. Thời gian của Canny có thể tăng khi số điểm mạnh/yếu và độ liên thông tăng."
        ),
    )

    section(
        4,
        "4.8. Ca 00013 và các ảnh biển bị nhận nhầm",
        F(
            "Hình 4.3. Ảnh 00013: đầu vào, ảnh lọc, CLAHE và biên ứng viên.",
            "class_1_00013_clahe.png",
        ),
        F("Hình 4.4. Cùng ROI vệt chính trên ảnh gốc, ảnh lọc và ảnh tăng cường.", "roi_00013.png"),
        P(data["case_analysis"]),
        P(
            "CLAHE làm rõ cả dao động nền vốn khó thấy bằng mắt; Otsu lại tối ưu phân tách mức xám chứ không tối ưu nhãn dầu. Nếu mask trước đó nhận nền thành một vùng lớn có lỗ, phép lấy biên sẽ vẽ cả mép các lỗ. Đây là lý do nhiều vòng nhỏ trên hình không nhất thiết biểu thị nhiều đối tượng riêng. Lỗi gán nhãn chủ yếu phát sinh ở phân đoạn; bước lấy biên chỉ phản ánh mask đó."
        ),
        T("Bảng 4.9. Ảnh biển mẫu, cấu hình CLAHE mặc định", data["sea_table"]),
        F(
            "Hình 4.5. Ca báo nhầm sea_surface_01: vùng nền tối được giữ thành ứng viên.",
            "sea_surface_01_clahe.png",
        ),
        P(
            "Hình 4.5 là ví dụ thất bại ở ảnh được đặt trong nhóm biển. Hai vùng qua được các kiểm tra diện tích và tương phản vì các tiêu chí đó mô tả hình học/mức xám, không kiểm chứng bản chất dầu. Closing có thể nối nền tối thành vùng lớn. Vì vậy lọc diện tích đơn thuần không đủ sửa loại báo nhầm này; cần đánh giá quy tắc nền cục bộ và mask gán tay như đề xuất ở chương 5."
        ),
    )

    section(
        4,
        "4.9. Đánh giá cấp ảnh trên cả hai lớp",
        T("Bảng 4.10. Ma trận nhầm lẫn theo nhãn thư mục", data["confusion_table"]),
        T("Bảng 4.11. Chỉ số cấp ảnh và phạm vi diễn giải", data["class_metrics"]),
        P(
            "Quy tắc dự đoán dương tính là có ít nhất một vùng tối được giữ. Kết quả cho thấy nhiều ảnh Class_0 cũng có vùng thỏa diện tích và tương phản, nên độ đặc hiệu còn thấp. Đây là hạn chế của quy tắc dựa vào cường độ và hình thái, không thể sửa bằng cách đổi nhãn heuristic thành “sạch chuẩn”. Tỷ lệ phát hiện cao ở Class_1 phải được đọc cùng số báo nhầm."
        ),
        P(
            "Precision=TP/(TP+FP), Recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN), Specificity=TN/(TN+FP), Accuracy=(TP+TN)/N. Các chỉ số này dựa trên giả định ý nghĩa nhãn thư mục và ở cấp ảnh. Không có giá trị IoU/Dice hoặc sai số diện tích thực vì thiếu mask, độ phân giải mặt đất và xác minh vật lý."
        ),
        P(
            "Không loại các ca xấu khỏi mẫu đánh giá và không dùng tập này để khẳng định hiệu năng triển khai ngoài thực tế. Tất cả 5.538 đường dẫn được lưu ở bảng per_image; số ảnh mỗi lớp được kiểm tra trước tổng hợp. Bước tiếp theo có căn cứ là xây dựng nhãn vùng trên một tập đại diện và đối chiếu các quy tắc nền cục bộ, không phải tăng độ mạnh CLAHE để làm hình bắt mắt hơn."
        ),
    )

    section(
        5,
        "5.1. Đối chiếu mục tiêu và kết quả đạt được",
        T(
            "Bảng 5.1. Đối chiếu mục tiêu chương 1",
            [
                ["Mục tiêu", "Kết quả", "Giới hạn"],
                [
                    "M1: lõi NumPy",
                    "Đã triển khai và có kiểm tra ranh giới import",
                    "FFT dùng primitive NumPy; I/O/resize ở lớp tích hợp",
                ],
                [
                    "M2: kiểm chứng",
                    "5 ví dụ; 33 thuật toán/chỉ số ×18 ca",
                    "558 PASS, 36 DESCRIPTIVE; không phải mọi thuật toán có API độc lập",
                ],
                [
                    "M3: demo",
                    "Streamlit, AppTest và xuất PNG/JSON",
                    "Chưa là kiểm thử mọi trình duyệt/tệp ảnh",
                ],
                [
                    "M4: tái lập",
                    "Một lệnh, kết quả từng ảnh, manifest/hash",
                    "CSIRO có metadata/giấy phép; chưa rõ 92 ảnh chênh lệch",
                ],
                [
                    "M5: hồ sơ nhóm",
                    "Phân công, báo cáo, slide, mẫu đánh giá",
                    "Tên đã cung cấp; MSSV/chữ ký chờ điền; video đang hoãn",
                ],
            ],
        ),
        P(
            "Kết quả đạt được quan trọng nhất là pipeline có thể giải thích và kiểm chứng từng phần. Báo cáo đã sửa cách hiểu C_R, tách làm nét khỏi phân đoạn và loại lời kết luận tuyệt đối từ một heuristic. Các sửa lỗi số học như endpoint Otsu, ảnh hằng, gradient float và gần-zero LoG được gắn với kiểm thử tái hiện, thay vì chỉ mô tả bằng lời."
        ),
        P(
            "Mặt khác, khả năng nhận diện dầu từ vùng tối chưa đạt mức đủ tin cậy cho vận hành. Số báo nhầm toàn tập là bằng chứng trực tiếp cho giới hạn này. Học phần có thể đánh giá việc cài đặt, phân tích và cải tiến theo phạm vi đã đăng ký; báo cáo không tự thay giảng viên kết luận điểm hoặc mức đạt của cả nhóm."
        ),
    )

    section(
        5,
        "5.2. Hạn chế và hướng phát triển khả thi",
        P(
            "Hạn chế dữ liệu gồm JPEG không có thông tin hiệu chuẩn bức xạ đi kèm mỗi ảnh, thiếu mask pixel, ít hơn bộ CSIRO công bố 92 ảnh và chưa xác định các chip có cùng cảnh chụp. Hạn chế thuật toán gồm ngưỡng toàn cục, ROI ENL cố định, vòng nền có thể chứa vùng ứng viên khác và tham số diện tích phụ thuộc resize. Hạn chế thực nghiệm gồm bộ mẫu nhỏ cho khảo sát tham số, một realization mỗi mức nhiễu và benchmark chạy song song có ảnh hưởng thời gian."
        ),
        T(
            "Bảng 5.2. Ba hướng tiếp tục trong xử lý ảnh truyền thống",
            [
                ["Hướng", "Cách kiểm tra đề xuất"],
                [
                    "Ước lượng nền cục bộ",
                    "So sánh vòng nền loại trừ vùng ứng viên với nền toàn cục; giữ tập đánh giá riêng",
                ],
                [
                    "Phân đoạn đa tỉ lệ",
                    "Khảo sát cửa sổ và phép hình thái theo độ phân giải; đánh giá bỏ sót/nhận nhầm",
                ],
                [
                    "Gán mask tập đại diện",
                    "Nhóm khoanh vùng độc lập, thống nhất bất đồng; tính IoU/Dice và sai số biên",
                ],
            ],
        ),
        P(
            "Những hướng này không đòi hỏi ML/DL. Nếu thử thêm một quy tắc lọc mới, cần nêu giả thuyết, tham số và tiêu chí trước khi xem kết quả trên tập đánh giá. Một cải thiện về precision có thể làm giảm recall; cần báo cả hai thay vì chỉ lựa chỉ số thuận lợi. Bổ sung mask chỉ phục vụ đánh giá nếu không dùng để huấn luyện mô hình."
        ),
        P(
            "Trước khi nộp, nhóm cần điền MSSV và xác nhận đóng góp, kiểm tra nguồn tham khảo, bổ sung hồ sơ dữ liệu và diễn tập 12 phút trình bày, 3 phút demo, 5 phút vấn đáp. Nhật ký hồi cứu phải ghi đúng ngày bổ sung và minh chứng, không sửa lịch sử commit. Video chưa thực hiện theo yêu cầu hiện tại; điểm và nhận xét trong bảng đánh giá chéo được để trống để từng thành viên tự điền."
        ),
    )
    # Explicit cross-references connect each table to its interpretation.
    introductions = {
        "1.1": "Bảng 1.1 giới hạn các kết luận có thể rút ra từ chuỗi xử lý. ",
        "1.2": "Bảng 1.2 chuyển phạm vi bài toán thành các tiêu chí nghiệm thu. ",
        "1.3": "Bảng 1.3 đối chiếu vai trò và đánh đổi của các hướng tiếp cận. ",
        "2.4": "Các trường hợp ở Bảng 2.1 dùng để phát hiện lỗi số học và hướng gradient. ",
        "2.6": "Bảng 2.2 định nghĩa chỉ số; Bảng 2.3 ghi kết quả chạy các ví dụ số. ",
        "3.1": "Bảng 3.1 xác định module và trách nhiệm tích hợp. ",
        "3.2": "Bảng 3.2 chỉ ra chi phí tăng theo cửa sổ và số pixel. ",
        "3.7": "Bảng 3.3 phân biệt mức bằng chứng mà mỗi kiểu đối chứng cung cấp. ",
        "4.1": "Bảng 4.1 ghi môi trường đã khóa; lệnh tái lập nằm ở mục 3.7 và phụ lục A. ",
        "4.2": "Bảng 4.3 phân biệt dữ liệu đánh giá, demo và ca tổng hợp. ",
        "4.4": "Bảng 4.5 và Bảng 4.6 liệt kê sai số nhóm biên, hình thái và chỉ số. ",
        "4.6": "Bảng 4.8 là lát cắt clip=2 của khảo sát ở Hình 4.1. ",
        "4.8": "Hình 4.4 phóng to vệt chính; Bảng 4.9 cho thấy các ảnh biển vẫn có báo nhầm. ",
        "4.9": "Bảng 4.10 và Bảng 4.11 phải được đọc cùng phạm vi nhãn cấp ảnh. ",
        "5.1": "Bảng 5.1 đối chiếu từng mục tiêu M1–M5 với bằng chứng và giới hạn. ",
        "5.2": "Bảng 5.2 đề xuất các bước kiểm tra cụ thể cho ba hướng cải tiến. ",
    }
    for page in pages:
        key = ".".join(page["title"].split(".")[:2])
        if key in introductions:
            target = next(item for item in page["items"] if item["type"] == "paragraph")
            target["text"] = introductions[key] + target["text"]
    environment = next(p for p in pages if p["title"].startswith("4.1."))
    commands = next(i for i in environment["items"] if i.get("caption", "").startswith("Bảng 4.2."))
    environment["items"].remove(commands)
    integration = next(p for p in pages if p["title"].startswith("3.7."))
    commands["caption"] = "Bảng 3.4. Lệnh và sản phẩm"
    integration["items"].extend(
        [
            commands,
            P(
                "Bảng 3.4 phục vụ kiểm tra giao diện và tái lập từ cùng môi trường; kết quả chạy được lưu riêng với dữ liệu đầu vào."
            ),
        ]
    )
    # Keep table numbers sequential after moving the run instructions to design.
    mapping = {}
    counts = {}
    for page in pages:
        ch = page["chapter"]
        for item in page["items"]:
            if item["type"] == "table":
                counts[ch] = counts.get(ch, 0) + 1
                old = re.match(r"Bảng \d+\.\d+", item["caption"]).group()
                new = f"Bảng {ch}.{counts[ch]}"
                mapping[old] = new
                item["caption"] = item["caption"].replace(old, new, 1)
    for page in pages:
        for item in page["items"]:
            if item["type"] == "paragraph":
                item["text"] = re.sub(
                    r"Bảng \d+\.\d+", lambda m: mapping.get(m.group(), m.group()), item["text"]
                )
    return pages


REFERENCES = [
    "[1] Bộ môn Xử lý ảnh, UTC, “ds btl xla VÀ HƯỚNG DẪN,” tài liệu hướng dẫn BTL trong dự án, không ghi năm.",
    "[2] C. Brekke and A. H. S. Solberg, “Oil spill detection by satellite remote sensing,” Remote Sensing of Environment, vol. 95, pp. 1–13, 2005, doi:10.1016/j.rse.2004.11.015.",
    "[3] K. Topouzelis, “Oil spill detection by SAR images: Dark formation detection, feature extraction and classification algorithms,” Sensors, vol. 8, pp. 6642–6659, 2008, doi:10.3390/s8106642.",
    "[4] J.-S. Lee, “Digital image enhancement and noise filtering by use of local statistics,” IEEE TPAMI, vol. PAMI-2, pp. 165–168, 1980, doi:10.1109/TPAMI.1980.4766994.",
    "[5] A. M. Reza, “Realization of the contrast limited adaptive histogram equalization (CLAHE) for real-time image enhancement,” Journal of VLSI Signal Processing Systems, vol. 38, pp. 35–44, 2004, doi:10.1023/B:VLSI.0000028532.53893.82.",
    "[6] J. Canny, “A computational approach to edge detection,” IEEE TPAMI, vol. PAMI-8, pp. 679–698, 1986, doi:10.1109/TPAMI.1986.4767851.",
    "[7] N. Otsu, “A threshold selection method from gray-level histograms,” IEEE TSMC, vol. 9, pp. 62–66, 1979, doi:10.1109/TSMC.1979.4310076.",
    "[8] D. T. Kuan et al., “Adaptive noise smoothing filter for images with signal-dependent noise,” IEEE TPAMI, vol. PAMI-7, pp. 165–177, 1985, doi:10.1109/TPAMI.1985.4767641.",
    "[9] V. S. Frost et al., “A model for radar images and its application to adaptive digital filtering of multiplicative noise,” IEEE TPAMI, vol. PAMI-4, pp. 157–166, 1982, doi:10.1109/TPAMI.1982.4767223.",
    "[10] R. C. Gonzalez and R. E. Woods, Digital Image Processing, 4th ed. Pearson, 2018.",
    "[11] OpenCV, “Image processing reference,” tài liệu thư viện, https://docs.opencv.org/4.x/d7/dbd/group__imgproc.html. Đối chứng thực tế dùng phiên bản ghi trong manifest.",
    "[12] SciPy, “Multidimensional image processing (scipy.ndimage),” tài liệu thư viện, https://docs.scipy.org/doc/scipy/reference/ndimage.html. Đối chứng thực tế dùng phiên bản ghi trong manifest.",
    "[13] D. Blondeau-Patissier, CSIRO Sentinel-1 SAR image dataset of oil- and non-oil features for machine learning (Deep Learning), CSIRO, Dec. 15, 2022, doi:10.25919/4v55-dn16. Nguồn và CC BY-SA 4.0 theo metadata/giấy phép kèm repo; số ảnh bản cục bộ khác số công bố.",
]
