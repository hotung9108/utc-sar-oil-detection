# Thuyết trình quy trình phát hiện dầu loang trên ảnh SAR

## Dự án UTC SAR Oil Spill Detection

## 1. Giới thiệu bài toán

Ảnh SAR (Synthetic Aperture Radar) thường được sử dụng để quan sát bề
mặt biển và phát hiện các hiện tượng như dầu loang. Trên ảnh SAR, dầu
loang thường xuất hiện dưới dạng những vùng tối hơn so với khu vực biển
xung quanh.

Nguyên nhân là lớp dầu làm giảm các gợn sóng nhỏ trên bề mặt biển, khiến
tín hiệu radar phản xạ trở lại vệ tinh yếu hơn. Tuy nhiên, không phải
vùng tối nào cũng là dầu loang. Các hiện tượng tự nhiên như vùng gió
lặng cũng có thể tạo ra tín hiệu tối tương tự.

Vì vậy, dự án xây dựng quy trình xử lý ảnh gồm 7 bước. Toàn bộ quy trình
sử dụng các thuật toán xử lý ảnh truyền thống, triển khai bằng NumPy,
không sử dụng Machine Learning hoặc Deep Learning.

## 2. Sơ đồ tổng quan quy trình

``` mermaid
flowchart TD
    A["Ảnh SAR đầu vào (Grayscale)"] --> B["1. Khử nhiễu đốm – Lee MMSE Filter"]
    B --> C["2. Cải thiện tương phản – CLAHE"]
    C --> D["3. Phân đoạn vùng tối – Adaptive Otsu"]
    D --> E["4. Tinh lọc – Morphological Opening & Closing"]
    E --> F["5. Dán nhãn – Connected Components"]
    F --> G["6. Lọc diện tích và tỷ số tương phản"]
    G --> H["7. Trích xuất đường biên và Overlay"]
```

Có thể hình dung quy trình như sau: trước tiên làm sạch ảnh, sau đó làm
rõ các vùng tối, tách chúng khỏi nền biển, loại bỏ các vùng nhiễu và
cuối cùng đánh dấu đường biên của những vùng đạt tiêu chí.

------------------------------------------------------------------------

## 3. Giải thích chi tiết từng bước

### Bước 1. Khử nhiễu đốm SAR -- Lee MMSE Filter

**Mục tiêu:** Làm sạch nhiễu đốm nhưng hạn chế làm mất đường biên của
vết dầu.

Ảnh SAR có một dạng nhiễu đặc trưng gọi là *Speckle Noise*. Nhiễu này
khiến những vùng biển tương đối đồng nhất xuất hiện nhiều điểm sáng tối
xen kẽ, làm ảnh trở nên lốm đốm.

Dự án sử dụng bộ lọc Lee MMSE. Bộ lọc xem xét các pixel trong một vùng
lân cận để đánh giá mức độ đồng nhất của khu vực:

-   Nếu khu vực tương đối đồng nhất, bộ lọc tăng cường làm mịn để giảm
    nhiễu.
-   Nếu khu vực có sự thay đổi mức xám lớn, bộ lọc giữ lại nhiều thông
    tin gốc hơn nhằm hạn chế làm mờ cạnh.

Về nguyên lý, bộ lọc tính giá trị trung bình và phương sai cục bộ, sau
đó dùng trọng số Lee để kết hợp giá trị pixel gốc với giá trị trung bình
cục bộ.

Công thức trọng số trong cách triển khai:

\[ W =
`\max`{=tex}`\left`{=tex}(0,`\frac{\sigma_I^2-\sigma_v^2\bar I^2}{\sigma_I^2}`{=tex}`\right`{=tex})
\]

Giá trị pixel sau lọc:

\[ `\hat `{=tex}R = `\bar `{=tex}I + W(I-`\bar `{=tex}I) \]

Trong đó:

-   (I): giá trị pixel đầu vào.
-   (`\bar `{=tex}I): giá trị trung bình cục bộ.
-   (`\sigma`{=tex}\_I\^2): phương sai cục bộ.
-   (`\sigma`{=tex}\_v\^2): phương sai nhiễu theo mô hình.
-   (W): trọng số quyết định mức độ giữ lại thông tin pixel gốc.

