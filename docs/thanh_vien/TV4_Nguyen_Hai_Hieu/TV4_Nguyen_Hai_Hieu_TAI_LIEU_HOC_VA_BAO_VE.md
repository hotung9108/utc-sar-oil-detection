# TV4 — Nguyễn Hải Hiếu — Sổ tay học và bảo vệ từ nền tảng

GitHub: `hina-kasumi`. Trách nhiệm: Làm nét, biên, Otsu và hình thái học. Mã phụ trách: `src/tv4/`.

Tài liệu này dành cho người mới. Học lần lượt phần nền tảng, phần cá nhân, ví dụ, thực hành và câu hỏi có gợi ý trả lời. Công thức và mô tả bám vào mã hiện tại của dự án; không mặc nhiên đồng nhất mọi biến thể cùng tên trong tài liệu khác. Đừng chỉ học thuộc đáp án: hãy tính ví dụ rồi kiểm bằng chương trình.

## 1. Nền tảng: máy tính nhìn ảnh như thế nào?

### 1.1. Ảnh số, pixel và tọa độ là gì?

Một ảnh xám trong chương trình là một bảng số có H hàng và W cột. Mỗi ô gọi là pixel; số trong ô biểu diễn mức xám. Với ảnh 8 bit của dự án, 0 là đen và 255 là trắng; các số ở giữa biểu diễn những mức sáng trung gian. Ảnh 400×400 gồm 160.000 giá trị, không phải một vật thể mà máy tự hiểu là biển hay dầu.

Ta viết I[y, x] để lấy pixel ở hàng y, cột x. Python đánh số từ 0: pixel đầu tiên là I [0,0], pixel cuối của ảnh 400×400 là I [399,399]. Trong mảng, chỉ số hàng tăng từ trên xuống, chỉ số cột tăng từ trái sang. Nếu nhầm x với y, ta có thể lấy sai lát cắt, quay hướng đạo hàm hoặc vẽ sai vị trí vùng.

Ví dụ ma trận dưới có hai hàng, ba cột. I [0,2]=200; I [1,0]=20. Ta chưa thể gọi các ô tối là dầu vì bảng chỉ chứa độ sáng.

```text
I = [ [ 10, 100, 200 ],
      [ 20, 110, 210 ] ]
shape = (2, 3)
```

**Để làm gì?** Mọi bộ lọc, ngưỡng và phép đo diện tích đều thao tác trên bảng này. Hiểu ảnh là mảng số giúp ta tính một ví dụ bằng tay rồi đối chiếu code, thay vì chỉ nói ảnh sau xử lý “đẹp hơn”.

**Tự kiểm tra:** Vì sao một vùng 300 pixel không tự tương đương 300 m²? Vì pixel là đơn vị của ảnh. Muốn đổi sang diện tích mặt đất cần độ phân giải không gian, phép chiếu và thông tin xử lý trước đó; JPEG trong repo chưa cung cấp đầy đủ các thông tin ấy.

### 1.2. Ảnh màu, ảnh xám và ảnh nhị phân khác nhau ở đâu?

Ảnh màu thông thường có ba kênh, có thể hình dung là ba bảng số chồng lên nhau. Một file lưu RGB vẫn có thể chỉ thể hiện nội dung xám. Dữ liệu cục bộ được lưu dưới dạng JPEG RGB, nhưng hàm đọc của dự án đưa nó về một bảng xám 2 chiều trước khi xử lý.

Ảnh nhị phân chỉ biểu diễn hai trạng thái. Trong code, mask thường dùng 0 cho nền và 255 cho phần được chọn; khi tính logic có thể dùng False/True. Số 255 ở mask có nghĩa “pixel thuộc vùng đang xét”, không có nghĩa pixel đó vốn sáng hoặc chắc chắn là dầu. Cùng một vị trí có thể có giá trị 40 trong ảnh xám và 255 trong mask.

