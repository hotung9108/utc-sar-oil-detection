# TV3 — Hồ Việt Tùng — Sổ tay học và bảo vệ từ nền tảng

GitHub: `hotung9108`. Trách nhiệm: Lọc ảnh và tăng cường tương phản. Mã phụ trách: `src/tv3/`.

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

## 3. Bốn bộ lọc không gian: hiểu phép tính trước khi chọn tên

### 3.1. Box filter: thay pixel bằng trung bình lân cận

Box filter dùng trọng số bằng nhau trong cửa sổ. Với k×k pixel, đầu ra là tổng cửa sổ chia k². Nó làm giảm dao động ngẫu nhiên khi các pixel lân cận phản ánh cùng một vùng, nhưng cũng trộn cường độ ở hai phía đường biên. Đó là đánh đổi giữa làm mượt và giữ chi tiết.

Ví dụ cửa sổ có tám ô 100 và tâm 200 cho mean 111,11; sau round là 111. Nếu điểm 200 là nhiễu, đây có thể là tác dụng mong muốn. Nếu đó là một mục tiêu nhỏ thật, lọc đã làm suy yếu mục tiêu. Mục đích không quyết định bản chất của từng pixel; bộ lọc chỉ thực hiện phép toán đã chọn.

Trong `_box_filter_2d`, ảnh tích lũy lưu tổng từ gốc tới từng vị trí. Tổng hình chữ nhật tính bằng bốn giá trị D+A−B−C, tránh cộng lại k² phần tử ở mỗi pixel. Sau khi dựng bảng tích lũy, mỗi tổng cửa sổ có chi phí hằng số; không được nói toàn thuật toán có độ phức tạp O(1), vì vẫn phải đọc và xử lý toàn ảnh, xấp xỉ O (HW) với padding phù hợp.

**Tại sao cần float?** Tổng nhiều pixel và bình phương cường độ dùng ở Lee có thể vượt 255. Tích lũy trong uint8 sẽ không biểu diễn được các tổng ấy đúng cách.

### 3.2. Gaussian: láng giềng gần có trọng số lớn hơn

Gaussian dùng trọng số exp(−x²/(2 σ²)) cho khoảng cách 1 chiều, sau đó chuẩn hóa để tổng bằng 1. Với cửa sổ 3 và σ=1, các trọng số gần [0,274; 0,452; 0,274]. Pixel giữa có trọng số lớn hơn hai bên; so với box, sự thay đổi trọng số mềm hơn.

Trong hai chiều, kernel Gaussian hình vuông là tích của hai kernel 1D. Vì vậy code lọc theo hàng rồi theo cột, gọi là tính tách được. Thay vì khoảng k² phép nhân mỗi pixel, hai lượt dùng khoảng 2 k. Đây là lý do thuật toán nhanh hơn cách duyệt mọi ô kernel 2D, với cùng kernel tách được đã chuẩn hóa.

σ lớn hơn thường trải trọng số rộng hơn, nhưng nếu cửa sổ vẫn rất nhỏ thì phần đuôi Gaussian bị cắt. Không nói tăng σ vô hạn trong kernel 3×3 sẽ tương đương dùng một Gaussian rộng trên toàn ảnh. Muốn khảo sát phải ghi cả window và sigma.

**Hỏi:** Vì sao ảnh hằng phải giữ nguyên qua Gaussian đã chuẩn hóa? Vì tổng trọng số bằng 1, nên C×tổng_trọng_số=C; sai ở mép có thể do padding hoặc lượng tử hóa.

### 3.3. Median: chọn giá trị giữa, không lấy trung bình

Median sắp thứ tự các giá trị trong cửa sổ và lấy trung vị. Với tám số 100 và một số 200, giá trị giữa là 100. Nó bền hơn trung bình trước một số giá trị cực đoan, nên hữu ích với nhiễu xung. Tuy nhiên nó có thể xóa chi tiết thật mảnh hoặc nhỏ hơn cửa sổ.

Median là phép phi tuyến: median của tổng hai ảnh không nhất thiết bằng tổng hai median. Nó không được biểu diễn bằng một kernel trọng số cố định như box. Trong code, `sliding_window_view` tạo cách nhìn các cửa sổ, rồi `np.median` tính theo hai trục cửa sổ.

**Tại sao vẫn phải quan tâm RAM?** View không sao chép ngay toàn bộ pixel, nhưng các phép tiếp theo và xử lý thống kê có thể tạo dữ liệu trung gian. Cửa sổ lớn làm khối tính toán tăng nhanh; vector hóa không tự đảm bảo ít bộ nhớ.

