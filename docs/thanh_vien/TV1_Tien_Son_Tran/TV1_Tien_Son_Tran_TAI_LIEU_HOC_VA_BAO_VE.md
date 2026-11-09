# TV1 — Tiến Sơn Trần — Sổ tay học và bảo vệ từ nền tảng

GitHub: `Maloque18705`. Trách nhiệm: Trưởng nhóm — tích hợp, Streamlit và báo cáo chung. Mã phụ trách: `src/tv1/, streamlit_app.py`.

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

## 3. Kiến trúc phần mềm: nối các phép toán thành một hệ thống

### 3.1. Module, hàm và trách nhiệm là gì?

Module là một file Python tập hợp các hàm có liên quan. Hàm là một thao tác nhận đầu vào và trả đầu ra. Ta chia module để mỗi phần có một trách nhiệm rõ: TV3 biến đổi cường độ, TV4 tìm biên/vùng, TV5 đo kết quả; TV1 nối các phần và cung cấp giao diện. Cách chia này giúp tìm lỗi theo vị trí, không phải đoán trong một file rất dài.

`src/tv3/filters.py` chứa triển khai thật. File `src/filters.py` chỉ chuyển tiếp import để mã cũ vẫn dùng được. Vì vậy nếu sửa `src/filters.py` bằng cách chép thêm một bản thuật toán, có thể tạo hai phiên bản khác nhau mà giao diện và thí nghiệm gọi khác chỗ. Trưởng nhóm phải biết đâu là nguồn triển khai duy nhất.

**Tình huống:** TV3 sửa Lee nhưng bảng thực nghiệm không đổi. Trước khi kết luận bộ lọc không tác dụng, kiểm tra file vừa sửa có được import thật không, process đã được khởi động lại chưa, và bảng đang xem thuộc lần chạy nào. Đây là lý do kiến trúc và nguồn dữ liệu quan trọng bằng công thức.

### 3.2. Pipeline là gì, vì sao không viết thuật toán ngay trong giao diện?

Pipeline là chuỗi xử lý có thứ tự và có các đầu ra trung gian. Hàm trung tâm ở đây là `process_image(image, config)`. Nó không cần biết Streamlit, HTTP hay nút bấm. Cùng một hàm được gọi từ demo và từ thí nghiệm, nhờ đó một cấu hình có cùng ý nghĩa ở hai nơi.

Nếu thuật toán nằm trực tiếp trong handler của một nút giao diện, chương trình batch có thể dùng một bản cũ khác. Khi đó slide, CSV và demo sẽ không nhất quán. Tách lõi khỏi giao diện cũng giúp thử một ma trận 5×5 mà không mở trình duyệt.

Hãy xem mỗi bước như một hợp đồng: đầu vào ảnh xám 2D, đầu ra đúng kích thước, ý nghĩa khóa rõ ràng. Không được tự đổi `mask` thành bản đồ biên chỉ vì cả hai đều có 0 và 255. Hai ma trận giống kiểu dữ liệu vẫn có thể khác ý nghĩa.

### 3.3. Theo dấu một ảnh qua từng biến

Giả sử người dùng chọn `class_1_00013.jpg`. Giao diện đọc byte, giải mã xám và chuẩn hóa kích thước demo 400×400. Sau đó `raw` nhận ảnh hợp lệ; Lee tạo `filtered`; CLAHE tạo `enhanced`. Nếu bật unsharp, `displayed` đổi; nếu không, `displayed` là bản sao của `enhanced`.

Nhánh morphology nhận `enhanced` và `reference_image=filtered`. Bên trong nhánh này, quy tắc có thể chuyển ảnh phân ngưỡng về reference nếu ảnh CLAHE không phù hợp theo các tiêu chí đã cài. Vì vậy sơ đồ Lee→ CLAHE →Otsu là mô tả tổng quát; giải thích sâu phải nhắc tới việc chọn ảnh phân ngưỡng và ảnh đo tương phản.

Cuối cùng `mask` dùng để đếm diện tích, `boundary` dùng để vẽ viền, `overlay` dùng để đặt viền lên ảnh gốc. `metrics` được tính giữa `raw` và `displayed`, nên khi bật làm nét một số chỉ số ảnh có thể đổi dù mask vẫn giữ nguyên. Đây là một câu hỏi vấn đáp dễ gây nhầm.