Đường biên là những pixel quanh ranh giới, còn mask vùng gồm toàn bộ phần bên trong. Một hình vuông đặc 4×4 có diện tích 16 pixel nhưng biên trong 1 pixel chỉ có 12 pixel khi erosion bằng vuông 3×3. Vì vậy không lấy số pixel Canny làm diện tích dầu.

**Vì sao cần phân biệt?** Hàm lọc nhận cường độ; hình thái nhị phân nhận tập pixel; hàm đo diện tích đếm mask. Truyền nhầm loại dữ liệu có thể cho ảnh trông hợp lý nhưng phép đo sai hoàn toàn.

### 1.3. Kiểu dữ liệu: tại sao phải đổi sang số thực?

`uint8` chỉ lưu số nguyên từ 0 đến 255. Phép trừ cần có khả năng tạo số âm, còn tổng có thể vượt 255. Nếu tính trực tiếp trong số nguyên 8 bit, có thể bị tràn hoặc quay vòng giá trị. Chẳng hạn 10−20 phải là −10 về mặt toán học; không được để nó biến thành một số sáng lớn do kiểu dữ liệu.

Các hàm lõi thường đổi ảnh sang `float64`, tính toán xong mới làm tròn, chặn về [0,255] và đổi lại `uint8`. `round` là làm tròn; `clip` là giữ giá trị trong khoảng cho phép. Ví dụ kết quả −3 bị chặn thành 0, 260 thành 255, còn 111,11 được làm tròn thành 111.

Không được chặn mọi giá trị trung gian về 255. Đạo hàm Sobel có thể lớn hơn 255; Canny cần độ lớn gradient thực để so ngưỡng và loại điểm không cực đại. Chỉ ảnh dùng hiển thị hoặc đầu ra được quy ước 8 bit mới nên lượng tử hóa tại bước phù hợp.

**Bài nhỏ:** Với ba kết quả thực [−5, 111,11, 270], đầu ra uint8 sau round rồi clip là [0,111,255]. Nếu bỏ clip, đó không còn là phép biến đổi đã mô tả. Nếu làm tròn quá sớm giữa nhiều bước, sai số có thể tích lũy.

### 1.4. Cửa sổ, kernel và padding là gì?

Cửa sổ là vùng nhỏ quanh pixel đang tính, ví dụ 3×3 hoặc 5×5. Kernel là bảng trọng số hoặc phần tử cấu trúc quy định cách kết hợp các pixel trong cửa sổ. Cùng một cửa sổ 3×3 nhưng kernel trung bình và kernel Sobel có mục đích khác nhau: một cái làm mượt, một cái đo thay đổi.

Với lọc trung bình 3×3, ta cộng chín giá trị và chia 9. Cửa sổ có tám giá trị 100 và một giá trị 200 cho kết quả 1000/9≈111,11. Đây là trung bình, chưa phải mọi chi tiết của bộ lọc Lee. Kernel có kích thước lẻ giúp xác định một ô tâm rõ ràng; dự án kiểm tra kích thước là số nguyên lẻ dương.

Ở mép ảnh, cửa sổ vượt ra ngoài vùng có dữ liệu. Padding là quy tắc bổ sung giá trị để vẫn tính được. Đệm 0 có thể làm mép ảnh tối bất thường. Phản xạ dùng các giá trị đối xứng bên trong ảnh. Với dãy [10,20,30], đệm 1 theo `reflect` cho [20,10,20,30,20]; theo `symmetric` cho [10,10,20,30,30]. Hai quy tắc không giống nhau.

**Vì sao có padding?** Nó xác định giả định về phần ảnh không quan sát được bên ngoài khung. Nếu bản NumPy và thư viện dùng hai cách đệm khác nhau, sai số ở mép không nhất thiết do công thức phần giữa ảnh sai. Trong phép đạo hàm, còn phải phân biệt tương quan với tích chập có lật kernel: đảo kernel đạo hàm có thể đổi dấu.

### 1.5. Trung bình, phương sai, độ lệch chuẩn và histogram

