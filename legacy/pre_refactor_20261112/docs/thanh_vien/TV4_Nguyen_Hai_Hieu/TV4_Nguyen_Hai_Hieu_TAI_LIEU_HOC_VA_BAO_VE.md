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

### 4.5. Canny chưa tạo diện tích vùng dầu

Biên có thể đứt, có lỗ hoặc thuộc kết cấu nền. Lấp mọi đường bao Canny thành một vùng là một quyết định bổ sung cần thiết kế và kiểm chứng riêng. Pipeline hiện không làm điều đó; nó trả `mask=None` khi chọn Canny. Giới hạn này giúp tránh một phép đo diện tích không có cơ sở.

## 5. Otsu và quy tắc chọn ảnh phân ngưỡng

### 5.1. Phân ngưỡng là gì?

Phân ngưỡng gán pixel vào hai nhóm theo một số T. Vì mục tiêu là vùng tối, ta dùng I<=T làm foreground. T thấp hơn thường giữ ít pixel tối hơn trên cùng ảnh. Phân ngưỡng không biết hình dạng hoặc bản chất dầu; nó chỉ chia cường độ.

Ngưỡng thủ công là số do người dùng đặt. Otsu tìm số đó bằng một tiêu chí histogram: tối đa hóa mức tách trung bình giữa hai nhóm, có tính đến tỷ lệ pixel mỗi nhóm. Ưu điểm là không phải chọn T bằng mắt cho từng ảnh; hạn chế là tiêu chí mức xám không phải tiêu chí nhãn dầu.

### 5.2. Công thức Otsu và từng ký hiệu

Tại mỗi t, w0 là tỷ lệ pixel<=t, w1=1−w0. μ0 và μ1 là mean của hai nhóm. Điểm giữa lớp là B (t)=w0×w1×(μ0−μ1)². Chọn t có B lớn nhất. Trọng số giúp tránh chỉ chọn một pixel cực đoan có mean rất khác nhưng đại diện quá ít ảnh.

Code tạo histogram 256 bin, CDF xác suất và CDF tổng mức xám, rồi quét 256 ngưỡng. Nó bỏ các ngưỡng làm một nhóm gần rỗng để tránh chia 0. η=max (B)/ variance_toàn_ảnh mô tả khả tách mức xám; ảnh hằng có variance gần 0 được trả(0,0).

### 5.3. Ví dụ hai mức và điểm dễ sai ở endpoint

Ảnh có một nửa 50, một nửa 200: mean 125, variance 5625. Với t 50..199, hai nhóm đều 0,5 và chênh mean 150; B=5625, η 1. Code giữ ngưỡng tối ưu đầu tiên là 50. Điều kiện <=50 giữ đúng nửa tối; <50 làm mất hết nửa đó.

η 1 chỉ nói histogram có hai nhóm rõ, không chứng minh một nhóm là dầu. Một hình vẽ đen–trắng không liên quan biển cũng có thể cho khả tách cao.

### 5.4. Vì sao dự án có reference_image?

CLAHE có thể đổi histogram làm vùng tối bị mở rộng. Hàm nhận cả ảnh enhanced và ảnh filtered làm reference. Nếu tỷ lệ tối của enhanced>30% trong khi reference<=30%, hoặc η_reference lớn hơn η_enhanced hơn 0,05, code chọn reference làm ảnh phân ngưỡng; nếu không chọn enhanced. Đây là quy tắc dự án, không phải một định lý của Otsu.

Trong chế độ tự động, nếu vùng tối ban đầu của ảnh đã chọn>35%, code giảm T một lượng delta=max (round(0,10×(mean_sáng− mean_tối)),3), không xuống dưới 1. Mục đích là thu hẹp vùng tối quá rộng; mặt trái là có thể bỏ vùng dầu thật rộng hoặc mờ. Khi dùng ngưỡng thủ công, bước giảm tự động này không áp dụng.