**Cách diễn đạt khi thuyết trình:**

"Đầu tiên, chúng ta xử lý nhiễu đốm -- một đặc điểm thường gặp trên ảnh
SAR. Bộ lọc Lee MMSE xem xét mức độ biến thiên của các pixel xung quanh.
Ở vùng biển đồng nhất, bộ lọc làm mịn để giảm nhiễu; còn ở khu vực có
cạnh hoặc thay đổi mức xám rõ rệt, bộ lọc cố gắng giữ lại thông tin gốc.
Nhờ đó, ảnh sạch hơn mà vẫn hạn chế làm mất hình dạng của vết dầu."

**Kết quả:** Ảnh SAR đã giảm nhiễu, được sử dụng làm ảnh tham chiếu cho
các bước xử lý tiếp theo.

### Bước 2. Cải thiện tương phản -- CLAHE

**Mục tiêu:** Làm rõ sự khác biệt giữa vùng tối nghi ngờ dầu loang và
nền biển.

Sau khi khử nhiễu, sự khác biệt giữa vết dầu và vùng biển xung quanh đôi
khi vẫn chưa đủ rõ. Dự án sử dụng CLAHE (*Contrast Limited Adaptive
Histogram Equalization*) để cải thiện tương phản cục bộ.

Thay vì cân bằng histogram trên toàn bộ ảnh, CLAHE chia ảnh thành các ô
nhỏ. Histogram của từng ô được cân bằng riêng, đồng thời giới hạn mức
khuếch đại tương phản để tránh làm nổi nhiễu quá mức.

Các ô sau đó được kết hợp bằng nội suy song tuyến tính (*bilinear
interpolation*) nhằm hạn chế sự xuất hiện của ranh giới giữa các ô.

**Cách diễn đạt khi thuyết trình:**

"Sau khi khử nhiễu, ảnh đã sạch hơn nhưng vùng dầu vẫn có thể chưa nổi
bật. CLAHE cải thiện tương phản trên từng khu vực nhỏ của ảnh. Có thể
hiểu đơn giản, thuật toán giúp sự khác biệt về mức xám giữa các vùng lân
cận trở nên dễ quan sát hơn. CLAHE không trực tiếp phát hiện dầu loang,
mà chỉ cải thiện chất lượng ảnh để hỗ trợ bước phân đoạn."

**Kết quả:** Ảnh có tương phản cục bộ tốt hơn, giúp bước tìm ngưỡng phân
đoạn có thêm thông tin.

### Bước 3. Phân đoạn vùng tối -- Adaptive Otsu Thresholding

**Mục tiêu:** Chuyển ảnh xám thành mặt nạ nhị phân, tách các vùng tối
tiềm năng.

Trên ảnh SAR, vùng dầu thường có mức xám thấp hơn nền biển. Thuật toán
Otsu tự động tìm một ngưỡng mức xám để chia pixel thành hai nhóm:

-   Nhóm pixel có mức xám thấp: vùng tối tiềm năng.
-   Nhóm pixel có mức xám cao hơn: nền biển.

Otsu lựa chọn ngưỡng nhằm tối ưu khả năng phân tách thống kê giữa hai
nhóm pixel, thay vì yêu cầu người dùng đặt một ngưỡng cố định.

#### Cơ chế thích ứng trong dự án

Nếu áp dụng Otsu trực tiếp lên ảnh đã tăng cường tương phản, thuật toán
đôi khi có thể phân đoạn quá nhiều vùng tối. Điều này khiến mặt nạ bị
lan rộng sang những khu vực biển không phải dầu loang.

Để hạn chế hiện tượng này, dự án bổ sung các bước kiểm tra:

1.  Đánh giá khả năng phân tách histogram của ảnh CLAHE và ảnh tham
    chiếu sau lọc Lee.
2.  Nếu ảnh CLAHE có tỷ lệ vùng tối quá lớn hoặc khả năng phân tách kém
    hơn ảnh tham chiếu, hệ thống ưu tiên tính ngưỡng trên ảnh Lee.
