# TV2 — Lương Tiến Dũng — Sổ tay học và bảo vệ từ nền tảng

GitHub: `ltdungg`. Trách nhiệm: Lý thuyết, ví dụ số và đối chiếu thư viện. Mã phụ trách: `src/tv2/`.

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

## 3. Kiểm chứng là gì và đang kiểm chứng điều gì?

### 3.1. Ba câu hỏi khác nhau: chạy được, tính đúng, giải quyết tốt

“Chạy được” nghĩa chương trình kết thúc mà không báo lỗi. “Tính đúng” nghĩa đầu ra đáp ứng định nghĩa toán học và quy ước đã chọn. “Giải quyết tốt” nghĩa kết quả có ích cho bài toán trên dữ liệu thực tế. Ba câu không tương đương: code có thể chạy nhưng sai padding; code đúng phép Otsu nhưng vẫn nhận nhầm nền tối là dầu.

Vai trò TV2 tập trung vào tính đúng của triển khai và độ tin cậy của bằng chứng. Bạn phải nêu rõ phép đối chiếu đang kiểm cái gì. So custom Gaussian với OpenCV không trả lời trực tiếp câu hỏi “ảnh này có dầu không”. Nó trả lời liệu bộ lọc tự cài có gần kết quả tham chiếu dưới cùng cấu hình hay không.

### 3.2. Oracle: đáp án để so đến từ đâu?

Oracle là nguồn đáp án kỳ vọng trong kiểm thử. Một ví dụ tính tay nhỏ có thể là oracle độc lập. Một hàm thư viện đáng tin cậy cũng có thể là tham chiếu, nhưng phải kiểm tra hai bên có cùng tham số, kiểu dữ liệu và quy tắc biên. Không được gọi chính hàm custom để tạo expected rồi so custom với expected: nếu cả hai cùng sai thì vẫn “đạt”.

Trong `src/tv2/verification.py`, expected của năm ví dụ là hằng số đã tính trước; actual lấy từ hàm triển khai. Đây là lý do phải hiểu phép tính trên giấy, không chỉ chạy script nhìn chữ PASS.

### 3.3. Ba loại đối chiếu trong registry

**Direct**: có API thư viện tương ứng, ví dụ median, HE, CLAHE. Vẫn cần khớp định nghĩa; tên giống nhau chưa đủ. Ví dụ CLAHE cần cùng số tile, clip, padding và quy tắc làm tròn.

**Composition**: không giả định có API chuẩn trực tiếp cho thuật toán đang dùng. Ta ghép các primitive thư viện như lọc trung bình hoặc FFT vào công thức đã chọn. Lee đối chiếu moment cục bộ từ SciPy rồi dùng công thức Lee; điều này kiểm cách tính moment và phép kết hợp, nhưng hai bên có thể chia sẻ cùng giả định sai về mô hình.

**Variant**: hai cài đặt khác biến thể hoặc rời rạc hóa nên chỉ mô tả sai khác. Bilateral tự cài dùng cửa sổ vuông trong khi tham chiếu OpenCV có footprint khác; Canny có khác biệt ở các bước làm mịn/NMS/quy ước. Không áp một ngưỡng tương đương giả rồi gọi tất cả PASS.

**Câu hỏi:** Vì sao 36 DESCRIPTIVE không được cộng vào 558 PASS? Vì DESCRIPTIVE chưa phải kết luận đáp ứng một tiêu chí tương đương. Nó là thông tin so sánh có giới hạn, không phải thất bại mặc định và cũng không phải thành công mặc định.

### 3.4. Sai số tuyệt đối, MAE, MSE và tỷ lệ trùng

Cho hai đầu ra x và y cùng kích thước. Delta=x−y; max_abs_error là giá trị lớn nhất của |delta|; MAE là trung bình |delta|; MSE là trung bình delta². Tỷ lệ trùng đếm phần tử bằng nhau chính xác. Mỗi chỉ số nhấn mạnh một kiểu sai khác.

Ví dụ x=[0,0,0,100], y=[0,0,0,90]. Delta=[0,0,0,10]; max error=10; MAE=2,5; MSE=25; tỷ lệ trùng=75%. MSE không bằng MAE và có đơn vị bình phương mức xám. Nếu chỉ nhìn trung bình trên một ảnh lớn, một điểm sai lớn có thể bị pha loãng; max error giúp thấy điểm đó.