Với manual threshold, ảnh để threshold là enhanced, còn ảnh đo tương phản vẫn ưu tiên reference. Cần phân biệt ảnh dùng để tạo mask và ảnh dùng để đo C_R. Một câu “tất cả tính trên CLAHE” là sai với pipeline hiện tại.

## 6. Hình thái học và liên thông: từ pixel rời đến vùng

### 6.1. Phần tử cấu trúc là gì?

Phần tử cấu trúc B là mẫu nhỏ quy định những vị trí lân cận tham gia phép hình thái. `disk_kernel(r)` giữ các ô có x²+y²<=r² trong khung(2 r+1)×(2 r+1). Đĩa bán kính 2 nằm trong khung 5×5 nhưng không phải cả 25 ô đều bằng 1. Kernel vuông giữ mọi ô; chữ thập chỉ giữ hàng/cột giữa.

Chọn B là chọn thang và hình dạng chi tiết muốn tác động. Kernel lớn có thể loại gai nhỏ/lấp khe rộng hơn, đồng thời làm mất hoặc gộp cấu trúc thật. Không có một kernel “phù hợp nhất” cho mọi vệt chỉ vì hình đĩa nhìn tự nhiên.

### 6.2. Erosion và dilation bằng logic

Erosion giữ pixel nếu tất cả vị trí được B chọn đều thuộc foreground. Với mask nhị phân, đó là AND của các mảng dịch tương ứng. Dilation giữ pixel nếu có ít nhất một vị trí được B chọn là foreground, tương ứng OR trong cài đặt dùng các kernel đối xứng này.

Ví dụ khối 4×4 giữa ảnh 8×8, kernel vuông 3×3: erosion còn 2×2=4 pixel; dilation thành 6×6=36 pixel. Một pixel đứng riêng bị erosion xóa, nhưng dilation biến nó thành một cụm. Vì vậy chỉ dùng dilation để “nối vệt” cũng sẽ làm nhiễu to hơn.

Padding phải khớp mục đích. Code erosion thông thường dùng ngoại vi True như giá trị trung tính, dilation dùng False. Riêng trích biên dùng erosion ngoại vi 0 để thể hiện cả ranh giới chạm khung ảnh. Không áp mặc định của OpenCV mà bỏ qua sự khác biệt này khi đối chiếu.

### 6.3. Opening và closing vì sao không đổi chỗ được?

Opening=erosion rồi dilation. Bước co loại các cấu trúc không chứa được kernel; bước giãn phục hồi một phần kích thước những cấu trúc còn lại. Nó thường loại đốm/gai nhỏ nhưng có thể xóa vệt thật hẹp. Dilation sau đó không thể khôi phục một vùng đã bị xóa sạch ở erosion.

Closing=dilation rồi erosion. Bước giãn có thể nối khe/lấp lỗ nhỏ; bước co thu lại vùng mở rộng. Nếu hai vệt gần nhau bị nối thành một, erosion sau không nhất thiết tách lại. Vì vậy closing không có nghĩa chỉ “vá những chỗ sai” đã biết.

Pipeline mặc định opening bằng đĩa r=2 rồi closing bằng đĩa r=4. Đổi closing_radius về 0 làm closing gần phép đồng nhất với kernel 1×1, nhưng opening r=2 vẫn tồn tại. Đây là lý do có thể còn mất đốm nhỏ dù đã đặt closing 0.

### 6.4. Liên thông 4 và liên thông 8

Hai pixel liên thông 4 nếu có thể đi giữa chúng bằng các bước trên/dưới/trái/phải qua foreground. Liên thông 8 còn cho phép chéo. Với mask[[1,0],[0,1]], có hai vùng nếu dùng 4, một vùng nếu dùng 8. Dự án chọn 8, nên chạm chéo có thể gộp vùng.