Trung bình μ là tổng giá trị chia số pixel. Nó mô tả mức sáng chung nhưng không mô tả độ dao động. Phương sai v là trung bình của (I−μ)²; độ lệch chuẩn σ là căn bậc hai của v. Hai vùng cùng μ=100 vẫn có thể rất khác: [100,100] có v=0, còn [80,120] có v=400 và σ=20.

Lee cần thống kê cục bộ để điều chỉnh mức làm mượt. ENL cũng dùng μ²/v nhưng mục đích là mô tả độ đồng nhất của một vùng. Không được suy ra mọi thay đổi phương sai đều do nhiễu: một đường biên thật cũng làm phương sai lớn.

Histogram là bảng đếm số pixel ở mỗi mức xám. Ảnh xám 8 bit có 256 ô đếm. Dãy [0,0,1,3] có hist [0]=2, hist [1]=1, hist [3]=1; các ô khác bằng 0. CDF là tổng tích lũy của histogram: số pixel có mức xám nhỏ hơn hoặc bằng một ngưỡng. Histogram và CDF dùng trong HE, CLAHE và Otsu.

**Điểm dễ nhầm:** Histogram bỏ thông tin vị trí. Hai ảnh hoán đổi vị trí pixel có thể có cùng histogram nhưng hình dạng hoàn toàn khác nhau. Vì vậy một kết luận chỉ dựa vào histogram chưa nói đầy đủ về cấu trúc ảnh.

### 1.6. Lọc, tăng tương phản, làm nét, biên và phân đoạn

Lọc là thay mỗi pixel bằng một giá trị tính từ vùng lân cận nhằm giảm dao động hoặc giữ đặc điểm mong muốn. Tăng tương phản là làm các mức sáng dễ phân biệt hơn. Làm nét nhấn mạnh thay đổi nhanh để ảnh trông rõ chi tiết. Phát hiện biên tìm vị trí đổi sáng mạnh. Phân đoạn chia pixel thành những tập/vùng theo một tiêu chí.

Các mục tiêu có thể xung đột. Lọc mạnh làm ít đốm nhưng có thể xóa vệt mảnh. Tăng tương phản mạnh làm vệt rõ hơn nhưng cũng làm nền lốm đốm. Làm nét có thể tạo viền sáng/tối quanh cạnh. Mask có ít vùng hơn sau hình thái không tự có nghĩa là đúng hơn: hai vệt thật có thể bị gộp thành một.

**Cách học đúng:** Với mỗi bước, trả lời đủ bốn câu: đầu vào là gì, phép toán thay đổi gì, đầu ra dùng vào đâu và trường hợp nào nó thất bại. Đừng thay bốn câu đó bằng một câu “giúp tăng độ chính xác”.

## 2. Hiểu bài toán SAR và giới hạn của dự án

### 2.1. Ảnh SAR trong bài này đại diện cho điều gì?

SAR là ảnh radar khẩu độ tổng hợp: độ sáng có liên quan đến tín hiệu radar phản hồi sau các bước tạo ảnh. Nó không phải ảnh màu chụp bằng mắt. Trong ngữ cảnh bài toán, một số vùng dầu có thể làm giảm độ gồ ghề nhỏ của mặt biển và xuất hiện tối hơn nền xung quanh. Tuy nhiên gió yếu, điều kiện biển và các hiện tượng khác cũng có thể tạo vùng tối giống dầu.

Dự án sử dụng JPEG 8 bit đã được chuẩn bị sẵn. Giá trị 50 so với 100 là hai mức xám trong ảnh hiển thị; không được tự diễn giải rằng độ dày dầu hoặc năng lượng phản hồi vật lý luôn gấp đôi. Muốn kết luận vật lý cần dữ liệu hiệu chuẩn và thông tin thu nhận mà các JPEG này không cung cấp đầy đủ.

**Để làm gì?** SAR cung cấp dữ liệu có vệt tối và nhiễu/kết cấu phù hợp để thực hành lọc, tương phản, biên, phân đoạn. Mục tiêu chính của BTL vẫn là hiểu và tự cài các phép xử lý ảnh, không phải chứng minh khả năng vận hành một hệ thống giám sát dầu ngoài thực địa.