### 3.4. Bản đồ đầu ra phải thuộc lòng theo ý nghĩa

| Khóa | Nó là gì và dùng để làm gì |
| --- | --- |
| `raw`| Ảnh xám đầu vào sau kiểm tra; mốc so sánh |
| `filtered`| Ảnh giảm dao động; dùng làm tham chiếu trước CLAHE |
| `enhanced`| Ảnh tăng tương phản; có thể dùng phân ngưỡng |
| `displayed`| Ảnh để quan sát sau lựa chọn làm nét; ảnh được dùng cho nhóm metrics |
| `mask`| Vùng ứng viên đặc; None ở chế độ chỉ tìm biên |
| `boundary`| Pixel biên; không đồng nghĩa toàn bộ diện tích vùng |
| `overlay`| Hình màu giúp quan sát vị trí biên trên raw |
| `stats`| Đặc trưng vùng; rỗng khi không có phân đoạn vùng |
| `metrics`| Sáu chỉ số ảnh: ENL, SSI, RMS, entropy, AMBE, EPI |
| `config`| Bản mô tả tham số để người khác tái lập |

**Câu hỏi:** Nếu người xem thấy “số vùng=0” khi đang chọn Sobel, có nên hiển thị như một kết luận không có dầu? Không. Nhánh này không thực hiện quyết định vùng; thiết kế hiện tại trả stats rỗng để tránh diễn giải đó.

## 4. Cấu hình và giao diện: từ lựa chọn của người dùng đến phép tính

### 4.1. PipelineConfig và dataclass là gì?

`PipelineConfig` là một bản ghi tập hợp tham số. `dataclass` giúp tạo đối tượng dữ liệu mà không phải tự viết mọi phần khởi tạo. `frozen=True` ngăn gán lại trường của đối tượng sau khi tạo, nhằm giảm việc thay cấu hình giữa chừng mà không nhận ra. Nó không tự biến mọi mảng NumPy thành chỉ đọc và không tự kiểm chứng ý nghĩa toán học của tham số.

Các tên nên được truyền bằng từ khóa, ví dụ `PipelineConfig(filter_name="lee", min_area=300)`. Viết theo tên dễ đọc và an toàn hơn khi thêm trường. Giao diện hiện tại xây cấu hình theo thứ tự trường; nếu sửa dataclass cần kiểm tra lại chỗ tạo đối tượng, tránh đẩy nhầm giá trị sang trường kế tiếp.

### 4.2. Ý nghĩa những tham số phải giải thích được

`window_size=5` là chiều cửa sổ lọc, không phải số lần lọc. `num_looks=4` là L dùng trong ước lượng nhiễu của Lee/Kuan; với JPEG này ta không xác nhận đó là số look vật lý gốc. `clip_limit=2` điều khiển giới hạn histogram CLAHE, không chặn pixel ở mức sáng 2. `tile_grid=8` là 8×8 tile, không phải tile kích thước 8×8 pixel.

`min_area=300` loại vùng nhỏ hơn 300 pixel sau các bước hình thái. `min_contrast=0.10` đòi hỏi chênh lệch tương phản vùng/nền theo công thức C_R đạt mức tối thiểu. `closing_radius=4` tạo phần tử cấu trúc đĩa trong khung 9×9. `adaptive_otsu` bật quy tắc điều chỉnh ngưỡng khi vùng tối ban đầu quá rộng. `manual_threshold` thay ngưỡng tự động bằng ngưỡng người dùng.

Ngưỡng Canny là ngưỡng độ lớn gradient, không phải ngưỡng mức xám Otsu. Không thể dùng cùng một lời giải thích “pixel dưới 90 là dầu” cho cả hai. Thay tham số chỉ tác động phương pháp đang sử dụng nó; đổi L khi chọn median không có ý nghĩa như khi chọn Lee.

### 4.3. Streamlit chạy như thế nào?

Streamlit chạy file Python để tạo giao diện. Khi một widget thay đổi, script thường chạy lại từ trên xuống. Vì vậy biến được tạo trong lần chạy không tự là nơi lưu lâu dài. `st.sidebar` bố trí điều khiển, `st.selectbox` nhận lựa chọn, `st.image` trình bày ảnh và `st.download_button` cung cấp byte để trình duyệt tải xuống.