Ngược lại, nếu mọi pixel lệch đúng 1 mức xám, tỷ lệ trùng có thể là 0% nhưng sai số vẫn chỉ 1. Tùy quy ước lượng tử hóa, điều đó có thể nằm trong tolerance đã đặt. Không chọn chỉ số chỉ vì nó làm bản cài trông tốt hơn.

## 4. Năm ví dụ tính tay phải hiểu từ đầu đến cuối

### 4.1. HE 4×4: histogram thành bảng ánh xạ

Xét ảnh có bốn mức 0,1,2,3; mỗi mức xuất hiện bốn lần. Tổng N=16. Histogram tại bốn mức là [4,4,4,4], CDF là [4,8,12,16]. Phiên bản HE đang cài trừ CDF dương đầu tiên bằng 4, rồi chia N−CDF_min=12 và nhân 255.

```text
LUT(0) = round((4 - 4) / 12 * 255) = 0
LUT(1) = round((8 - 4) / 12 * 255) = 85
LUT(2) = round((12 - 4) / 12 * 255) = 170
LUT(3) = round((16 - 4) / 12 * 255) = 255
```

LUT là bảng tra: pixel đầu vào 2 được thay bằng 170. Không cần tìm lại histogram cho từng pixel. Mục đích là trải các mức đang dùng ra dải sáng rộng hơn. Ảnh hằng là trường hợp riêng; chương trình giữ nguyên để tránh mẫu số bằng 0 và tránh tạo tương phản giả.

**Hỏi sâu:** Vì sao công thức HE cơ bản trong sách đôi khi không trừ CDF_min? Có nhiều quy ước ánh xạ. Kiểm chứng phải bám đúng biến thể đã cài; không trộn một công thức với expected của công thức khác.

### 4.2. Lee: tâm 200 giữa tám pixel 100

Tạo ảnh 5×5 đều 100, tâm bằng 200; xét cửa sổ 3×3 quanh tâm. Tổng=8×100+200=1000, nên μ=1000/9≈111,111. Tổng bình phương=8×10000+40000=120000; E[I²]=120000/9. Phương sai v=E[I²]−μ²=80000/81≈987,654.

Với L=4, nhiễu ước lượng μ²/L≈3086,420, lớn hơn v. Công thức K=clip(1−noise_var/v,0,1) cho K=0. Kết quả tâm μ+K×(200−μ)=μ, làm tròn thành 111.

Đây là ví dụ cho thấy bộ lọc coi dao động trong cửa sổ là phần nên làm mượt theo giả định đã chọn. Không suy ra mọi xung 200 trong mọi ngữ cảnh đều là nhiễu. Nếu đó là một điểm sáng thật cần giữ, bộ lọc có thể làm mất nó.

**Hỏi sâu:** Nếu hai bản cùng cho 111 ở tâm, đã chứng minh toàn ảnh đúng chưa? Chưa. Mép ảnh dùng cửa sổ có padding, và các cửa sổ khác có thống kê khác; cần thêm ca biên và nhiều kiểu ảnh.

### 4.3. Sobel: từ hai đạo hàm đến độ lớn gradient

Xét ma trận 3×3 sau và tính tại tâm theo kernel Sobel trong code.

```text
0    0    0
0  100  100
0  100  100
Gx = (0 + 2*100 + 100) - (0 + 2*0 + 0) = 300
Gy = (0 + 2*100 + 100) - (0 + 2*0 + 0) = 300
```

Độ lớn thực là sqrt(300 ²+300 ²)≈424,264. Điều này giải thích tại sao gradient cần số thực và vì sao 255 không phải giới hạn toán học của đạo hàm. Ảnh độ lớn để hiển thị có thể clip về 255; Canny phải giữ/recompute độ lớn từ Gx, Gy trước NMS.

**Hỏi sâu:** Đổi dấu cả Gx và Gy có giữ độ lớn không? Có. Nhưng hướng cần hiểu theo quy ước góc và hệ tọa độ; so signed derivative khác với so magnitude. Kiểm thử không được vô tình bỏ qua một dấu sai khi mục tiêu đang kiểm đạo hàm có hướng.

### 4.4. Hình thái: khối 4×4 trong ảnh 8×8

Đặt một khối vuông đặc 4×4 ở giữa ảnh nhị phân 8×8. Với phần tử cấu trúc vuông 3×3, erosion chỉ giữ những pixel có toàn cửa sổ nằm trong khối. Khối còn 2×2, tức 4 pixel. Dilation mở rộng mỗi phía một pixel, thành 6×6, tức 36 pixel.