### 2.2. Speckle là gì và tại sao khó loại hoàn toàn?

Speckle là sự dao động dạng hạt của tín hiệu ảnh kết hợp. Mô hình đơn giản thường dùng là I=R×η: I là tín hiệu quan sát, R là phần cần ước lượng, η là thành phần dao động nhân. Đây là mô hình để thiết kế bộ lọc, không phải khẳng định mọi đốm trên JPEG đều được mô tả chính xác bởi một biến ngẫu nhiên duy nhất.

Nếu chỉ lấy trung bình mạnh, ta có thể giảm dao động nhưng đồng thời trộn pixel ở hai phía một vệt thật. Bộ lọc thích nghi như Lee sử dụng thống kê cục bộ để thay mức làm mượt theo vùng. Nó vẫn không biết pixel nào chắc chắn là nhiễu, nên không thể bảo đảm xóa hết hạt mà giữ nguyên mọi đường biên.

**Câu hỏi:** “Ảnh đã qua Lee thì phần đen nhỏ còn lại chắc chắn là dầu?” Không. Đó có thể là kết cấu nền, nhiễu còn sót, vùng tối tự nhiên hoặc chi tiết vật thể. Bộ lọc là phép ước lượng cường độ, không phải bộ xác nhận bản chất vật lý.

### 2.3. Luồng chạy thật của dự án

Đọc `src/tv1/pipeline.py`. Mặc định, ảnh xám đi qua Lee 5×5 với L=4, rồi CLAHE clip=2 và lưới 8×8. Nhánh làm nét tạo `displayed` để quan sát; nhánh phân đoạn dùng ảnh trước làm nét. Phần hình thái có thể chọn ảnh sau Lee hoặc ảnh sau CLAHE để phân ngưỡng theo quy tắc trong `src/tv4/morphology.py`. Ảnh sau Lee luôn được truyền làm tham chiếu đo tương phản vùng/nền khi chạy cấu hình mặc định.

```text
raw -> filtered -> enhanced -> displayed (nhánh quan sát)
          |             |
          +-> tham chiếu +-> chọn ảnh phân ngưỡng
                              -> opening -> closing
                              -> liên thông -> lọc vùng
                              -> mask -> boundary -> overlay
```

`raw` là ảnh đầu vào đã đọc xám; `filtered` là ảnh lọc; `enhanced` là ảnh tăng tương phản. `mask` là vùng được giữ, `boundary` là biên, `overlay` là biên màu phủ lên ảnh gốc. `stats` là số vùng/diện tích/tương phản; `metrics` là sáu chỉ số mô tả ảnh. Chúng trả lời các câu hỏi khác nhau và không được dùng thay cho nhau.

Nếu chọn Canny/Sobel/Prewitt/Roberts/LoG thay cho morphology, pipeline tạo bản đồ biên nhưng không tạo mask vùng dầu: `mask=None`, `stats={}`. Đây là cách ngăn lấy số pixel biên làm diện tích vùng.

### 2.4. Vì sao 00013 nhìn có một vệt nhưng sau CLAHE lộ thêm đốm?

Mắt người dễ chú ý tới vệt có tương phản mạnh nhất. Nền nhìn có vẻ đều vẫn có thể chứa pixel 95,98,100,103. Sau Lee, biến thiên có thể nhỏ đi nhưng không nhất thiết về đúng một giá trị. CLAHE ánh xạ histogram theo vùng, có thể kéo khoảng nhỏ đó thành khoảng dễ nhìn hơn. Ví dụ minh họa một ánh xạ tương phản có thể biến [98,100,102] thành [70,100,130]; đây là ví dụ nguyên lý, không phải số đo của ảnh 00013.

Toán tử biên chỉ thấy chênh lệch số tăng lên, nên có thể đánh dấu những đốm vừa nổi rõ. Điều đó không chứng minh thuật toán CLAHE bị lỗi; cũng không chứng minh các đốm là dầu. Nếu ta đặt tên tất cả biên ấy là “dầu”, sai nằm ở kết luận ứng dụng vượt quá bằng chứng.