Mã hiện tại đọc ảnh, xử lý ảnh được chọn và vẽ kết quả trong lượt chạy. Nó không huấn luyện mô hình và không mặc nhiên chạy cả dataset khi đổi một slider. Các lựa chọn Kaggle liệt kê file trong Class_0 / Class_1 để người dùng có thể chọn bất kỳ ảnh nào.

**Điểm quan trọng:** Nếu có file upload, chương trình ưu tiên byte upload thay vì file đang chọn trong selectbox. Muốn quay lại ảnh Kaggle phải xóa upload. Nếu không biết quy tắc này, người trình bày có thể tưởng đổi tên ảnh nhưng hình không đổi do thuật toán bị lỗi.

### 4.4. Vì sao cần lưu cả cấu hình, không chỉ ảnh đẹp?

Hai ảnh kết quả khác nhau có thể do input khác, bộ lọc khác, ngưỡng khác hoặc phiên bản code khác. PNG một mình không nói được nguyên nhân. JSON từ demo lưu `config`, `metrics`, `stats` giúp biết các giá trị đã dùng. Khi so sánh, phải giữ các yếu tố còn lại cố định và thay đúng một biến.

Demo hiện có nút tải `enhanced.png`, `boundary.png`, `mask.png` khi có mask, và `sar_result.json`. `overlay` được hiển thị nhưng chưa có nút tải riêng trong mã hiện tại. Những file tải về do trình duyệt quyết định thư mục đích; không tự ghi vào `results/` của repo.

### 4.5. Bài thực hành có thể tự chạy

Từ gốc repo, mở Python sau khi cài môi trường và chạy đoạn sau. Mục đích là tách thuật toán khỏi UI để kiểm tra một tính chất của thiết kế.

```python
import numpy as np
from src.pipeline import PipelineConfig, process_image
from src.utils import load_sar_image
a = load_sar_image("kaggle/data/Class_1/class_1_00013.jpg")
r0 = process_image(a, PipelineConfig(sharpening_name="none"))
r1 = process_image(a, PipelineConfig(sharpening_name="unsharp"))
print(np.array_equal(r0["mask"], r1["mask"]))
```

Kết quả mong đợi là True vì nhánh phân đoạn tách khỏi sharpening. Hãy kiểm thêm `displayed` và các metrics: chúng có thể khác. Nếu mask khác, kiểm các tham số và code trước khi sửa đáp án mong đợi của bài thử.

## 5. Kiểm tra đầu vào và xử lý lỗi

### 5.1. Vì sao validation là một phần của thuật toán thực tế?

Công thức thường giả định ảnh có kích thước hợp lệ và giá trị hữu hạn. Phần mềm phải kiểm tra giả định ấy. Một mảng 3 chiều, ảnh rỗng hoặc chứa NaN có thể làm phép tính trả giá trị vô nghĩa mà không dừng đúng nơi gây lỗi. Báo lỗi sớm giúp người dùng biết phải sửa đầu vào, không nhận một mask tưởng là hợp lệ.

`gray_image` kiểm tra 2 chiều, không rỗng, mọi giá trị hữu hạn và trong [0,255], rồi đổi sang uint8. Hàm này không tự cân bằng sáng, không tự chuẩn hóa một ảnh 16 bit, và việc ép float sang uint8 có thể cắt phần thập phân. Không được quảng cáo nó là bộ nhập mọi loại ảnh khoa học.

`odd_window` từ chối cửa sổ âm, chẵn hoặc không nguyên. `positive` kiểm tra một số thực hữu hạn lớn hơn 0. Những kiểm tra này bảo vệ các trường hợp phổ biến; không có nghĩa toàn bộ tổ hợp tham số bất thường của mọi hàm trong dự án đều đã được chứng minh an toàn.

### 5.2. Lỗi đọc ảnh khác lỗi xử lý ảnh

File không tồn tại là lỗi đường dẫn. File có tồn tại nhưng không giải mã được là lỗi nội dung/định dạng. File đọc được nhưng shape không phù hợp là lỗi hợp đồng đầu vào. Bộ lọc chạy xong nhưng phát hiện nhầm là lỗi chất lượng phương pháp, không phải lỗi mở file. Trưởng nhóm cần phân loại được để giao đúng người xử lý.