### 3.4. Bilateral: gần vị trí và gần cường độ mới được trộn mạnh

Bilateral nhân hai trọng số. Trọng số không gian giảm theo khoảng cách pixel; trọng số cường độ giảm theo chênh lệch mức xám so với tâm. Đầu ra là tổng có trọng số chia tổng trọng số, để vẫn nằm trong thang đo hợp lý.

```text
w_space = exp(-distance^2 / (2*sigma_s^2))
w_range = exp(-(neighbor-center)^2 / (2*sigma_r^2))
w = w_space * w_range
output = sum(w * neighbor) / sum(w)
```

Với tâm 100, sigma_r=25, hàng xóm 102 có w_range≈0,9968, hàng xóm 200 có w_range≈0,000335. Nếu cùng khoảng cách không gian, pixel 200 được trộn rất ít hơn, nên biên sáng–tối có thể giữ tốt hơn Gaussian. Đây là cơ chế “giữ biên”, không phải bảo đảm nhận ra biên dầu thật.

sigma_r rất lớn khiến chênh lệch cường độ ít bị phạt; bilateral gần với lọc không gian hơn. sigma_r rất nhỏ giữ pixel khác tâm rất yếu, có thể giữ cả nhiễu. Bản custom dùng cửa sổ vuông; đối chứng OpenCV là biến thể có footprint khác, nên kết quả được đánh dấu DESCRIPTIVE.

## 4. Lee, Kuan và Frost: thích nghi với thống kê cục bộ

### 4.1. Lee là gì, dùng để làm gì?

Lee là bộ lọc ước lượng cường độ dựa trên mean và variance trong cửa sổ. Ý tưởng là trộn mean cục bộ với pixel gốc: nếu dao động quan sát chủ yếu được giải thích bởi nhiễu theo mô hình, kéo pixel về mean; nếu còn biến thiên đáng kể, giữ lại nhiều hơn giá trị gốc.

Trong code, μ là mean, v=max (E[I²]−μ²,0), L là `num_looks`, noise_var=μ²/L. Trọng số K bị chặn trong [0,1], rồi đầu ra bằng μ+K×(I−μ). K=0 cho mean; K=1 cho pixel gốc. Phần bảo vệ mẫu số nhỏ tránh chia 0.

```text
noise_var = mu^2 / L
K = clip(1 - noise_var / max(v, epsilon), 0, 1)
filtered = mu + K * (input - mu)
```

Đây là công thức triển khai của dự án, không phải khẳng định mọi phần mềm gọi “Lee” đều có cùng bước ước lượng nhiễu. Nên đọc `custom_lee_filter` để giải thích đúng biến thể đang bảo vệ.

### 4.2. Ví dụ Lee chi tiết và ảnh hưởng của L

Cửa sổ 3×3 có tám 100 và tâm 200: μ=1000/9≈111,111; E[I²]=120000/9; v=80000/81≈987,654. L=4 cho noise_var≈3086,420, nên K=0 và đầu ra tâm 111. Kết quả này được kiểm trong ví dụ số thật của repo.

Ví dụ thống kê minh họa khác: giả sử một cửa sổ có μ=100, v=10000, L=4 và pixel đang xét 200. noise_var=2500, K=0,75; đầu ra 100+0,75×100=175. Khi v tăng tương đối so với nhiễu ước lượng, bộ lọc giữ nhiều pixel gốc hơn.

Giữ μ, v cố định, tăng L làm μ²/L nhỏ đi, thường làm K lớn hơn và giảm mức kéo về mean. Vì vậy nói “tăng L thì luôn làm mượt hơn” là ngược với công thức đang cài. Với JPEG này, L là tham số mô hình được đặt, chưa được xác nhận là số look vật lý của dữ liệu gốc.

### 4.3. Kuan khác Lee ở đâu?

Kuan cũng phối hợp mean và pixel gốc nhưng dùng hệ số biến thiên. Code đặt Cu²=1/L, Ci²=v/max (μ², epsilon); W=clip((1−Cu²/max (Ci², epsilon))/(1+Cu²),0,1). Đầu ra là μ+W×(I−μ).

Với ví dụ μ=100, v=10000, L=4, ta có Ci²=1, Cu²=0,25; W=(1−0,25)/1,25=0,6. Pixel 200 thành 160, khác Lee 175. Khác biệt mẫu số 1+Cu² làm mức giữ chi tiết khác, dù hai bộ lọc cùng dùng moment cục bộ.