Dự án giảm ảnh hưởng này bằng cách đo tương phản trên ảnh trước CLAHE, dùng diện tích tối thiểu, hình thái và quy tắc chọn ảnh phân ngưỡng. Những bước này vẫn là heuristic, nghĩa là quy tắc thiết kế có thể hữu ích nhưng không có bảo đảm đúng trên mọi ảnh. 00013 giữ khoảng một vùng 2,08% ở cấu hình đang báo cáo; không được lấy một ca thành công thay cho đánh giá toàn tập.

### 2.5. Vì sao có precision / recall mà vẫn không có ML / DL?

ML / DL nói về phương pháp học mô hình hoặc biểu diễn từ dữ liệu. Precision/ recall nói về cách đếm đúng/sai của một quyết định. Một quy tắc cổ điển “ảnh có ít nhất một vùng tối đạt điều kiện thì báo ứng viên” cũng có thể được đánh giá bằng hai chỉ số này, giống như một ngưỡng báo động thiết kế bằng tay.

Trong dự án, hàm xử lý không nhận nhãn Class_0 / Class_1 để học. Nó dùng các phép tính cố định; nhãn chỉ được so sánh sau khi đã xử lý. Không có vòng huấn luyện, hàm mất mát, lan truyền ngược hay file trọng số mô hình. Một phép convolution bằng kernel Sobel cố định không phải mạng CNN. “Thích nghi theo thống kê ảnh” cũng không tự có nghĩa là học máy.

Trọng tâm học phần là công thức, cài NumPy, đối chiếu thư viện, ảnh trước–sau và khảo sát tham số. Precision/ recall là phần đánh giá bổ sung của quy tắc báo vùng tối. Việc dùng Codex để hỗ trợ phát triển được khai báo trong báo cáo; đó là chuyện công cụ làm bài, khác với thuật toán chạy trên ảnh lúc demo.

### 2.6. Những điều mọi thành viên phải nói đúng

Một phép toán khớp thư viện không bảo đảm đúng nhãn dầu. Một ảnh đẹp không bảo đảm giữ đúng chi tiết. Một vùng lớn không bảo đảm là vật thể cần tìm. Một chỉ số tốt không thay thế ảnh đối chứng. Không có mask chuẩn thì chưa báo được IoU/Dice theo ground truth pixel. Không có nguồn độ phân giải phù hợp thì không tự đổi pixel sang km².

**Câu hỏi tổng hợp:** Tắt CLAHE mà số vùng vẫn có thể giống nhau, vì sao? Một khả năng là quy tắc đã chọn ảnh sau Lee làm ảnh phân ngưỡng; một khả năng khác là các vùng nhỏ bị loại ở bước sau. Muốn kết luận phải kiểm tra tham số, ảnh trung gian và nhánh điều kiện, không suy đoán từ ảnh cuối.

## 3. Đạo hàm, làm nét và các toán tử biên cơ bản

### 3.1. Đạo hàm trong ảnh nghĩa là gì?

Đạo hàm đo sự thay đổi. Với dãy mức xám [100,100,100,200,200], hiệu giữa hai vị trí lân cận gần 0 ở vùng phẳng và lớn ở chỗ chuyển 100→200. Trong ảnh2D, ta đo thay đổi theo ngang Gx và dọc Gy. Gradient là cặp (Gx, Gy); độ lớn thường là sqrt (Gx²+Gy²); hướng lấy từ atan 2 (Gy, Gx).

Vì sao cần? Một cạnh thường đi kèm thay đổi cường độ, nên gradient giúp định vị cạnh. Nhưng nhiễu cũng làm thay đổi cường độ; gradient không biết nguyên nhân vật lý. Cạnh của một đốm nền được CLAHE khuếch đại vẫn có thể cho đáp ứng lớn.