Ví dụ `cv2.imdecode` có thể trả None khi byte không phải ảnh hợp lệ. Demo kiểm tra và hiển thị thông báo. Không nên chữa bằng cách biến None thành ảnh đen rồi tiếp tục: người dùng sẽ nhận một kết quả giả là đã xử lý ảnh của họ.

### 5.3. Resize, tọa độ và đơn vị

Demo dùng `INTER_AREA` khi resize; hàm `load_sar_image` dùng `INTER_LINEAR` nếu cần đổi kích thước. Dataset chính vốn 400×400 nên khác biệt này không ảnh hưởng lượt đánh giá hiện tại, nhưng ảnh upload kích thước khác có thể cho pixel đầu vào khác. Muốn so demo với batch trên ảnh ngoài dataset phải thống nhất bước đọc/resize.

Ngưỡng diện tích tính bằng pixel phụ thuộc độ phân giải. Một vùng hình học có thể thành 100 pixel sau thu nhỏ dù trước đó có 400 pixel. Không kết luận cùng min_area=300 áp dụng công bằng cho mọi kích thước ảnh. Hãy lưu kích thước thực sự đã xử lý cùng cấu hình khi mở rộng ứng dụng.

### 5.4. Mảng, bản sao và tác dụng phụ

Mảng NumPy là đối tượng có thể thay đổi. Nếu một hàm sửa ảnh đầu vào tại chỗ, bước sau hoặc ảnh gốc để đối chiếu có thể bị ảnh hưởng. Khi kiểm thử, có thể tạo `before = image.copy()`, gọi hàm rồi so `image` với `before`. Một số phép slice tạo view chia sẻ dữ liệu, không phải bản sao độc lập.

**Ví dụ suy luận:** Gán `b=a` không sao chép ảnh; sửa b có thể sửa a. Gán `b=a.copy()` tạo dữ liệu riêng. `frozen=True` của config không giải quyết việc alias mảng. Đây là hai khái niệm khác nhau.

## 6. Tích hợp, kiểm thử và tìm nguyên nhân sai

### 6.1. Unit test, integration test và kiểm tra ứng dụng

Unit test kiểm một phần nhỏ, ví dụ Sobel trên ma trận biết đáp án. Integration test kiểm sự nối các phần, ví dụ đổi sharpening không làm đổi mask. Kiểm tra ứng dụng dùng Streamlit AppTest để chạy file giao diện, đổi chế độ và kiểm kết quả. Cả ba đều hữu ích nhưng không thay thế nhau.

Một hàm lọc đúng không ngăn giao diện truyền sai tham số. Một demo mở thành công không chứng minh phép toán đúng. Một ảnh 00013 hợp lý không chứng minh không có false positive trên Class_0. Vì vậy trưởng nhóm cần nói rõ một lần kiểm chứng bảo vệ điều gì.

### 6.2. Quy trình tìm lỗi theo ảnh trung gian

Nếu kết quả có nhiều vùng lạ, trước tiên ghi input và config; mở raw để chắc đúng ảnh; xem filtered để đánh giá lọc; xem enhanced để thấy tác động CLAHE; kiểm ngưỡng và ảnh phân ngưỡng; xem mask trước/sau hình thái nếu đang phân tích bằng mã; cuối cùng xem điều kiện area/contrast. Mỗi bước phải trả lời: hiện tượng bắt đầu từ đâu?

Đừng tăng tất cả slider cùng lúc để làm ảnh đẹp rồi gọi là đã sửa lỗi. Cách đó phá khả năng biết nguyên nhân. Một sửa hợp lý phải có ca tái hiện, giải thích thay đổi, kiểm tra lại ca đó và kiểm các tính chất liên quan không bị hỏng.

### 6.3. Thêm một phương pháp đúng cách

Cần có hàm lõi với input / output rõ ràng, thêm tên vào danh sách phương pháp, thêm lựa chọn gọi trong pipeline, làm đối chiếu thư viện hoặc giải thích không có API trực tiếp, rồi cập nhật tài liệu và ca thử phù hợp. Không chỉ thêm một nhãn vào selectbox.

Nếu thay mã trong `src/`, số liệu cũ không tự thành số liệu của thuật toán mới. Hash nguồn sẽ đổi; phải chạy lại thực nghiệm và dựng lại báo cáo khi sử dụng số mới. Chỉ sửa tài liệu học không làm thuật toán thay đổi, nên không cần chạy toàn dataset chỉ để đổi chữ trong PDF.