Biên trong được tính A−erode (A). Diện tích A là 16; phần lõi là 4; số pixel biên là 12. Đây là cách kiểm chứng trực tiếp rằng biên không phải diện tích vùng. Khối đặt giữa ảnh tránh phụ thuộc mép; muốn kiểm padding phải thêm một khối chạm mép.

### 4.5. Otsu: hai mức 50 và 200

Tạo ảnh 8×8, nửa pixel bằng 50, nửa bằng 200. Với ngưỡng t từ 50 đến 199, lớp tối có trọng số 0,5 và mean =50; lớp sáng có trọng số 0,5 và mean =200. Phương sai giữa lớp là 0,5×0,5×(200−50)²=5625.

Mean toàn ảnh=125, phương sai toàn ảnh cũng bằng 5625, nên η=1. Code quét từ 0 lên và chỉ cập nhật khi có giá trị lớn hơn, nên ngưỡng đầu tiên tối ưu là 50. Dùng điều kiện I<=50 mới giữ đúng nửa tối; nếu dùng I<50 sẽ không giữ pixel nào trong ví dụ này.

**Hỏi sâu:** η=1 có chứng minh ảnh dầu được phân đúng tuyệt đối không? Không. Nó chỉ nói hai nhóm mức xám tách tốt theo tiêu chí đang tính. Nhãn vật lý không xuất hiện trong công thức.

## 5. Tại sao hai cài đặt cùng tên vẫn khác nhau?

### 5.1. Padding và vùng nội thất

Nếu sai khác chỉ tập trung ở viền ảnh, hãy kiểm quy tắc đệm trước. `np.pad(..., mode="reflect")` tương ứng cách phản xạ không lặp pixel biên; trong các đối chứng của dự án, SciPy `mirror` và OpenCV `BORDER_REFLECT_101` được chọn khi phù hợp. EPI dùng `symmetric` để khớp cách SciPy reflect của phép Laplacian tham chiếu. Không đổi tên mode theo cảm giác vì tên giữa thư viện không hoàn toàn thống nhất.

Một cách chẩn đoán là so vùng giữa ảnh và toàn ảnh riêng. Nếu giữa khớp nhưng mép lệch, đó là dấu hiệu cần xem padding; chưa đủ để khẳng định nguyên nhân duy nhất. Cuối cùng vẫn phải đọc code và thiết lập đúng hợp đồng, không bỏ mép chỉ để giảm sai số báo cáo.

### 5.2. Dtype, rounding và clipping

Một thư viện có thể trả float còn hàm custom trả uint8. So trực tiếp mà không thống nhất đầu ra có thể đo cả khác biệt lượng tử hóa lẫn khác biệt công thức. Registry chuyển các đầu ra về số thực trước phép trừ để tránh tràn; trong từng reference, việc lượng tử hóa được thiết kế theo phép toán cụ thể.

Ví dụ 100,49 và 100,51 khác nhau 0,02 ở số thực nhưng có thể thành 100 và 101 sau làm tròn. Ngược lại, hai số thực khác nhau có thể cùng làm tròn thành 100. Vì vậy tỷ lệ trùng uint8 không thể thay thế toàn bộ kiểm tra trên đại lượng trung gian khi cần.

### 5.3. Kernel, normalization và footprint

Gaussian cần cùng sigma, kích thước kernel và cách chuẩn hóa. Một kernel bị quên chia tổng trọng số có thể đổi cả độ sáng ảnh hằng. Bilateral cần cùng sigma_s/sigma_r và tập láng giềng; dùng cùng tham số nhưng một bên đĩa, một bên vuông vẫn có thể khác.

Sobel magnitude có thể dùng chuẩn L 1 là |Gx|+|Gy| hoặc L 2 là sqrt (Gx²+Gy²). Với Gx=Gy=3, L 1=6, L 2≈4,243. Đây là khác định nghĩa, không phải sai số số học nhỏ. Khi giải thích reference của Canny, phải biết tham số liên quan đến chuẩn gradient và các bước làm mịn.

### 5.4. Tolerance phải có lý do trước khi xem kết quả

Tolerance là mức sai khác được chấp nhận cho phép kiểm tương đương cụ thể. Một số phép toán nguyên và cùng quy tắc có thể yêu cầu max error=0; một số phép có lượng tử hóa/interpolation cho phép chênh một mức xám. Gradient float hoặc chỉ số thực có thể dùng ngưỡng nhỏ khác. Không có một tolerance đúng cho mọi kiểu đầu ra.