Gán nhãn đặt một số nguyên cho mỗi vùng. Số nhãn 1 hay 7 chỉ là tên nhóm, không phải thứ hạng hoặc mức tin cậy. Khi so với thư viện, cần so phân hoạch pixel thành vùng, không đòi số nhãn giống hệt nếu thứ tự đánh số khác.

### 6.5. Run-length union-find hoạt động ra sao?

Run là một đoạn foreground liên tiếp trên một hàng, ví dụ các cột 3..8. Code tìm điểm bắt đầu/kết thúc đoạn từ biến thiên 0→1 và 1→0. Mỗi đoạn được một nhãn tạm; so với các đoạn ở hàng trước. Với liên thông 8, hai khoảng cột cách nhau không quá 1 cũng cần hợp nhất vì có thể chạm chéo.

Union-find quản lý quan hệ các nhãn cùng nhóm. `root` tìm đại diện và nén đường đi để lần sau tìm nhanh hơn; union gộp hai đại diện. Sau khi quét, code quy nhãn tạm về đại diện và đánh số vùng liên tục.

**Ví dụ:** Hàng 0 có đoạn [2,3], hàng 1 có đoạn [4,5]. Chúng chạm chéo qua cột 3→4, nên cùng vùng 8. Nếu hàng 1 bắt đầu 5, khoảng cách từ 3 đến 5 là 2, không liên thông trực tiếp giữa hai đoạn này.

Hàm trả tổng số thành phần, ảnh nhãn và danh sách đặc trưng. `min_area` lọc danh sách đặc trưng, không xóa nhãn nhỏ khỏi ảnh nhãn trả về hoặc thay tổng số vùng đã phát hiện. Đây là hợp đồng phải hiểu khi tích hợp.

### 6.6. Trích biên hình thái khác mask thế nào?

Biên trong β (A)=A−erosion (A, B). Với vuông 4×4 vàB 3×3, βcó 12 pixel còn A có 16. Nếu A có lỗ bên trong, biên có thể xuất hiện quanh lỗ chứ không chỉ đường bao ngoài. Độ dày và hình dạng phụ thuộc kernel, raster và cấu trúc; không hứa mọi đường biên trơn/khép kín đúng 1 pixel trong mọi ảnh.

## 7. Lọc vùng bằng diện tích và tương phản

### 7.1. Diện tích là gì và tại sao dùng min_area?

Diện tích pixel là số ô foreground thuộc một thành phần liên thông. `min_area=300` nhằm loại những vùng nhỏ khó phân biệt với đốm; đây là quy tắc thiết kế trên kích thước 400×400. Nó không biết vùng nhỏ nào là dầu thật. Tăng ngưỡng có thể giảm báo nhầm và tăng bỏ sót cùng lúc.

Tỷ lệ diện tích=100×tổng_pixel_được_giữ/(H×W). Ví dụ một mask có 3328 pixel trong 400×400 cho 2,08%. Đây là ví dụ tính phần trăm, không phải đổi sang đơn vị mặt đất. Kết quả hiển thị được làm tròn nên không dùng phần trăm đã làm tròn để khôi phục chính xác số pixel.

### 7.2. Ring nền và C_R là gì?

Ring là phần xung quanh vùng: giãn mask vùng bằng kernel vuông 15×15 rồi bỏ chính mask ấy. Mean của ring được dùng làm μ_nền; mean bên trong là μ_vùng. Với pipeline mặc định, hai mean được đo trên ảnh filtered trước CLAHE để hạn chế việc tự dùng tương phản vừa khuếch đại làm bằng chứng.

C_R=(μ_nền−μ_vùng)/μ_nền khi μ_nền>0,001; nếu nền quá gần 0 thì code gán 0. Nếu ring không có pixel hợp lệ, vùng bị bỏ qua vì không đo được tương phản cục bộ. C_R là tương phản, không phải độ tròn, xác suất dầu hay độ chính xác.