### 6.4. Hiệu năng phải được giải thích theo phạm vi

UI xử lý một ảnh, còn batch xử lý nhiều ảnh bằng nhiều process. Thời gian đo gồm đọc ảnh và pipeline trong hàm đánh giá, không chỉ Lee. Lần chạy song song có tranh chấp CPU /bộ nhớ; không đem số đó so trực tiếp với một benchmark đơn luồng rồi kết luận tối ưu hơn bao nhiêu lần.

Tối ưu trước hết phải giữ cùng kết quả trong phạm vi đã kiểm. Vector hóa giảm vòng lặp Python nhưng có thể tạo mảng trung gian rất lớn, ví dụ cửa sổ H×W×k×k. Không thể nói “dùng NumPy thì luôn ít RAM”.

## 7. Vai trò trưởng nhóm trong báo cáo và bảo vệ

### 7.1. Báo cáo phải nối được mục tiêu, phép toán và bằng chứng

Một luận điểm tốt có chuỗi: muốn cải thiện điều gì → chọn phép toán vì cơ chế nào → cài ở đâu → kiểm đúng công thức bằng cách nào → kết quả trên nhiều ảnh ra sao → giới hạn còn gì. Nếu chỉ có công thức ở chương 2 và ảnh đẹp ở chương 4 nhưng không nối chúng, người nghe không biết đóng góp của nhóm.

Nguồn chính của báo cáo hiện tại là `docs/report/`; những file tổng quan cũ chỉ là tham khảo lịch sử. PDF 42 trang và slide 18 trang đã có trong repo, nhưng số trang không chứng minh nhóm đã hiểu hoặc mọi yêu cầu hành chính đã hoàn tất. MSSV, chữ ký, đánh giá thật và video còn là phần cần nhóm xử lý theo kế hoạch.

### 7.2. Git, phân công và bằng chứng đóng góp

Commit ghi một trạng thái thay đổi cùng metadata. Tài khoản có quyền collaborator chỉ chứng minh quyền truy cập hiện tại; nó không chứng minh người đó đã viết một phần mã trong quá khứ. Vai trò TV1–TV5 là phân công trách nhiệm học và thực hiện hiện tại.

Nhật ký hồi cứu có thể tập hợp file gốc, chat, bản nháp hoặc commit thật. Phải ghi ngày bổ sung thật. Không gán tác giả hoặc ngày giả để biến bảng mới lập thành lịch sử tám tuần. Số commit cũng không tự là tỷ lệ đóng góp: một commit sửa nhiều lỗi có thể quan trọng hơn nhiều commit chỉnh chữ.

### 7.3. Điều phối câu hỏi chéo

Trưởng nhóm cần biết đủ cơ chế Lee/ CLAHE, Canny/hình thái và các chỉ số để không chỉ nói “phần này bạn khác làm”. Có thể nhờ người phụ trách bổ sung chi tiết sau khi tự trả lời ý chính. Tập bảo vệ bằng cách đổi người trình bày một đoạn code, rồi yêu cầu người nghe nêu một trường hợp phương pháp thất bại.

**Mức đạt:** Bạn phải tự mở repo, chạy demo, truy được từ widget tới hàm lõi, tìm được CSV thực nghiệm và giải thích vì sao một ví dụ không đủ chứng minh nhận diện dầu. Nếu chỉ đọc được tên module thì chưa đạt.

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

## 9. Câu hỏi ôn tập có gợi ý trả lời cho TV1

### 9.1. Câu hỏi nền tảng và kiến trúc

**Câu 1 — Ảnh xám uint8 400×400 chứa bao nhiêu phần tử?** 160.000. Dữ liệu mảng raw khoảng 160.000 byte, chưa tính đối tượng Python hoặc ảnh màu trung gian. float64 cần 8 byte mỗi phần tử, nên cùng kích thước có bộ nhớ dữ liệu lớn hơn tám lần.

**Câu 2 — Vì sao không gọi hàm thư viện trực tiếp ngay trong nút bấm?** Tách pipeline giúp demo và batch gọi cùng triển khai, kiểm thử không cần trình duyệt, và giữ thuật toán lõi đúng yêu cầu tự cài. Thư viện vẫn có vai trò I/O và đối chứng.