**Tại sao tồn tại nhiều bộ lọc?** Chúng biểu diễn các giả định/ước lượng và đánh đổi khác nhau. Tên “thích nghi” không nói một phương pháp luôn tốt nhất; phải so trên cùng input và nêu tiêu chí.

### 4.4. Frost trong repo là biến thể trọng số mũ

Code Frost tính hệ số biến thiên CV =σ/max (μ, epsilon). Với damping=d, khoảng cách không gian r, trọng số là exp(−d× CV ×r), rồi chuẩn hóa trong cửa sổ. Vùng có CV nhỏ có trọng số trải rộng hơn; vùng biến thiên mạnh có trọng số suy giảm theo khoảng cách nhanh hơn.

Ví dụ CV =1, d=2: tâm có trọng số chưa chuẩn hóa 1; pixel cách 1 có e^(−2)≈0,1353; cách 2 có e^(−4)≈0,0183. Sau chuẩn hóa, pixel gần tâm giữ vai trò lớn hơn. Đây là một biến thể dùng CV đúng như code, không tự đồng nhất với mọi công thức Frost khác có thể dùng CV ² hoặc ước lượng khác.

Damping lớn có thể giữ gần tâm nhiều hơn, nghĩa là có thể giữ cả nhiễu ở tâm. Không nói tham số lớn luôn khử nhiễu mạnh hơn. Nếu so tham chiếu, phải dùng cùng công thức trọng số và cùng cửa sổ.

### 4.5. Vì sao cả ba vẫn có thể làm sai mục tiêu ứng dụng?

Mean/ variance không gắn nhãn vật lý cho pixel. Vùng có biên thật và vùng có nhiễu mạnh đều có thể cho variance lớn. Một vệt nhỏ bị trộn vào nền có thể mất sau lọc, còn một vùng lookalike lớn vẫn tồn tại. Bộ lọc giảm dao động không tự giải quyết việc phân biệt dầu.

**Bài suy luận:** Tạo một dải tối rộng 1 pixel trên nền sáng rồi tăng window 3→9. Dự đoán tín hiệu dải sẽ yếu đi ở nhiều bộ lọc; kiểm bằng lát cắt ngang. Đừng chỉ xem thumbnail vì mắt dễ bỏ qua sự mất chi tiết mảnh.

## 5. Log, HE và CLAHE: tăng tương phản không phải tạo thông tin vật lý

### 5.1. Biến đổi log là gì?

Log là phép đổi từng pixel theo s=c× log (1+r). Dấu +1 giúp r=0 có giá trị hữu hạn. Khi c tự động, code chọn c=255/ log (1+max (r_max,1)). Hàm log tăng nhanh tương đối ở vùng nhỏ rồi chậm dần, nên có thể làm vùng tối dễ phân biệt hơn và nén vùng sáng.

Đây là phép biến đổi điểm: một pixel không cần nhìn hàng xóm để tính output, ngoài việc dùng r_max của toàn ảnh khi c tự chọn. Nó không phải bộ lọc speckle. Nếu nhiễu nằm trong vùng tối, log có thể làm nhiễu dễ thấy hơn cùng với tín hiệu.

### 5.2. HE: CDF tạo ánh xạ toàn ảnh

HE đếm histogram, cộng dồn thành CDF rồi tạo LUT. Với code hiện tại, s=round((CDF (r)−CDF_min)/(N−CDF_min)×255). Ảnh hằng có nhánh riêng giữ nguyên. Vì cùng một LUT dùng toàn ảnh, cùng mức r luôn cho cùng mức s bất kể vị trí.

Ví dụ bốn mức 0,1,2,3 có số lượng bằng nhau cho LUT [0,85,170,255]. HE mở rộng khoảng sử dụng mức xám, nhưng không bảo đảm histogram đầu ra phẳng hoàn toàn vì dữ liệu rời rạc và nhiều pixel phải cùng ánh xạ. Nó cũng có thể thay đổi độ sáng trung bình.

**Tại sao HE có hạn chế?** Nếu hai vùng có ánh sáng nền khác nhau, một ánh xạ toàn cục có thể không làm rõ chi tiết của cả hai. Những phần chiếm nhiều pixel có ảnh hưởng lớn lên histogram; chi tiết nhỏ có thể không được cải thiện như mong muốn.