3.  Nếu tỷ lệ vùng tối ban đầu vượt ngưỡng cấu hình, hệ thống điều chỉnh
    ngưỡng theo hướng chặt chẽ hơn.

Hệ số khả tách Otsu có thể biểu diễn như sau:

\[ `\eta `{=tex}=
`\frac{\sigma_B^2(T^*)}{\sigma_{\text{Total}}^2}`{=tex} \]

Trong đó:

-   (`\sigma`{=tex}\_B^2(T^\*)): phương sai giữa các lớp tại ngưỡng tối
    ưu.
-   (`\sigma`{=tex}\_{`\text{Total}`{=tex}}\^2): phương sai tổng thể của
    ảnh.

Mặt nạ vùng tối được tạo theo quy tắc:

\[ Mask\_{`\text{dark}`{=tex}}=(I`\leq `{=tex}T) \]

**Cách diễn đạt khi thuyết trình:**

"Ở bước này, chúng ta bắt đầu xác định những khu vực có khả năng chứa
dầu. Otsu tự động tìm ngưỡng mức xám để tách nhóm pixel tối khỏi nhóm
pixel sáng hơn. Tuy nhiên, ảnh sau CLAHE đôi khi có thể khiến vùng tối
bị phân đoạn quá rộng. Vì vậy, dự án so sánh chất lượng phân tách giữa
ảnh CLAHE và ảnh sau lọc Lee, đồng thời điều chỉnh ngưỡng khi vùng tối
chiếm tỷ lệ bất thường. Đây là lý do bước này được gọi là Adaptive
Otsu."

**Kết quả:** Mặt nạ nhị phân chứa các vùng tối tiềm năng, chưa phải kết
quả phát hiện cuối cùng.

### Bước 4. Tinh lọc bằng hình thái học -- Morphological Opening & Closing

**Mục tiêu:** Loại bỏ các điểm nhiễu nhỏ, lấp khe hở và cải thiện tính
liên tục của vùng phân đoạn.

Sau bước Otsu, mặt nạ nhị phân có thể chứa những điểm nhiễu nhỏ hoặc các
vùng nghi ngờ bị đứt đoạn. Dự án sử dụng hai phép toán hình thái học cơ
bản:

#### 4.1. Opening -- Phép mở

Phép mở gồm hai thao tác: co ảnh (*erosion*) trước, sau đó giãn ảnh
(*dilation*):

\[ A`\circ `{=tex}B=(A`\ominus `{=tex}B)`\oplus `{=tex}B \]

Tác dụng chính là loại bỏ những vùng trắng nhỏ không đủ lớn để tồn tại
sau phép co.

Trong dự án, phép mở sử dụng phần tử cấu trúc hình đĩa với bán kính
(r=2).

#### 4.2. Closing -- Phép đóng

Phép đóng thực hiện giãn ảnh trước, sau đó co ảnh:

\[ A`\bullet `{=tex}B=(A`\oplus `{=tex}B)`\ominus `{=tex}B \]

Phép đóng giúp lấp các khe hở nhỏ, nối những vùng gần nhau và làm cho
vùng phân đoạn liên tục hơn.

Trong dự án, phép đóng sử dụng phần tử cấu trúc hình đĩa với bán kính
(r=4).

**Cách diễn đạt khi thuyết trình:**

"Sau khi phân đoạn, mặt nạ vẫn có thể xuất hiện các điểm nhiễu hoặc
những vùng dầu bị đứt đoạn. Chúng ta sử dụng hai phép toán hình thái
học. Opening giúp loại bỏ các vùng nhiễu nhỏ; còn Closing giúp lấp khe
hở và nối những vùng gần nhau. Có thể nhớ ngắn gọn: Opening thiên về
loại bỏ chi tiết nhỏ, Closing thiên về lấp khoảng trống và kết nối
vùng."

**Kết quả:** Mặt nạ nhị phân sạch hơn, các vùng nghi ngờ có hình dạng
liên tục hơn.