**Câu 3 — `None` ở mask có giống mask toàn 0 không?** Không. None nghĩa nhánh hiện tại không tạo phân đoạn vùng; mask toàn 0 nghĩa đã thực hiện phân đoạn nhưng không giữ pixel nào. Hai trạng thái phải được trình bày khác nhau.

**Câu 4 — Đổi sharpen làm metrics đổi nhưng area không đổi có mâu thuẫn không?** Không. Metrics dùng displayed; area tính trên mask từ nhánh trước sharpen. Hai đại lượng mô tả hai đầu ra khác nhau.

**Câu 5 — Tại sao raw vẫn cần giữ lại?** Nó là mốc đối chiếu không tăng cường, nền overlay và đầu vào của các chỉ số so sánh. Nếu ghi đè raw bằng enhanced, không còn cơ sở thấy chương trình đã thay đổi ảnh ra sao.

**Câu 6 — `frozen=True` có làm pipeline thuần hàm tuyệt đối không?** Không. Nó ngăn gán trường config; không ngăn sửa mảng, đọc file hay mọi tác dụng phụ. Tính chất của hàm cần được kiểm tra riêng.

### 9.2. Tình huống thao tác và tìm lỗi

**Câu 7 — Chọn Class_0 nhưng ảnh vẫn là ảnh upload, có phải lỗi dữ liệu?** Trước hết kiểm upload còn tồn tại không. Mã ưu tiên upload. Xóa upload rồi chọn lại trước khi kết luận có lỗi.

**Câu 8 — Đầu ra của demo khác batch trên ảnh lớn có thể do đâu?** Kiểm bộ đọc, chuyển xám, resize, tham số và phiên bản. INTER_AREA và INTER_LINEAR có thể tạo ảnh đầu vào khác; dataset 400×400 không đại diện tình huống resize khác kích thước.

**Câu 9 — Cửa sổ 4×4 sao bị từ chối?** Thiết kế bộ lọc này dùng một ô tâm và bán kính nguyên đối xứng. Chẵn không đáp ứng hợp đồng đang cài; không phải mọi bộ lọc trong toàn bộ xử lý ảnh đều cấm kernel chẵn.

**Câu 10 — Ảnh hằng phải có Canny rỗng, vì sao?** Không có thay đổi cường độ nên gradient bằng 0. Nếu ngưỡng 0 vô tình giữ mọi pixel, cần kiểm điều kiện magnitude>0 chứ không chỉ >=threshold.

**Câu 11 — Bảng CSV cũ vẫn mở được sau khi sửa mã, có dùng báo cáo được không?** Chỉ khi chứng minh nó ứng với phiên bản cần báo cáo. Manifest và source hash giúp phát hiện lệch; việc file tồn tại không có nghĩa file còn đại diện mã mới.

**Câu 12 — Nút tải PNG có lưu vào results không?** Không trong demo hiện tại. Nó gửi byte cho trình duyệt; thư mục đích do trình duyệt/người dùng quyết định. Batch mới ghi các đường dẫn results được định nghĩa trong code.

### 9.3. Câu hỏi chéo và câu hỏi khó

**Câu 13 — Lee thích nghi có phải ML?** Không; trọng số tính theo công thức từ thống kê cửa sổ ảnh hiện tại. Không có mô hình học từ nhãn. Muốn trả lời sâu, nêu được K=clip(1−μ²/(L×v),0,1) với bảo vệ mẫu số.

**Câu 14 — CLAHE có thể làm biên nhiễu mạnh hơn không?** Có. Nó khuếch đại tương phản cục bộ còn sót; đầu ra đẹp hơn cho mắt không đồng nghĩa đúng nhãn hơn.

**Câu 15 — C_R có phải độ tròn không?** Không. Trong repo C_R=(μ_nền−μ_vùng)/μ_nền, có điều kiện bảo vệ nền gần 0. Độ tròn là đặc trưng hình học khác, không được thay thế định nghĩa.

**Câu 16 — Precision thấp có chứng minh mã NumPy sai không?** Không trực tiếp. Có thể công thức cài đúng nhưng quy tắc vùng tối không phân biệt dầu/ lookalike tốt. Phải tách correctness của phép toán khỏi chất lượng ứng dụng.