Ví dụ μ_nền 100, μ_vùng 80 cho C_R 0,20, đạt min_contrast 0,10. μ_vùng 95 cho 0,05, không đạt dù diện tích rất lớn. Mọi vùng đều phải qua điều kiện tương phản; diện tích lớn không tạo ngoại lệ.

### 7.3. Một ví dụ quyết định đầy đủ

Giả sử sau opening/closing có vùngA 350 pixel, C_R 0,20; vùngB 200 pixel, C_R 0,40; vùngC 10000 pixel, C_R 0,05. Với min_area 300, min_contrast 0,10: A được giữ, B bị loại do diện tích, C bị loại do tương phản. Chưa có bước nào xác nhận A thực sự là dầu; A chỉ đáp ứng các điều kiện thiết kế.

Nếu tăng min_area 400, cả A cũng mất. Nếu giảm min_contrast 0,04, C có thể được giữ và làm diện tích tăng mạnh. Đó là lý do không đổi nhiều tham số cùng lúc khi muốn giải thích tác dụng.

### 7.4. Những nguồn sai còn tồn tại

Ring có thể chứa vùng tối khác, nên μ_nền không chắc đại diện biển sạch. Vùng chạm mép có ring bị giới hạn. Tham số cố định có thể không phù hợp mọi cảnh. Otsu toàn cục khó với nền không đồng đều. Opening xóa vùng nhỏ thật, closing gộp hai vùng, liên thông 8 gộp chạm chéo. Kết luận ứng viên vẫn có false positive/false negative.

Trong thống kê, `mean_contrast_ratio` là trung bình C_R theo vùng được giữ, không có trọng số diện tích. Nếu hai vùng có diện tích rất khác, trung bình đơn giản này không bằng tương phản của tất cả pixel gộp lại. TV4 cần giải thích điều đó khi bàn giao số liệu cho TV5.

### 7.5. Bất biến và phản ví dụ để tự kiểm tra

Ảnh hằng phải không tạo ứng viên tối; mask chỉ chứa 0/255; số pixel biên không được dùng thay area; thay sharpening không đổi mask; Canny chỉ giữ điểm yếu nối được tới mạnh. Phản ví dụ cho quy tắc “vùng lớn là dầu” là một mảng biển tối tự nhiên rộng. Phản ví dụ cho “vùng nhỏ là nhiễu” là một vệt dầu nhỏ thật.

Các bất biến kiểm tính nhất quán của phần mềm, không chứng minh mọi quyết định vùng đều đúng với thực địa. Hãy trình bày cả điều đã kiểm và điều chưa có ground truth để kiểm.

## 8. Kết quả chạy thuật toán được lưu ở đâu và đọc thế nào?

### 8.1. Phân biệt mã, dữ liệu, kết quả và tài liệu

Mã nguồn nằm trong `src/` và các entrypoint. Dữ liệu đầu vào chính nằm trong `kaggle/data/Class_0`, `Class_1`. Kết quả thực nghiệm đang dùng nằm trong `results/reproducible/` và `results/verification/`. Báo cáo, slide và bản bằng chứng đóng băng nằm trong `docs/`. Không tìm ảnh đầu ra trong folder thuật toán rồi kết luận chương trình chưa chạy.

Trên máy hiện tại, gốc dự án là `D:\Codin\utc-code\HK4_1\XLA\BTL`. Các đường dẫn tiếp theo được tính từ gốc này. Manifest kiểm tra khi biên soạn ghi lượt toàn tập hoàn tất lúc 21:36:42 ngày 11/11/2026, múi giờ +07:00. Việc sửa sổ tay không tự là một lượt chạy thuật toán mới; cần đọc manifest nếu muốn xác định lần đo.

### 8.2. Những file kết quả hiện có