Nếu đang FAIL, quy trình là kiểm đầu vào/tham số/padding/dtype, tìm ca nhỏ tái hiện và giải thích khác biệt. Không tăng tolerance tới mức vừa đủ để hết đỏ rồi gọi là sửa thuật toán. Nếu thực sự là hai biến thể, phải chuyển cách trình bày sang DESCRIPTIVE có lý do, không âm thầm thay chuẩn.

## 6. Đọc và vận hành bộ đối chiếu của dự án

### 6.1. Registry là gì và tại sao hữu ích?

Registry là danh sách mô tả mỗi phép đối chiếu: tên, hàm custom, hàm reference, lời giải thích, nhóm direct/composition/variant và giới hạn sai số. Vòng chạy chung nhận từng mô tả để tạo bảng. Cách này giúp tránh viết 33 đoạn kiểm tra rời rạc với tiêu chí không nhất quán.

Khi đọc một hàng registry, hãy tự phát biểu thành câu: “Tôi đang so đầu ra X của hàm A với đầu ra Y của thư viện B, cùng tham số..., chấp nhận max error..., vì...”. Nếu không thể nói đủ, bạn chưa hiểu phép kiểm mà mình bảo vệ.

### 6.2. Vì sao có 18 ca?

Có tám ảnh tổng hợp: đen, hằng 127, trắng, ramp, bàn cờ, đường chéo, nhiễu có seed và xung đơn; cộng mười ảnh demo. 33 phép toán/chỉ số nhân 18 ca thành 594 hàng. Các ca tổng hợp không nhằm giống mọi cảnh biển; chúng làm nổi bật tính chất cụ thể khó kiểm từ ảnh thật.

Ảnh hằng kiểm gradient/chia 0; ramp kiểm hướng và tỷ lệ đạo hàm; đường chéo kiểm NMS/liên thông; bàn cờ gây nhiều thay đổi nhanh; xung đơn cho thấy đáp ứng kernel; ảnh nhiễu kích thước 63×67 kiểm cả trường hợp không chia hết lưới. Mười ảnh thật kiểm hành vi trên dữ liệu đang dùng nhưng không thay cho kiểm chứng toàn bộ không gian đầu vào.

### 6.3. Các cột kết quả và cách truy vết

`algorithm` và `case` xác định phép toán/ảnh. `reference` mô tả hàm đối chứng; `kind` nói mức tương đương. `max_abs_error`, `mae`, `mse`, `agreement_pct` mô tả sai khác. `limit` là giới hạn được dùng; `verdict` là kết luận theo giới hạn đó. `custom_ms` và `reference_ms` là thời gian đo trong lần chạy.

Một số bản đồ biên có `edge_f1_exact`: đây là độ trùng pixel giữa hai cài đặt, không phải F1 với mask dầu chuẩn. Dịch một biên đi một pixel có thể làm điểm exact thấp dù mắt nhìn gần nhau. Với hai bản đồ rỗng, quy ước mẫu số bảo vệ trong code cũng cần được hiểu; không suy ra chất lượng ứng dụng chỉ từ một số.

`summary.csv` gộp theo thuật toán và nhóm, còn `per_case.csv` mới cho biết lỗi nằm ở ảnh nào. TV2 phải biết mở hàng chi tiết, không chỉ đọc bảng trung bình cuối cùng.

### 6.4. Chạy đối chiếu thế nào?

```powershell
uv run python -m src.verification
uv run python -m src.library_comparison
uv run --extra dev python -m pytest tests/test_core.py -q
```

Lệnh đầu chạy cả ví dụ tay và registry; lệnh thứ hai chỉ chạy registry. Đầu ra nằm trong `results/verification/`. Lệnh thoát khác 0 khi có FAIL ở nhóm có giới hạn; phải đọc log và bảng chi tiết trước khi đưa số vào báo cáo.

## 7. Tư duy khoa học khi diễn giải kết quả

### 7.1. Không dùng “khớp thư viện” thay cho chứng minh mọi thứ

Thư viện là đối chứng hữu ích, không phải sự thật vật lý của cảnh biển. Hai cách cài cùng công thức có thể cùng không phù hợp với dữ liệu. Phép ghép reference Lee chia sẻ công thức với custom, nên không độc lập hoàn toàn về lựa chọn mô hình. Ví dụ tay, đối chiếu và phân tích ca lỗi bổ sung cho nhau.

### 7.2. Phản ví dụ giúp hiểu sâu hơn ảnh thành công