**Câu 17 — Nếu bỏ CLAHE mà mask không đổi, có thể xóa CLAHE khỏi bài không?** Chưa kết luận từ một ảnh. Cần xem nhánh chọn ảnh phân đoạn và vai trò tăng cường quan sát, rồi khảo sát có/không trên nhiều ảnh. Một bước có thể phục vụ quan sát mà không đổi quyết định ở ca cụ thể.

**Câu 18 — Tại sao không chia mỗi người 20% theo folder?** Folder là phân công, không phải đo công sức thực tế. Đánh giá cần sản phẩm, minh chứng, nhận xét của nhóm và quy định môn học.

**Câu 19 — 558 PASS có bao gồm 36 DESCRIPTIVE không?** Không. Có 594 đối chiếu, gồm 558 PASS và 36 so sánh biến thể chưa áp tiêu chí tương đương. Nói “594 ca đều đạt” làm mất khác biệt quan trọng.

**Câu 20 — Cách bảo vệ trung thực khi bị hỏi hệ thống có dùng được ngoài thực tế không?** Nêu đã cài và kiểm chứng xử lý ảnh, đã đánh giá toàn bộ ảnh cục bộ, nhưng FP cao, thiếu mask chuẩn và thông tin cảnh; chưa có cơ sở khẳng định triển khai đáng tin cậy.

## 10. Bài thực hành và kịch bản trình bày của TV1

### 10.1. Bốn bài phải tự hoàn thành

**Bài A — Tái tạo không cần UI.** Gọi `process_image` bằng Python với ảnh 00013; in shape/dtype của các đầu ra. Giải thích vì sao overlay có kênh màu còn mask không có. Đạt khi bạn không nhầm `stats` với `metrics`.

**Bài B — Kiểm bất biến.** Dùng đoạn so mask khi đổi unsharp ở chương 4. Ghi kết quả True và chỉ ra hai dòng code khiến bất biến này đúng. Nếu tự đổi pipeline, bài thử phải phát hiện việc vô tình đưa displayed vào segmentation.

**Bài C — Tái hiện một lỗi đầu vào.** Thử mảng 3D, mảng chứa NaN và cửa sổ 4. Ghi thông báo lỗi thực tế và giải thích giả định bị vi phạm. Không sửa hàm để nuốt lỗi.

**Bài D — Dẫn giải một false positive.** Mở Class_0 `class_0_00001.jpg`, giữ cấu hình mặc định và mô tả từng bước tới vùng được giữ. Kết luận đó là ứng viên bị báo nhầm theo nhãn thư mục, không đổi nhãn để bảo vệ thuật toán.

### 10.2. Trình bày theo slide và chuyển lời

Slide 1/2/3 mỗi slide 20 giây: giới thiệu bài toán, đầu ra có giới hạn và năm người. Slide 6 trong 40 giây: giải thích các nhánh raw/filtered/enhanced/displayed, tại sao tách hiển thị khỏi phân đoạn. Slide 18 trong 30 giây: tổng kết theo bằng chứng và hướng cải tiến vẫn là xử lý ảnh. Tổng 130 giây, không tính phần demo.

Trong demo 180 giây, TV1 dùng khoảng 90 giây để mở ứng dụng, chọn đúng nguồn ảnh, điều phối người giải thích và tải JSON / PNG hiện có. TV3 giải thích Lee– CLAHE, TV4 đổi Canny/morphology, TV5 nêu số liệu và ca sai. TV2 theo dõi tính nhất quán với bảng đối chiếu. Mọi người phải sẵn sàng thay vai khi giảng viên chỉ định.

### 10.3. Cách tự chấm mức hiểu

Mức 1: đọc được tên và chạy được lệnh. Mức 2: giải thích được input / output và thông số. Mức 3: tính ví dụ và dự đoán điều gì đổi khi thay một tham số. Mức 4: chỉ ra phản ví dụ, giới hạn và bằng chứng kiểm chứng. Trưởng nhóm cần đạt mức 4 ở kiến trúc/tích hợp và ít nhất mức 3 ở phần của các bạn khác.

Tự ghi những câu chưa trả lời được vào nhật ký học thật. Tài liệu này không chứng nhận bạn đã hiểu chỉ vì đã tải PDF.