| Đường dẫn | Nội dung và cách sử dụng |
| --- | --- |
| `results/reproducible/dataset_per_image.csv`| 5.538 hàng ảnh: input, label, prediction, số vùng, area_pct, contrast, runtime; dùng truy từng ca |
| `results/reproducible/confusion.json`| Tổng TP/FP/FN/TN và chỉ số cấp ảnh; không phải model hoặc mask |
| `results/reproducible/dataset_summary.csv`| Thống kê gộp theo lớp; phải hiểu ý nghĩa mỗi cột |
| `results/reproducible/manifest.json`| Cấu hình, hash nguồn, môi trường, thời điểm và phạm vi full/samples |
| `results/reproducible/filters_per_image.csv`| So bộ lọc trên 10 ảnh mẫu, tắt tăng tương phản |
| `results/reproducible/clahe_per_image.csv`| Khảo sát clip/grid trên tập mẫu |
| `results/reproducible/edge_noise_per_image.csv`| Các phương pháp biên dưới các mức nhiễu khảo sát |
| `results/reproducible/failure_cases_per_image.csv`| 00013 và 5 ảnh biển, có/không CLAHE |
| `results/verification/hand_examples.json`| Kết quả mong đợi, kết quả thực tế và phép tính của 5 ví dụ tay |
| `results/verification/per_case.csv`| 594 đối chiếu chi tiết; đọc kind/limit/verdict cùng sai số |
| `results/verification/summary.csv`| Bảng đối chiếu gộp theo phép toán và nhóm tham chiếu |

CSV là văn bản bảng, có thể mở bằng Excel hoặc Pandas. JSON lưu cặp tên–giá trị/cấu trúc lồng nhau, phù hợp cấu hình và thống kê. Không sửa tay các giá trị đo chỉ để bảng đẹp; nếu cần sửa cách đo, sửa mã và chạy lại, đồng thời ghi nguồn gốc lần đo mới.

### 8.3. Những PNG đã được lưu tự động

Trong `results/reproducible/`, `class_1_00013_clahe.png` và `class_1_00013_none.png` là ảnh so sánh nhiều ô: input, filtered, enhanced và overlay. `roi_00013.png` so vùng cắt của ảnh gốc/lọc/tăng cường. Các file `sea_surface_01_clahe.png` tới các mẫu biển tương ứng minh họa ca lỗi; hậu tố `none` cho phiên bản không CLAHE.

**Toàn tập hiện lưu số liệu từng ảnh, chưa lưu 5.538 bộ ảnh PNG trung gian/mask.** Vì vậy không có một folder chứa mask riêng của mọi ảnh đã chạy batch. Muốn xem một ảnh cụ thể, chọn nó trong demo với đúng cấu hình hoặc tự gọi pipeline rồi lưu đầu ra. Không được nói mỗi hàng CSV đồng nghĩa một PNG đã được xuất.

### 8.4. File tải từ demo nằm ở đâu?

Nút Streamlit tạo dữ liệu để trình duyệt tải xuống. Thư mục đích do trình duyệt/người dùng chọn, thường là Downloads nhưng có thể khác; code không đặt một đường dẫn tải cố định trong repo. Demo hiện cho tải `enhanced.png`, `boundary.png`, `mask.png` khi có mask và `sar_result.json`. Ảnh overlay được hiển thị nhưng chưa có nút tải riêng.

Khi tải nhiều lần, trình duyệt có thể thêm hậu tố vào tên file. Để so sánh, nên đặt lại tên theo ảnh và cấu hình, đồng thời giữ JSON tương ứng. Ví dụ `00013_lee5_clahe2_mask.png` đi với JSON của đúng lượt đó; không dùng JSON mặc định để giải thích PNG được tạo bằng ngưỡng thủ công.

### 8.5. Cách tự lưu một bộ ảnh kết quả vào repo

Đây là ví dụ học cách xuất một ảnh, chưa phải lời khẳng định chương trình đã tự xuất mọi ảnh. Chạy đoạn Python này từ gốc dự án nếu cần tạo bộ kết quả riêng. Nó chỉ ghi vào `results/manual_00013/`, không sửa dữ liệu gốc.