Độ lớn không âm nhưng Gx/Gy có thể âm. Dùng uint8 cho đạo hàm làm mất thông tin dấu và miền giá trị. Hướng còn phụ thuộc quy ước tọa độ; trong ảnh, hàng tăng xuống dưới. Không học một sơ đồ góc trong sách rồi áp mà không kiểm quy ước code.

### 3.2. Roberts, Prewitt và Sobel

Roberts lấy chênh lệch theo hai đường chéo của cửa sổ 2×2. Ví dụ[[10,10],[10,110]] cho gx=10−110=−100, gy=10−10=0, magnitude 100. Nó đơn giản nhưng cửa sổ nhỏ ít làm mượt, nên dễ phản ứng với dao động cục bộ.

Prewitt 3×3 so tổng bên phải với bên trái và tổng dưới với trên, trọng số các hàng/cột bằng nhau. Sobel cũng 3×3 nhưng trọng số hướng vuông góc là 1,2,1. Với Gx, hàng giữa nặng hơn, tạo tác dụng làm mượt nhẹ theo chiều vuông góc với đạo hàm.

```text
Sobel Kx = [-1  0  1]     Sobel Ky = [-1 -2 -1]
           [-2  0  2]                [ 0  0  0]
           [-1  0  1]                [ 1  2  1]
```

Trong ví dụ tâm của[[0,0,0],[0,100,100],[0,100,100]], Gx=300, Gy=300, magnitude≈424,264. Hàm trả bản magnitude uint8 để hiển thị nhưng vẫn trả Gx/Gy float; Canny dùng chúng để tính lại độ lớn thực. Ngưỡng 90 của magnitude không có cùng ý nghĩa với ngưỡng mức xám 90.

### 3.3. Unsharp và high-boost: tại sao làm nét có thể tạo viền?

Unsharp đầu tiên làm mờ ảnh f thành b, lấy chi tiết m=f−b, rồi cộng f+k×m. Dù tên có chữ “ unsharp ”, mục tiêu cuối là làm nét nhờ cộng lại thành phần khác giữa ảnh và ảnh mờ. k=1 là lựa chọn thông dụng trong code; k>1 được gọi high-boost theo cách triển khai này.

Nếu pixel gốc 100 và bản mờ 90, chi tiết 10; k 1 cho 110, k 2 cho 120. Nếu pixel gốc 80 nhưng bản mờ 90, chi tiết−10; k 1 cho 70. Vì vậy hai phía cạnh có thể sáng hơn/tối hơn, tạo halo. Nhiễu tần số cao cũng có thể bị tăng.

**Vì sao tách khỏi phân đoạn?** Làm nét thay cường độ theo mục đích quan sát. Đưa ảnh đó vào threshold có thể tạo thêm vùng giả hoặc đổi diện tích chỉ vì tham số hiển thị. Pipeline hiện tách `displayed` khỏi mask để giảm sự lẫn lộn này.

### 3.4. Laplacian sharpening và LoG không phải một thứ

Laplacian là đạo hàm bậc hai. Kernel 4 láng giềng tâm−4 cho đáp ứng L=trên+dưới+trái+phải−4×tâm. Làm nét dùng f−alpha×L. Nếu tâm 120, bốn láng giềng 100, L=400−480=−80; alpha 0,5 cho 160. Dấu trong công thức phụ thuộc kernel tâm âm hay dương; không đổi dấu tùy ý.

LoG là Laplacian of Gaussian, dùng đạo hàm bậc hai đã gắn với làm mượt Gaussian để tìm điểm đổi dấu. Code tạo kernel theo sigma, trừ mean để tổng gần 0, tính đáp ứng rồi tìm các cặp láng giềng đối diện có tích âm và chênh lệch vượt threshold. Đây là đầu ra biên, không phải ảnh làm nét.

Ví dụ hai đáp ứng−6 và+7 cho tích âm, chênh 13; nếu threshold 4 thì đạt. Hai đáp ứng−0,00000000001 và+0,00000000001 có thể chỉ do sai số; code ép đáp ứng có trị tuyệt đối<1e−9 về 0 để tránh coi đó là biên vật lý. Hai số cùng dấu dù chênh lớn chưa đáp ứng điều kiện zero-crossing này.