Nếu HE làm một ảnh rõ hơn, hãy hỏi ảnh hằng sẽ thế nào, ảnh có nền rất sáng nhỏ sẽ thế nào, và histogram có thể khác dù hình dạng giống nhau không. Nếu erosion xóa nhiễu nhỏ, hãy hỏi nó có xóa vệt thật nhỏ không. Một phản ví dụ có giải thích cho thấy bạn hiểu điều kiện áp dụng hơn là khẳng định phương pháp luôn tốt.

### 7.3. Khảo sát tham số không được làm đẹp kết luận

Chọn clip/grid sau khi xem kết quả trên mười ảnh có thể tạo thiên lệch về bộ mẫu đó. Không có ML không đồng nghĩa không có thiên lệch chọn tham số. Khi báo cáo, nêu rõ ảnh nào dùng khảo sát, ảnh nào dùng đánh giá, và không gọi các mẫu đã xem là kiểm thử độc lập.

Tương tự, không so thời gian hai hàm khi một bên bao gồm đọc ảnh còn bên kia không. Một số runtime nhỏ dễ chịu ảnh hưởng khởi động, luồng và tải máy. Sai số số học và hiệu năng là hai câu hỏi khác nhau.

### 7.4. Tài liệu tham khảo phải phục vụ lập luận

Nguồn gốc công thức, định nghĩa tham số và khác biệt biến thể cần được ghi theo tài liệu nhóm thực sự đọc. Sổ tay này giải thích triển khai đang có trong repo; không khẳng định đã kiểm chứng mọi biến thể từ mọi bài báo cùng tên. Trước bảo vệ, TV2 cần mở các nguồn được trích trong báo cáo, xác nhận chúng hỗ trợ đúng câu đang dùng, và ghi lại phần chưa hiểu để hỏi giảng viên/nhóm.

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

## 9. Câu hỏi ôn tập có gợi ý trả lời cho TV2

**Câu 1 — Tại sao expected không được sinh bằng hàm custom?** Vì hai bên sẽ chia sẻ cùng lỗi; so một hàm với chính nó không kiểm chứng độc lập. Dùng phép tính tay hoặc reference có quy ước rõ.

**Câu 2 — Với delta=[0,0,0,10], MSE bằng bao nhiêu?** (0+0+0+100)/4=25. MAE=2,5; max error=10. Hãy giải thích chứ không chỉ đọc số.

**Câu 3 — Tỷ lệ trùng 0% có luôn chứng minh sai lớn?** Không. Tất cả pixel lệch một mức xám cũng cho 0%; cần đọc độ lớn sai khác và tolerance.

**Câu 4 — Tại sao Gaussian và median không dùng cùng reference?** Chúng là hai phép toán khác: tổ hợp có trọng số và chọn trung vị. Tên chung “lọc nhiễu” không làm chúng tương đương.

**Câu 5 — HE ví dụ có ánh xạ mức 1 thành bao nhiêu?** CDF tại 1 là 8; trừ CDF_min=4, chia 12 và nhân 255 được 85. Nếu trả lời 64 là đang dùng quy ước khác, cần chỉ ra khác công thức.

**Câu 6 — Tại sao tâm Lee ví dụ thành 111?** v nhỏ hơn μ²/L nên K bị chặn 0; đầu ra là mean 1000/9, rồi round. Không phải Lee luôn thay tâm bằng trung bình.

**Câu 7 — Sobel vượt 255 có nghĩa ảnh đầu vào lỗi không?** Không; đạo hàm là tổ hợp có trọng số, có miền giá trị khác cường độ. Cần float để giữ nó.

**Câu 8 — Vì sao Otsu chọn 50 thay vì 125 ở ví dụ hai mức?** Nhiều ngưỡng 50–199 cùng cực đại; code giữ ngưỡng đầu tiên. Nhãn phân lớp vẫn giống nhau nếu dùng điều kiện phù hợp.

**Câu 9 — Nếu dùng `<t` thay `<=t` có khác không?** Có ở mức đúng bằng t; ví dụ t=50 sẽ mất toàn bộ nửa tối nếu dùng <50. Đây là lỗi endpoint có thể lớn dù chỉ khác một ký tự.

**Câu 10 — Erosion của vuông 4×4 bằng kernel 3×3 còn bao nhiêu?** Bỏ một lớp viền mỗi phía, còn 2×2=4; chỉ đúng cho hình đặt đủ xa biên và quy ước đang nêu.