```python
import json
from pathlib import Path
import cv2
from src.pipeline import PipelineConfig, process_image
from src.utils import load_sar_image

source = "kaggle/data/Class_1/class_1_00013.jpg"
result = process_image(load_sar_image(source), PipelineConfig())
out = Path("results/manual_00013")
out.mkdir(parents=True, exist_ok=True)
for name in ["raw", "filtered", "enhanced", "boundary", "mask"]:
    if result[name] is not None:
        ok = cv2.imwrite(str(out / (name + ".png")), result[name])
        if not ok:
            raise OSError("Cannot write " + name)
payload = {"input": source, "config": result["config"],
           "stats": result["stats"], "metrics": result["metrics"]}
(out / "result.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
```

PNG giữ các giá trị ảnh đã xuất không qua nén mất mát kiểu JPEG. Điều đó không làm ảnh đã xử lý trở thành ground truth; nó chỉ tránh thêm một nguồn biến đổi do định dạng xuất. Mẫu code không tự xuất overlay màu để tránh nhầm thứ tự kênh RGB/BGR khi ghi bằng OpenCV; muốn thêm phải kiểm quy ước màu của hàm tạo overlay.

### 8.6. Bản đưa lên GitHub nằm ở đâu?

`results/` được Git bỏ qua vì có nhiều file tái tạo được, ngoại trừ file hướng dẫn. Vì thế người khác clone repo có thể chưa có CSV/PNG ở đó cho đến khi chạy thực nghiệm. Các CSV/JSON đã dùng trong báo cáo được đóng băng ở `docs/report/evidence/`, có tiền tố như `reproducible_dataset_per_image.csv`, `reproducible_manifest.json`, `verification_per_case.csv` và `checksums.json`.

Một số hình đưa vào báo cáo nằm ở `docs/report/assets/`. PDF báo cáo là `docs/report/BAO_CAO_BTL_XLA.pdf`; nguồn Word/LaTeX cùng thư mục. File được commit là bản được chọn lưu trong Git, không phải mọi đầu ra tạm trên máy. Cũng đừng gọi các thư mục cũ `results/tables`, `figures`, `edge_evaluation_output` là đầu ra hiện tại nếu chưa kiểm phiên bản.

### 8.7. Lệnh chạy và phạm vi của từng lệnh

```powershell
uv run streamlit run streamlit_app.py
uv run python -m src.verification
uv run python reproduce.py --workers 4
uv run python reproduce.py --samples-only
```

Lệnh demo cho tương tác một ảnh. Lệnh verification chạy kiểm chứng. Lệnh reproduce không có `--samples-only` chạy kiểm chứng, khảo sát mẫu và toàn tập rồi ghi manifest với phạm vi `full`. Lựa chọn `--samples-only` bỏ phần toàn tập và ghi phạm vi thiếu phần đó. Các lệnh thực nghiệm có thể ghi đè đầu ra cùng tên; lưu bản có nhãn/cấu hình/phiên bản rõ nếu cần so hai lần chạy.

**Câu hỏi phải trả lời:** Một ảnh PNG mới hơn CSV có chắc được tạo bằng cùng mã/cấu hình không? Không. Phải đối chiếu đầu vào, cấu hình JSON và manifest. Chỉ nhìn thời gian sửa file không đủ chứng minh cùng thí nghiệm.

## 9. Câu hỏi ôn tập có gợi ý trả lời cho TV4

**Câu 1 — Gradient là gì?** Cặp đạo hàm ngang/dọc. Magnitude đo mức thay đổi, hướng chỉ chiều thay đổi; cả hai không mang nhãn dầu.

**Câu 2 — Gx 300, Gy 300 cho magnitude bao nhiêu?** sqrt 180000≈424,264. Không ép thành 255 trước NMS nếu cần giữ quan hệ độ lớn.