### Bước 5. Phân tích thành phần liên thông -- Connected Component Labeling

**Mục tiêu:** Tách từng vùng tối độc lập thành các đối tượng riêng biệt
và xác định thông tin hình học của chúng.

Sau các phép toán hình thái học, hệ thống đã có mặt nạ nhị phân tốt hơn.
Tuy nhiên, các vùng tối vẫn chỉ là những pixel trên cùng một ảnh. Chúng
ta cần xác định có bao nhiêu vùng độc lập và mỗi vùng nằm ở đâu.

Dự án sử dụng thuật toán *Connected Component Labeling* với liên thông 8
hướng (*8-connectivity*). Hai pixel được xem là liên thông nếu chúng
tiếp xúc theo chiều ngang, chiều dọc hoặc đường chéo.

Thuật toán được triển khai bằng cách kết hợp:

-   **Run-Length Encoding:** Biểu diễn các đoạn pixel liên tiếp trên
    từng hàng.
-   **Union-Find:** Hợp nhất các đoạn thuộc cùng một thành phần liên
    thông.
-   **Path Compression:** Tối ưu quá trình tìm đại diện của mỗi tập hợp.

Với mỗi thành phần, hệ thống trích xuất các thông tin:

-   Diện tích (*Area*).
-   Hộp giới hạn (*Bounding Box*).
-   Tâm hình học (*Centroid*).

**Ví dụ:** Nếu mặt nạ có ba vùng tối độc lập, thuật toán sẽ gán cho
chúng ba nhãn khác nhau. Mỗi vùng có diện tích, tọa độ bao quanh và
trọng tâm riêng để phục vụ bước đánh giá tiếp theo.

**Cách diễn đạt khi thuyết trình:**

"Ở bước này, chúng ta chuyển từ việc xử lý toàn bộ mặt nạ sang phân tích
từng đối tượng riêng biệt. Thuật toán Connected Components nhóm các
pixel kết nối với nhau thành từng vùng và gán cho mỗi vùng một nhãn. Nhờ
đó, hệ thống biết được có bao nhiêu vùng tối độc lập, diện tích và vị
trí của từng vùng."

**Kết quả:** Danh sách các thành phần liên thông cùng thông tin hình học
tương ứng.

### Bước 6. Lọc theo diện tích và tỷ số tương phản -- Area & Contrast Ratio

**Mục tiêu:** Loại bỏ các vùng tối không phù hợp, giảm nhầm lẫn với
những hiện tượng tự nhiên giống dầu loang.

Đây là bước quan trọng vì không phải vùng tối nào trên ảnh SAR cũng là
dầu loang. Ví dụ, khu vực gió lặng cũng có thể tạo ra tín hiệu phản xạ
yếu và xuất hiện dưới dạng vùng tối.

Dự án sử dụng hai tiêu chí chính để đánh giá từng thành phần.

#### 6.1. Lọc theo diện tích -- Area Filtering

Những vùng có diện tích quá nhỏ thường là nhiễu hoặc đối tượng không
đáng kể. Vì vậy, dự án đặt ngưỡng diện tích tối thiểu:

\[ Area`\geq `{=tex}min_area \]

Giá trị mặc định trong cấu hình là:

\[ min_area=300`\text{ pixel}`{=tex} \]

Những thành phần nhỏ hơn ngưỡng này sẽ bị loại bỏ.

#### 6.2. Lọc theo tỷ số tương phản -- Contrast Ratio

Tiếp theo, hệ thống đánh giá mức độ tối của vùng nghi ngờ so với nền
biển xung quanh.

Để xác định nền biển lân cận, hệ thống tạo một vùng đệm (*Ring Buffer*)
bằng cách giãn vùng nghi ngờ rồi loại bỏ phần diện tích của chính vùng
đó:

\[ Mask\_{`\text{ring}`{=tex}}=
Dilate(Mask\_{`\text{comp}`{=tex}},B\_{15`\times15`{=tex}})
`\setminus `{=tex}Mask\_{`\text{comp}`{=tex}} \]

Sau đó, tính tỷ số tương phản:

\[
C_R=`\frac{\mu_{\text{sea}}-\mu_{\text{slick}}}{\mu_{\text{sea}}}`{=tex}
\]

Trong đó:

-   (`\mu`{=tex}\_{`\text{sea}`{=tex}}): mức xám trung bình của vùng
    biển bao quanh.
-   (`\mu`{=tex}\_{`\text{slick}`{=tex}}): mức xám trung bình của vùng
    nghi ngờ dầu loang.

Nếu (C_R) lớn, vùng nghi ngờ tối hơn đáng kể so với nền biển xung quanh.

Ngưỡng mặc định của dự án:

\[ min_contrast=0.10 \]

Tức là vùng nghi ngờ cần có tỷ số tương phản tối thiểu 10% để vượt qua
tiêu chí này.

**Ví dụ minh họa:**

Giả sử:

-   Mức xám trung bình vùng biển là 100.
-   Mức xám trung bình vùng nghi ngờ là 80.

Khi đó:

\[ C_R=`\frac{100-80}{100}`{=tex}=0.2=20% \]

Vùng này vượt ngưỡng tương phản 10%.

Nếu tỷ số tương phản chỉ đạt 5%, vùng đó không đạt tiêu chí và sẽ bị
loại bỏ.

**Cách diễn đạt khi thuyết trình:**

"Đây là bước giúp hạn chế nhầm lẫn giữa dầu loang và các hiện tượng tự
nhiên. Đầu tiên, chúng ta loại bỏ những vùng quá nhỏ. Tiếp theo, thay vì
chỉ nhìn vào mức xám của vùng nghi ngờ, hệ thống so sánh nó với khu vực
biển ngay xung quanh. Nếu vùng nghi ngờ tối hơn nền biển đủ nhiều, nó sẽ
vượt qua tiêu chí tương phản. Như vậy, chúng ta đánh giá đối tượng dựa
trên cả kích thước và đặc trưng mức xám."

**Kết quả:** Danh sách các vùng tối đã vượt qua hai tiêu chí lọc diện
tích và tương phản.

### Bước 7. Trích xuất đường biên và Overlay

**Mục tiêu:** Xác định đường viền của các vùng được giữ lại và hiển thị
trực quan trên ảnh SAR gốc.

Sau bước lọc, hệ thống đã xác định được những vùng tối đáp ứng các tiêu
chí của dự án. Để hiển thị kết quả, chúng ta cần xác định đường biên của
từng vùng.

Dự án sử dụng phép trích xuất biên bằng hình thái học:

\[
`\beta`{=tex}(A)=A`\setminus`{=tex}(A`\ominus `{=tex}B\_{3`\times3`{=tex}})
\]

Trong đó:

-   (A): mặt nạ của vùng cần trích xuất biên.
-   (A`\ominus `{=tex}B): kết quả sau phép co ảnh (*erosion*).
-   (`\beta`{=tex}(A)): phần đường biên được giữ lại.

Có thể hiểu đơn giản: chúng ta lấy mặt nạ ban đầu trừ đi phần bên trong
sau khi co ảnh, nhờ đó chỉ giữ lại lớp pixel nằm ở đường viền.

Cuối cùng, đường biên được tô màu đỏ và chồng lên ảnh SAR gốc
(*Overlay*).

**Cách diễn đạt khi thuyết trình:**

"Ở bước cuối cùng, chúng ta trích xuất đường viền của những vùng đã vượt
qua các tiêu chí lọc. Bằng cách lấy mặt nạ ban đầu trừ đi kết quả sau
phép co, hệ thống giữ lại phần đường biên bên ngoài. Sau đó, đường biên
được tô đỏ và chồng lên ảnh SAR gốc để người dùng dễ dàng quan sát vị
trí cũng như hình dạng của các vùng dầu loang được phát hiện."

**Kết quả:** Ảnh SAR có các vùng nghi ngờ dầu loang được đánh dấu đường
biên để trực quan hóa.

------------------------------------------------------------------------