**Câu 11 — Thấy sai ở mép thì làm gì trước?** Kiểm padding, anchor, kernel và dtype; tách sai vùng nội thất để chẩn đoán. Không xóa mép khỏi báo cáo mà không giải thích.

**Câu 12 — Direct có độc lập tuyệt đối không?** Không. Nó độc lập hơn về triển khai, nhưng vẫn có giả định tham số/biến thể và có thể cùng không phù hợp với mục tiêu vật lý.

**Câu 13 — Composition Lee kiểm được điều gì?** Moment cục bộ và việc kết hợp theo công thức đã chọn; nó không chứng minh công thức này là lựa chọn tối ưu cho mọi ảnh SAR.

**Câu 14 — Vì sao Bilateral là variant?** Footprint và các chi tiết rời rạc hóa giữa custom và reference khác nhau; cùng tên/sigma chưa đủ đảm bảo cùng toán tử.

**Câu 15 — 594 gồm những gì?** 33 mục×18 ca; 18 ca gồm 8 tổng hợp+10 demo. Kết quả hiện tại 558 PASS,36 DESCRIPTIVE,0 FAIL.

**Câu 16 — `edge_f1_exact` có phải chất lượng biên dầu không?** Không. Nó đo trùng pixel với bản đồ biên của reference, không với mask dầu được gán chuẩn.

**Câu 17 — Có được tăng tolerance khi FAIL không?** Chỉ khi có phân tích xác lập quy ước và lý do toán học/số học phù hợp; không thay nó chỉ để đạt kết quả mong muốn. Nếu khác biến thể, phải báo khác biến thể.

**Câu 18 — Không ML thì có cần lo chọn mẫu thuận lợi không?** Có. Chọn ảnh đẹp hoặc tham số sau khi xem kết quả vẫn làm kết luận lạc quan quá mức.

**Câu 19 — Tại sao cần test ảnh hằng?** Để kiểm gradient 0, nhánh chia 0 và hành vi thuật toán khi không có tương phản. Ảnh biển thật không cung cấp đáp án đơn giản như vậy.

**Câu 20 — Mục tiêu tối thiểu khi giải thích một hàng CSV?** Nêu input, phép toán, reference, loại so sánh, chỉ số, tolerance, kết luận và giới hạn. Nếu chỉ nói PASS thì chưa đủ.

## 10. Thực hành và trình bày của TV2

### 10.1. Bài học có sản phẩm

**Bài A:** Viết lại năm ví dụ ở chương 4 trên giấy, che đáp án rồi tính từ đầu. Sau đó chạy `src.verification` và so. Ghi rõ chỗ sai do công thức, số học hay quy ước.

**Bài B:** Chọn một direct, một composition và một variant trong registry. Lập ba đoạn văn, mỗi đoạn giải thích input /reference/tolerance và điều không được kết luận. Đây là bài tập chuẩn bị slide 14.

**Bài C:** Đọc một hàng có max error lớn nhất trong CSV; mở ảnh tương ứng, kiểm vùng nội thất/biên và quy tắc làm tròn. Không sửa số liệu. Nếu không biết nguyên nhân, ghi “chưa giải thích” cùng ca tái hiện.

**Bài D:** Tự tạo hai mask cùng diện tích nhưng dịch nhau một pixel. Dự đoán tỷ lệ trùng và edge F1 sẽ thay đổi, rồi giải thích vì sao số pixel bằng nhau chưa đủ chứng minh hình học giống nhau.

### 10.2. Kịch bản nói

Slide 5 trong 40 giây: nói ảnh SAR khó vì speckle và lookalike; tối không đồng nghĩa dầu. Slide 14 trong 80 giây: ba loại reference, năm ví dụ tay,33×18 ca và phạm vi 558 PASS/36 DESCRIPTIVE. Tổng 120 giây. Dành phần lớn thời gian cho logic kiểm chứng, không đọc hết tên các hàm.

Nếu được yêu cầu minh họa, mở một hàng CSV và diễn giải đầy đủ, hoặc tính ví dụ Lee/HE trên giấy. Chuẩn bị để trả lời chéo về mask/biên, CLAHE và ENL. Không cần chạy toàn bộ benchmark trong phần trình bày ngắn.

### 10.3. Tiêu chí tự đánh giá

Đạt khi tự tính được cả năm fixture, giải thích được tại sao phải khớp padding/dtype, và đưa ra một trường hợp phép toán đúng nhưng ứng dụng báo nhầm. Chưa đạt nếu chỉ nhớ 558 và 36 mà không biết chúng được tạo ra từ đâu.