**Câu 3 — Unsharp có thể làm nhiễu mạnh hơn vì sao?** Nhiễu cũng nằm trong phần khác giữa ảnh gốc và ảnh mờ; cộng lại phần đó có thể tăng nhiễu.

**Câu 4 — Laplacian sharpening khác LoG ở đâu?** Một bên tạo ảnh sắc hơn bằng cộng/trừ đạo hàm bậc hai; một bên tìm biên qua điểm đổi dấu của đáp ứng đã gắn Gaussian.

**Câu 5 — LoG đổi dấu rất nhỏ có đáng tin không?** Có thể do sai số số học. Code chặn trị tuyệt đối<1e−9 về 0 và yêu cầu chênh vượt ngưỡng để tránh nhận dao động rất nhỏ.

**Câu 6 — NMS so dọc đường biên hay theo gradient?** Theo gradient, tức thường vuông góc với đường biên. So sai hướng sẽ làm mảnh sai và giữ/loại sai điểm.

**Câu 7 — NMS dùng>=có hậu quả gì?** Plateau bằng nhau có thể giữ nhiều điểm; không bảo đảm mọi biên duy nhất 1 pixel.

**Câu 8 — Một điểm magnitude 60 với low 35, high 90 có được giữ không?** Nó là yếu; chỉ được giữ nếu nối 8 hướng tới điểm mạnh qua chuỗi hợp lệ. Nếu đứng riêng sẽ bị loại.

**Câu 9 — Vì sao BFS cần visited?** Để không đưa lại cùng điểm vào queue liên tục, bảo đảm mỗi điểm được xử lý có giới hạn và tránh vòng lặp trên đồ thị có chu trình.

**Câu 10 — Threshold Canny 90 có giống Otsu 90 không?** Không. Một bên áp lên magnitude gradient sau NMS, một bên lên mức xám của ảnh phân đoạn.

**Câu 11 — Otsu η 1 có nghĩa dầu đúng 100% không?** Không. Chỉ là tỷ lệ phương sai giữa lớp so với toàn ảnh; nhãn vật lý không tham gia công thức.

**Câu 12 — Tại sao Otsu 50 phải dùng<=?** Vì lớp tối bao gồm pixel bằng ngưỡng. Dùng<50 mất toàn bộ nhóm 50 trong ví dụ hai mức.

**Câu 13 — Khi nào pipeline có thể phân đoạn trên filtered?** Khi tỷ lệ tối enhanced>30% và reference<=30%, hoặc η_reference>η_enhanced+0,05. Đây là heuristic có giới hạn.

**Câu 14 — Manual threshold có đi qua giảm ngưỡng tự động không?** Không trong code hiện tại. Ảnh phân ngưỡng manual là enhanced; đo tương phản vẫn có thể dùng reference.

**Câu 15 — Đĩa r=2 có phải 25 ô foreground không?** Không. Khung 5×5 nhưng chỉ ô trong x²+y²<=4 được chọn. Hình kernel ảnh hưởng chi tiết bị giữ/xóa.

**Câu 16 — Opening và closing đổi chỗ được không?** Không; một cái co→giãn, một cái giãn→co, tác động khác. Một vùng bị co mất không tự được phục hồi bằng bước giãn sau.

**Câu 17 — Đặt closing_radius 0 có tắt mọi hình thái không?** Không; opening r=2 vẫn chạy. Closing 0 chỉ làm bước closing dùng kernel 1×1.

**Câu 18 — Hai pixel chạm chéo là một hay hai vùng?** Theo 8 là một; theo 4 là hai. Dự án dùng 8.

**Câu 19 — Nhãn custom 1 và library 7 có chứng minh khác vùng không?** Không. Nhãn là tên nhóm; so phân hoạch pixel, không so tên số nguyên đơn thuần.