## 4. Tổng kết vai trò của 7 bước

  -----------------------------------------------------------------------
  Bước                    Thuật toán              Vai trò chính
  ----------------------- ----------------------- -----------------------
  1                       Lee MMSE Filter         Khử nhiễu đốm, hạn chế
                                                  làm mất cạnh

  2                       CLAHE                   Cải thiện tương phản
                                                  cục bộ

  3                       Adaptive Otsu           Phân đoạn các vùng tối
                                                  tiềm năng

  4                       Morphological Opening & Loại bỏ nhiễu nhỏ, lấp
                          Closing                 khe hở và kết nối vùng

  5                       Connected Components    Tách từng vùng độc lập
                                                  và trích xuất thông tin
                                                  hình học

  6                       Area & Contrast Ratio   Lọc vùng theo kích
                                                  thước và mức tương phản
                                                  với nền biển

  7                       Boundary Extraction &   Trích xuất đường biên
                          Overlay                 và trực quan hóa kết
                                                  quả
  -----------------------------------------------------------------------

### Lời kết thuyết trình

"Nhìn chung, quy trình của dự án được xây dựng dựa trên sự kết hợp của
các thuật toán xử lý ảnh truyền thống. Mỗi thuật toán giải quyết một vấn
đề cụ thể, từ khử nhiễu, cải thiện chất lượng ảnh, phân đoạn, phân tích
hình thái cho đến đánh giá đặc trưng của từng vùng.

Điểm quan trọng là dự án không sử dụng mô hình học máy để đưa ra dự
đoán, mà dựa trên các đặc trưng vật lý và thống kê của ảnh SAR, kết hợp
với các thuật toán xử lý ảnh để xác định những vùng có khả năng là dầu
loang."

------------------------------------------------------------------------

## 5. Câu hỏi phản biện có thể gặp

### Câu 1. Tại sao sử dụng Lee Filter thay vì Median hoặc Gaussian Filter?

Lee Filter được thiết kế để xử lý nhiễu đốm trong ảnh radar. Bộ lọc sử
dụng thống kê cục bộ để thích nghi với đặc điểm từng vùng ảnh, nhờ đó có
thể giảm nhiễu ở vùng đồng nhất và hạn chế làm mờ các cạnh. Median và
Gaussian là các bộ lọc hữu ích trong nhiều trường hợp, nhưng không mô
hình hóa trực tiếp đặc tính nhiễu đốm nhân như Lee.

### Câu 2. Tại sao cần cả CLAHE và Otsu?

Hai thuật toán có chức năng khác nhau. CLAHE cải thiện tương phản cục bộ
để các vùng có mức xám khác nhau dễ phân biệt hơn. Otsu sử dụng
histogram để tìm ngưỡng và phân đoạn ảnh thành các lớp. CLAHE không thay
thế Otsu và Otsu cũng không thực hiện chức năng tăng cường tương phản.

### Câu 3. Tại sao không sử dụng một ngưỡng cố định?

Mức tán xạ ngược trên ảnh SAR có thể thay đổi theo điều kiện mặt biển,
vùng chụp và đặc điểm ảnh. Một ngưỡng cố định có thể hoạt động tốt trên
ảnh này nhưng không phù hợp với ảnh khác. Otsu giúp tự động xác định
ngưỡng từ histogram của ảnh; cơ chế thích ứng trong dự án tiếp tục kiểm
tra và điều chỉnh kết quả.

### Câu 4. Tại sao cần Opening và Closing?

Opening giúp loại bỏ các chi tiết trắng nhỏ, còn Closing giúp lấp các
khe hở nhỏ và kết nối những vùng gần nhau. Hai phép toán hỗ trợ làm sạch
mặt nạ nhị phân trước khi phân tích từng thành phần.

### Câu 5. Tại sao cần Contrast Ratio?

Một vùng tối không nhất thiết là dầu loang. Contrast Ratio đánh giá mức
độ tối của vùng nghi ngờ so với nền biển lân cận. Đây là một đặc trưng
bổ sung giúp loại bỏ một số vùng tối không phù hợp.

### Câu 6. Không sử dụng Machine Learning/Deep Learning thì có hạn chế gì?