## 4. Canny: tại sao cần nhiều bước thay vì chỉ threshold Sobel?

### 4.1. Làm mịn rồi tính gradient

Canny kết hợp giảm nhiễu, định hướng biên, làm mảnh và nối biên có điều kiện. Trong hàm hiện tại, ảnh được làm mịn Gaussian 5×5 với sigma mặc định 1,2 trước Sobel. Bước này giảm đáp ứng do dao động nhỏ nhưng cũng có thể làm yếu biên mảnh; sigma là một đánh đổi.

Hàm tính magnitude bằng `np.hypot(gx,gy)` từ đạo hàm float. Nếu chặn về 255 trước bước sau, hai độ lớn 300 và 600 đều thành 255, làm mất quan hệ cần dùng để xác định điểm mạnh nhất và threshold.

### 4.2. Non-maximum suppression là gì?

NMS chỉ giữ điểm có magnitude không nhỏ hơn hai láng giềng dọc theo hướng gradient. Gradient chỉ hướng thay đổi nhanh nhất, thường vuông góc với đường biên; so theo hướng đó giúp giảm một dải đáp ứng dày về các điểm cực đại.

Ví dụ magnitude theo hướng đang xét là [10,30,20]. Điểm 30 được giữ; điểm 20 sẽ bị loại nếu láng giềng 30 mạnh hơn. Nếu hai điểm bằng nhau, code dùng >= nên có thể giữ cả điểm bằng nhau trong một plateau; đừng hứa mọi biên luôn mảnh đúng 1 pixel trong mọi trường hợp.

Code lượng tử hóa góc thành bốn nhóm. Với quy ước Gx/Gy hiện tại, nhóm 0 so trái/phải,90 so trên/dưới,45 so trên-trái/dưới-phải,135 so trên-phải/dưới-trái. Nên đối chiếu các mảng trong thân hàm; một chú thích cũ có thể không đủ làm bằng chứng về cặp thực sự được dùng.

### 4.3. Ngưỡng kép và hysteresis dùng để làm gì?

Ngưỡng cao xác định biên mạnh; ngưỡng thấp giữ các điểm yếu có khả năng là phần tiếp nối của biên mạnh. Chỉ threshold cao sẽ làm đứt cạnh; chỉ threshold thấp sẽ giữ nhiều nhiễu. Hysteresis giữ điểm yếu nếu nối được tới một điểm mạnh qua các điểm yếu/mạnh theo 8 hướng.

Ví dụ high 90, low 35: đoạn magnitude [100,60,50] liên thông có một điểm mạnh rồi hai điểm yếu, nên có thể giữ cả chuỗi. Một đốm 60 đứng riêng không nối tới điểm mạnh sẽ bị loại. Các con số là magnitude sau NMS, không phải mức xám của ảnh ban đầu.

Code dùng hàng đợi BFS: đưa tất cả điểm mạnh vào queue, lấy từng điểm ra và thêm láng giềng yếu chưa thăm. `visited` ngăn duyệt lặp/vòng lặp. Đây là thuật toán đồ thị cổ điển, không phải học mô hình.

### 4.4. Các trường hợp biên phải kiểm

Ảnh hằng có magnitude 0. Khi low=high=0, điều kiện chỉ `>=0` sẽ nhận mọi pixel; code còn yêu cầu nms>0 nên ảnh hằng không biến thành toàn biên. Hàm từ chối low>high vì khi đó khái niệm yếu/mạnh không còn phù hợp.

Hàm có nhánh tự chọn threshold từ trung vị nếu truyền None; nhưng pipeline / demo mặc định truyền 35 và 90. Vì vậy không được nói mặc định demo đang “tự học ngưỡng Canny theo mỗi ảnh”. Ngay cả nhánh tự tính ngưỡng cũng chỉ là quy tắc thống kê, không phải ML.