**Câu 20 — C_R 0,2 có phải xác suất 20% dầu?** Không. Nó là tỷ lệ chênh mean nền/vùng theo công thức, không được hiệu chuẩn như xác suất.

**Câu 21 — Vùng 10000 pixel, C_R 0,05 có qua mặc định không?** Không, vì 0,05<0,10. Không có ngoại lệ cho vùng lớn.

**Câu 22 — Biên có thể bao quanh lỗ trong mask không?** Có. A−erode (A) đánh dấu những pixel bị co mất, gồm quanh lỗ nội bộ, không chỉ đường bao ngoài.

**Câu 23 — Tại sao không đo C_R trên CLAHE mặc định?** Ánh xạ cục bộ đã thay tương phản; dùng filtered làm tham chiếu giảm việc lấy hiệu ứng tăng cường làm bằng chứng cho chính vùng đó.

**Câu 24 — Không có ring thì nên tự gán C_R 1 không?** Không. Không có dữ liệu nền để đo; code bỏ vùng. Gán 1 sẽ tạo bằng chứng giả về tương phản.

**Câu 25 — Giảm số vùng sau morphology luôn là cải tiến?** Không. Nó có thể xóa nhiễu hoặc gộp/xóa vùng thật. Cần kiểm hình học và nhãn chuẩn nếu có.

## 10. Thực hành và trình bày của TV4

### 10.1. Các bài phải tự làm

**Bài A:** Tính Gx, Gy, magnitude cho ma trận Sobel 3×3 ở chương 3. Sau đó gọi `custom_sobel`, so Gx/Gy dạng float và magnitude dạng uint8; giải thích vì sao hai cách biểu diễn độ lớn khác nhau.

**Bài B:** Tạo ảnh hằng 127, chạy Canny với low=high=0. Kết quả phải rỗng. Tạo một đường chéo và giải thích nhóm hướng NMS bằng tọa độ hàng/cột thực tế.

**Bài C:** Tạo khối 4×4 giữa ảnh 8×8. Kiểm diện tích erosion 4, dilation 36, biên 12 với kernel 3×3. Dời khối sát mép và giải thích tác động của padding thay vì cho rằng đáp án giữa ảnh vẫn giữ nguyên.

**Bài D:** Tạo mask hai pixel chạm chéo; kiểm `find_connected_components`. Sau đó thử min_area lớn hơn diện tích và xem ba đầu ra để hiểu min_area lọc metadata chứ không sửa ảnh nhãn.

**Bài E:** Trên 00013 và Class_0_00001, thay từng min_area/min_contrast/closing_radius, lưu JSON và mask. Ghi cả vùng mất/gộp và lý do có thể gây false positive/negative. Không chọn chỉ cấu hình đẹp nhất để kết luận.

### 10.2. Kịch bản nói

Slide 9:25 giây giải thích làm nét và đạo hàm. Slide 10:40 giây cho Canny. Slide 11:30 giây cho Otsu. Slide 12:35 giây cho hình thái/liên thông. Slide 13:30 giây cho C_R và lọc vùng. Tổng 160 giây. Dùng một ví dụ nhỏ để làm rõ cơ chế thay vì đọc công thức dài không giải thích ký hiệu.

Trong 30 giây demo, đổi morphology→Canny→morphology trên cùng ảnh. Chỉ rõ trạng thái có mask và chỉ có biên; nếu đổi thêm tham số, chỉ đổi một giá trị và nói đánh đổi trước khi xem kết quả.

### 10.3. Tiêu chí hiểu sâu

Bạn phải lần theo được một vùng từ threshold tới mask cuối, tự tính được một phép erosion/dilation và một C_R, giải thích NMS/hysteresis bằng ví dụ, và nêu được ít nhất một phản ví dụ cho min_area, min_contrast và closing. Chỉ nhớ tên hàm hoặc nói “hình thái làm sạch ảnh” chưa đáp ứng mục tiêu học.