Phương pháp dựa trên xử lý ảnh truyền thống phụ thuộc vào các tham số và
giả định về đặc trưng ảnh. Những hiện tượng tự nhiên có hình dạng và mức
tán xạ ngược tương tự dầu loang vẫn có thể gây nhầm lẫn. Ngoài ra, tham
số phù hợp với một tập ảnh chưa chắc phù hợp với mọi điều kiện quan sát.
Vì vậy, cần đánh giá thực nghiệm trên dữ liệu có nhãn và kiểm tra khả
năng tổng quát hóa.

------------------------------------------------------------------------

## 6. Lưu ý kỹ thuật khi trình bày và bảo vệ

1.  **Lee Filter:** Không nên khẳng định bộ lọc luôn bảo toàn hoàn toàn
    đường biên. Cách diễn đạt chính xác hơn là bộ lọc có khả năng thích
    nghi theo thống kê cục bộ và hạn chế làm mờ cạnh so với một số bộ
    lọc làm mịn đồng nhất.

2.  **CLAHE:** CLAHE có thể làm nổi bật cả nhiễu và hiện tượng giả.
    Không nên khẳng định CLAHE luôn giúp phân biệt dầu và biển tốt hơn.

3.  **Otsu:** Hệ số khả tách cao cho thấy histogram được chia thành hai
    nhóm tốt hơn theo tiêu chí thống kê của Otsu, nhưng không chứng minh
    hai nhóm đó chắc chắn tương ứng với dầu và biển.

4.  **Morphology:** Opening và Closing có thể làm thay đổi diện tích và
    hình dạng vùng phân đoạn. Kernel quá lớn có thể xóa vùng nhỏ hoặc
    nối nhầm các vùng độc lập.

5.  **Contrast Ratio:** Đây là một đặc trưng tương phản tương đối, không
    phải bằng chứng đủ để xác nhận một vùng là dầu loang. Ngưỡng 10% cần
    được kiểm chứng thực nghiệm trên dataset.

6.  **Đường biên:** Phép trừ mặt nạ với kết quả erosion tạo ra đường
    biên hình thái học. Không nên khẳng định đường biên luôn có độ dày
    đúng 1 pixel nếu chưa kiểm tra chi tiết cách triển khai và cấu trúc
    kernel.

7.  **Các tham số cấu hình:** Các giá trị như `min_area = 300`,
    `min_contrast = 0.10`, `num_looks = 4.0` nên được trình bày là tham
    số cấu hình hoặc tham số thực nghiệm của dự án. Chỉ gọi chúng là
    tiêu chuẩn NASA khi có tài liệu NASA cụ thể chứng minh.

## 7. Gợi ý bố cục slide

Có thể chia nội dung thành khoảng 9--10 slide:

1.  **Bài toán và đặc điểm ảnh SAR:** Vì sao dầu loang thường xuất hiện
    dưới dạng vùng tối?
2.  **Sơ đồ tổng quan:** Giới thiệu quy trình 7 bước.
3.  **Khử nhiễu và tăng cường ảnh:** Lee MMSE Filter và CLAHE.
4.  **Phân đoạn vùng tối:** Otsu và cơ chế thích ứng.
5.  **Tinh lọc mặt nạ:** Morphological Opening và Closing.
6.  **Phân tích vùng:** Connected Components.
7.  **Đánh giá và loại bỏ vùng giả:** Area Filtering và Contrast Ratio.
8.  **Trích xuất biên:** Boundary Extraction và Overlay.
9.  **Kết quả thực nghiệm:** So sánh ảnh đầu vào, ảnh trung gian và kết
    quả cuối.
10. **Kết luận:** Ưu điểm, hạn chế và hướng phát triển.

**Nguyên tắc trình bày:** Với mỗi thuật toán, nên trả lời ba câu hỏi:
*Vấn đề gì cần giải quyết? Thuật toán hoạt động như thế nào? Kết quả
được sử dụng ra sao ở bước tiếp theo?* Cách này giúp người nghe hiểu
logic của toàn bộ pipeline thay vì chỉ ghi nhớ tên thuật toán và công
thức.
