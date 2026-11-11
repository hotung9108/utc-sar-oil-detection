# TV5 — Phạm Minh Tuấn — Sổ tay học và bảo vệ từ nền tảng

GitHub: `tuanpham21105`. Trách nhiệm: Dữ liệu, chỉ số, thực nghiệm và tái lập. Mã phụ trách: `src/tv5/, reproduce.py`.

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

## 3. Dataset, nhãn và phạm vi bằng chứng

### 3.1. Dataset là gì, nhãn là gì?

Dataset là tập dữ liệu được dùng có hệ thống cho thực nghiệm. Trong repo, ảnh chính nằm ở `kaggle/data/Class_0` và `Class_1`. Theo metadata đi kèm, Class_0 biểu diễn không dầu/biển sạch hoặc lookalike; Class_1 biểu diễn ảnh có dầu. Nhãn này gắn với toàn ảnh, không chỉ ra chính xác pixel nào thuộc dầu.

Nhãn cấp ảnh có thể dùng để kiểm một quy tắc báo “có ứng viên hay không”. Muốn kiểm đường biên hoặc diện tích pixel, cần mask chuẩn được gán riêng. Không được tự biến tên thư mục thành một mask bằng threshold rồi dùng mask ấy làm ground truth để đánh giá chính threshold.

### 3.2. Nguồn dữ liệu và giấy phép để làm gì?

Metadata cục bộ nêu bộ CSIRO Sentinel-1 SAR của David Blondeau-Patissier, DOI 10.25919/4v55-dn16. File license đi kèm ghi CC BY-SA 4.0. Hồ sơ nguồn giúp biết dữ liệu là gì, nhãn được hiểu ra sao và cách ghi công khi sử dụng. Sổ tay này dựa vào hồ sơ trong repo, không tự khẳng định đã tải lại và xác minh toàn bộ bộ gốc từ máy chủ nguồn.

Tên dataset có cụm “for machine learning (Deep Learning)” nói tới mục đích có thể sử dụng của bộ ảnh. Nó không bắt buộc chương trình phải dùng ML / DL. Dự án chỉ đọc ảnh, áp công thức xử lý và đánh giá đầu ra; không train mô hình.

### 3.3. Vì sao có ba con số 5.630, 5.538 và 5.548?

Metadata công bố 5.630 ảnh: 3.725 lớp 0 và 1.905 lớp 1. Hai thư mục chính trong repo có 5.538 ảnh: 3.695 lớp 0 và 1.843 lớp 1, ít hơn 30+62=92 ảnh. Chưa có checksum bộ gốc để giải thích nguyên nhân chênh; không được tự nói đó là 92 ảnh lỗi đã loại nếu không có bằng chứng.

Kiểm kê đệ quy thấy thêm 10 file ở `kaggle/data/sample/`, đều trùng SHA-256 với ảnh chính. Vì vậy tổng có 5.548 đường dẫn nhưng 5.538 ảnh khác byte. Thống kê chính không đếm lặp 10 bản sao này. Mười ảnh demo ở `data/sample/` cũng trùng byte với một số ảnh chính.

### 3.4. SHA-256, trùng byte và độc lập dữ liệu

Hash là một dấu vân tay nội dung dùng để đối chiếu file. Nếu hai file có cùng SHA-256 trong kiểm kê, ta có bằng chứng rất mạnh rằng byte giống nhau. Nhưng hai ảnh có hash khác vẫn có thể là hai crop chồng lấn của cùng cảnh, hoặc một ảnh đã nén lại. Khác hash không chứng minh độc lập về nội dung.

Chưa có scene ID đầy đủ nên chưa kết luận các chip độc lập. Mười ảnh demo đã dùng để quan sát/chọn tham số không được coi là một tập kiểm thử độc lập. Không có train mô hình vẫn có thiên lệch khi chỉ chọn ảnh thuận lợi hoặc chỉnh tham số sau khi xem kết quả.

### 3.5. Chuẩn hóa đầu vào và điều gì đã mất

Ảnh chính 400×400 được lưu RGB, pipeline đọc xám. JPEG 8 bit là dữ liệu đã xử lý, không giữ mọi thông tin hiệu chuẩn bức xạ và độ phân giải mặt đất trong quy trình hiện tại. Đổi sáng/resize có thể thay ý nghĩa chỉ số theo pixel.

TV5 cần ghi kích thước, số ảnh, nhãn, nguồn, bản sao và thiếu hụt trước khi báo hiệu năng. Một bảng có hàng nghìn số nhưng không biết những hàng ấy thuộc dữ liệu nào chưa phải bằng chứng có thể tái lập.

## 4. Sáu chỉ số xử lý ảnh: định nghĩa, ví dụ và giới hạn

### 4.1. ROI và ENL

ROI là vùng quan tâm được chọn để đo. ENL =μ²/v, với μ là mean và v là variance trong ROI. Nếu ROI là vùng tương đối đồng nhất, dao động thấp hơn so với mean có thể gợi ý speckle đã giảm. Nó không đếm trực tiếp số look vật lý của JPEG.

Ví dụ ROI mean 100, variance 400 cho ENL 25. Sau lọc, nếu mean vẫn 100 và variance 100 thì ENL 100. Tuy nhiên một bộ lọc xóa hết cả chi tiết cũng có thể làm variance rất nhỏ và ENL rất lớn. Vì vậy ENL cao chỉ có ý nghĩa khi ROI và mục tiêu giữ chi tiết được kiểm.

Mặc định code lấy hàng 20:80, cột 20:80 nếu ảnh đủ lớn, tức ROI 60×60 trên ảnh 400×400. Đây là tọa độ cố định, không phải một bước tự nhận diện biển sạch. Nếu kích thước nhỏ<=20, code dùng toàn ảnh. Khi variance <1e−8, trả 999 như giá trị quy ước, không phải số đo vật lý chính xác 999 look. ROI tự truyền phải hợp lệ và không rỗng; không quảng cáo mọi ROI đều tự được kiểm.

### 4.2. SSI: tỷ lệ biến thiên trước và sau lọc

Hệ số biến thiên CV = std / mean. SSI = CV_sau/ CV_trước. Nếu mean trước/sau 100, std trước 20 và std sau 10, thì CV trước 0,2, CV sau 0,1, SSI 0,5. Nó nói mức dao động tương đối giảm một nửa theo cách đo, không nói 50% pixel nhiễu đã được loại chính xác.

SSI <1 có thể phù hợp với làm mượt, nhưng cũng có thể do mất cấu trúc thật. Nó được tính trên toàn ảnh trong hàm hiện tại, nên biên/vệt cũng ảnh hưởng std. Nếu mean hoặc std ban đầu quá nhỏ, code trả 1 để tránh chia không ổn định; số 1 khi đó không phải bằng chứng lọc không có tác dụng.

### 4.3. RMS contrast

RMS contrast trong repo là độ lệch chuẩn mức xám: căn của trung bình (I−μ)². Dãy [80,120] mean 100 cho RMS 20; dãy [90,110] cho RMS 10. Nó đo mức trải cường độ toàn cục.

Tăng RMS có thể làm chi tiết dễ phân biệt hơn, nhưng nhiễu cũng tăng RMS. Giảm RMS có thể là lọc thành công hoặc mất tương phản vệt. Không kết luận cứ lớn hơn là tốt hơn nếu chưa xác định đang đánh giá tăng cường hay khử nhiễu và ảnh nào được đo.

### 4.4. Entropy histogram

Entropy H=−sum (p_i× log2 (p_i)), trong đó p_i là tỷ lệ pixel mức i; bỏ các p_i=0 để tránh log 0. Ảnh hằng chỉ có một mức với xác suất 1 nên H 0. Hai mức xuất hiện bằng nhau có H 1 bit. Histogram đều trên 256 mức có H 8 bit.

Entropy mô tả độ đa dạng của mức xám, không hiểu vị trí hoặc ý nghĩa. Ảnh nhiễu ngẫu nhiên có thể entropy cao nhưng không hữu ích hơn. Hai ảnh hoán vị pixel có cùng histogram/ entropy trong khi cấu trúc khác hoàn toàn. Không gọi entropy tăng là “thông tin dầu tăng” nếu chưa có bằng chứng khác.

### 4.5. AMBE: khác biệt mean

AMBE =| mean_sau− mean_trước|, đo mức thay đổi độ sáng trung bình. Ví dụ mean 100→110 cho AMBE 10. AMBE 0 chỉ nói hai mean bằng nhau. Hai dãy [80,120] và [0,200] đều mean 100 nhưng tương phản/chi tiết thay đổi mạnh; AMBE vẫn 0.

Chỉ số này hữu ích khi muốn theo dõi độ sáng chung sau tăng cường, không phải độ giống ảnh ở từng pixel. Khi CLAHE làm mean đổi, cần giải thích đó là tác dụng biến đổi histogram, không mặc định coi mọi thay đổi mean là lỗi cài đặt.

### 4.6. EPI: tổng đáp ứng Laplacian trước/sau

Code tính Laplacian 5 điểm của ảnh gốc và ảnh xử lý, lấy tổng trị tuyệt đối mỗi ảnh rồi lấy tỷ số sau/trước. Nếu tổng trước 1000, sau 800 thì EPI 0,8. Nó gợi ý tổng mức đáp ứng tần số cao/biên đã giảm, nhưng không so vị trí từng đường biên.

Hai ảnh có cạnh ở chỗ khác nhau vẫn có thể cùng tổng Laplacian và EPI 1. Nhiễu mới cũng có thể bù tổng đáp ứng bị mất ở vệt. Vì vậy EPI gần 1 không chứng minh biên dầu được giữ đúng. Nếu mẫu số gần 0, code trả 1; đây cũng là quy ước bảo vệ cần nói rõ.

Padding của phép Laplacian trong metrics là symmetric để khớp reference SciPy. Không tự thay thành reflect vì thấy các bộ lọc khác dùng reflect: đó là một thay đổi định nghĩa ở mép cần kiểm lại.

### 4.7. Chỉ số đang đo ảnh nào?

Trong pipeline, metrics so `raw` với `displayed`, là ảnh sau lựa chọn làm nét. Do đó bật unsharp có thể làm entropy / RMS / EPI đổi dù mask không đổi. Trong thí nghiệm so lọc, enhancement được đặt none để tập trung vào đầu ra lọc. Đọc config và entrypoint trước khi gắn tên “chất lượng bộ lọc” cho một cột.

Mean/ std /count trong bảng summary là thống kê qua nhiều hàng ảnh, không phải mean / variance pixel bên trong công thức ENL /Lee. Hai cấp thống kê này có ý nghĩa khác nhau. Pandas std tổng hợp dùng quy ước mẫu mặc định, còn `np.var`/`np.std` trên ảnh trong các hàm đang dùng quy ước chia N.

## 5. Thiết kế thí nghiệm để câu trả lời có căn cứ

### 5.1. Biến độc lập, biến đo và yếu tố giữ cố định

Biến độc lập là thứ ta chủ động thay, như loại lọc hoặc clip. Biến đo là kết quả ta ghi, như ENL, diện tích hay thời gian. Yếu tố giữ cố định gồm ảnh, kích thước, code và các tham số còn lại. Nếu thay nhiều thứ cùng lúc, không thể biết nguyên nhân riêng của thay đổi.

Thí nghiệm so lọc hiện dùng 8 lựa chọn kể cả none trên 10 ảnh, tổng 80 hàng. Khảo sát CLAHE dùng 5 clip×3 grid×10 ảnh=150 hàng. Nhiễu dùng 4 mức sigma kể cả 0×6 phương pháp biên×10 ảnh=240 hàng. Ca lỗi dùng 00013 và 5 ảnh biển, có/không CLAHE, tổng 12 hàng. Các số hàng phải phù hợp thiết kế, không chỉ nhìn CSV tồn tại.

### 5.2. Seed và nhiễu tổng hợp

Seed 2026 giúp lặp lại chuỗi số giả ngẫu nhiên trong cùng quy trình. Mỗi ảnh/mức sigma tạo một ảnh nhiễu cộng Gaussian rồi các phương pháp biên dùng cùng ảnh đó, giúp so công bằng hơn ở điều kiện ấy. Tuy nhiên chỉ có một realization cho mỗi trường hợp; chưa có đủ lặp để mô tả đầy đủ độ biến thiên theo nhiễu.

Nhiễu Gaussian cộng không thay thế hoàn toàn speckle nhân của SAR. Thí nghiệm kiểm độ nhạy khi có dao động bổ sung, không chứng minh khả năng khử mọi speckle vật lý. Sau cộng nhiễu có clipping và làm tròn về 8 bit, nên phân bố cuối cũng chịu ảnh hưởng các bước này.

### 5.3. Per-image trước, summary sau

Hàng theo ảnh giúp tìm ca nào tốt/xấu, kiểm số mẫu và tái tính tổng hợp. Summary giúp nhìn xu hướng nhưng có thể che một số ca hỏng nặng. Luôn giữ bảng chi tiết thay vì chỉ chụp một con số trung bình.

Một độ lệch chuẩn lớn nghĩa các hàng khác nhau nhiều trong phép đo; không tự chứng minh code không ổn định. Có thể ảnh có cấu trúc khác nhau. Muốn tách biến thiên do máy chạy và do ảnh, cần thiết kế lặp phù hợp, không trộn hai nguyên nhân.

### 5.4. Ca thất bại cần được giữ lại

00013 là ví dụ dễ giải thích vệt chính; sea_surface_01 là ví dụ cho thấy vùng tối không phải dầu vẫn có thể qua quy tắc. Không xóa ca xấu khỏi báo cáo để tăng điểm. Phân tích lỗi cho biết giới hạn nào cần cải tiến: threshold toàn cục, ROI nền, kích thước kernel, ngưỡng vùng hay dữ liệu không đủ.

Khi thay thuật toán, cần chạy lại cả hai lớp để xem giảm FP có làm FN tăng không. Chỉ chạy lại đúng ảnh từng bị sai có thể tạo một sửa phù hợp cục bộ nhưng hỏng nhiều ảnh khác.

## 6. Đánh giá quy tắc vùng tối mà không dùng học máy

### 6.1. Từ mask đến một quyết định cấp ảnh

Sau khi `process_image` kết thúc, hàm `evaluate_one` đặt prediction=1 nếu `slicks_count>0`, ngược lại 0. Đây là quy tắc xác định bằng tay, không phải mô hình được train. Nhãn thư mục đi cùng đường dẫn chỉ được dùng để đối chiếu sau đó, không được truyền vào bộ lọc để học.

Quy tắc này bỏ qua nhiều chi tiết của mask: một pixel vùng ở sai vị trí nhưng vẫn tạo thành phần đạt điều kiện có thể làm ảnh được báo dương. Vì vậy kết quả cấp ảnh không chứng minh đường biên hoặc vùng dầu trong ảnh được tìm đúng vị trí.

### 6.2. Confusion matrix là bảng đếm gì?

| Trường hợp | Ý nghĩa trong bài |
| --- | --- |
| TP | Ảnh Class_1 và quy tắc có ứng viên |
| FN | Ảnh Class_1 nhưng quy tắc không giữ ứng viên |
| FP | Ảnh Class_0 nhưng quy tắc giữ ứng viên |
| TN | Ảnh Class_0 và quy tắc không giữ ứng viên |

“Đúng/sai” ở bảng này được hiểu là đối chiếu với nhãn nguồn đã cung cấp, không phải nhóm đã xác minh thực địa từng ảnh. Lượt toàn tập có TP 1639, FN 204, FP 2885, TN 810. Tổng 5538; TP + FN 1843 đúng số ảnh Class_1; FP + TN 3695 đúng số Class_0. Đây là hai kiểm tra cộng phải tự làm được.

### 6.3. Precision và recall trả lời hai câu hỏi khác nhau

Precision= TP /(TP + FP)=1639/4524≈36,23%. Nó trả lời: trong các ảnh bị quy tắc báo có ứng viên dầu, bao nhiêu mang nhãn có dầu? Recall= TP /(TP + FN)=1639/1843≈88,93%. Nó trả lời: trong các ảnh mang nhãn có dầu, có bao nhiêu được quy tắc tìm ứng viên?

Recall cao cùng precision thấp nghĩa quy tắc ít bỏ sót tương đối nhưng báo nhầm nhiều. Đây là thước đo đầu ra của bất kỳ hệ quyết định phù hợp, kể cả ngưỡng cổ điển. Việc dùng phép chia hai số đếm không khiến thuật toán thành ML. Trọng tâm BTL vẫn là xử lý ảnh; hai chỉ số này chỉ giúp nhìn giới hạn của quy tắc ứng viên.

### 6.4. F1, specificity và accuracy

F1=2 TP /(2 TP + FP + FN)≈51,48%, tổng hợp precision / recall theo dạng trung bình điều hòa. Specificity= TN /(TN + FP)≈21,92%, cho biết tỷ lệ ảnh không dầu được giữ đúng âm. Accuracy =(TP + TN)/N≈44,22%.

Không có một số nào tự tóm hết chất lượng. Quy tắc “luôn báo có” có recall 100% nhưng báo nhầm mọi Class_0. Quy tắc “luôn báo không” có accuracy 3695/5538≈66,72% trên tập lệch lớp này nhưng recall 0. Accuracy của một quy tắc không tìm được dầu vẫn có thể cao hơn 44,22%; điều đó buộc ta mô tả giới hạn thật, không chọn chỉ số có vẻ đẹp nhất.

### 6.5. Vì sao chưa báo IoU/Dice của dầu?

IoU so phần giao mask dự đoán và mask chuẩn chia phần hợp; Dice dùng 2 giao chia tổng diện tích hai mask. Cả hai cần ground truth theo pixel để nói về chất lượng phân đoạn dầu. Repo chưa có bộ mask chuẩn đó. Tự lấy mask từ Otsu làm “chuẩn” để đánh giá Otsu là kiểm vòng, không phải chứng minh đúng vật lý.

Có thể đo độ trùng với một hàm thư viện để kiểm cách cài, nhưng phải gọi đúng tên phép đối chiếu. Không lấy edge F1 giữa hai cài đặt ở TV2 để thay cho F1 với nhãn dầu chuẩn.

### 6.6. Đọc summary theo lớp phải cẩn thận

`dataset_summary.csv` tổng hợp các cột số theo label. Trung bình cột prediction ở Class_1 bằng tỷ lệ báo dương trong ảnh có dầu, tức recall theo quy tắc này. Ở Class_0, nó là tỷ lệ báo dương nhầm, không phải accuracy. Nếu thấy prediction_mean cao rồi gọi cả hai lớp “đạt cao” là đọc sai ý nghĩa cột.

## 7. Tái lập: từ lệnh chạy đến manifest

### 7.1. Tái lập là gì và tại sao cần?

Tái lập nghĩa người khác có thể xác định input, code, tham số và môi trường đã tạo ra kết quả, rồi chạy lại trong điều kiện tương ứng. Chỉ có ảnh chụp màn hình đẹp không đủ vì thiếu những thông tin này. Một thay đổi nhỏ ở threshold hoặc padding có thể làm mask khác.

`reproduce.py` viết manifest trạng thái in_progress, chạy ví dụ/đối chiếu, khảo sát mẫu và toàn dataset, rồi mới ghi completed_scope = full. Nếu dùng `--samples-only`, phạm vi là samples. Trình dựng báo cáo kiểm phạm vi full và source hash, nên không dùng một lượt mẫu để xác nhận toàn tập.

### 7.2. Source hash khác Git SHA thế nào?

Git SHA xác định một commit. Nếu có thay đổi chưa commit lúc đo, SHA đó chưa mô tả hết working tree. `code_digest()` băm các file Python trong src, cùng reproduce.py, pyproject.toml, uv.lock để lưu dấu nội dung lõi/môi trường đang đo. Manifest còn có git_dirty cho biết có thay đổi chưa commit.

Hash này không tự bao phủ mọi byte của dataset và mọi script tài liệu. Kiểm kê dữ liệu là bằng chứng bổ sung. Trong lần cập nhật sổ tay này, thuật toán lõi không đổi; sửa MD / PDF không có nghĩa vừa sinh ra một thuật toán mới hoặc một lần đánh giá mới.

### 7.3. Worker và Windows

Batch dùng ProcessPoolExecutor để xử lý nhiều ảnh bằng các process. Worker không phải một thành viên nhóm và không phải một mô hình ML; nó là tiến trình thực thi hàm trên các ảnh khác nhau. Mặc định 4 worker, được giới hạn theo CPU. Trong worker, OpenCV được giới hạn một luồng để giảm cạnh tranh luồng.

Trên Windows, tiến trình con cần cơ chế khởi tạo phù hợp; entrypoint đặt trong `if __name__ == "__main__"` để không tự khởi tạo batch lặp khi import. Hàm chạy trên worker cần có thể được truyền/khởi tạo đúng; không tùy tiện chuyển nó thành một closure khó serialize rồi mong vẫn chạy.

### 7.4. Thời gian đo gồm gì?

Trong `evaluate_one`, đồng hồ bắt đầu trước đọc ảnh và dừng sau pipeline; số pipeline_ms bao gồm đọc/xử lý theo hàm này. Nhiều ảnh chạy song song nên tổng mọi pipeline_ms không bằng thời gian chờ thực tế của toàn batch. Khởi tạo process, ghi file và tranh chấp máy cũng tác động thời gian.

Nếu mục tiêu là so tốc độ thuật toán, cần cùng input /cấu hình/điều kiện luồng và phạm vi đo; có thể cần warm-up và lặp nhiều lần. Không lấy một con số của máy khác rồi khẳng định phần mềm nhanh hơn mà không thống nhất cách đo.

### 7.5. Thực nghiệm lỗi phải dừng hoặc được ghi rõ

Đường đọc ảnh hiện báo lỗi nếu không mở được; không có quy trình âm thầm bỏ file hỏng rồi vẫn tuyên bố đủ dataset. Khi kiểm hoàn tất, so tập đường dẫn CSV với tập ảnh chính và kiểm 5538 hàng duy nhất. Nếu lượt chạy bị ngắt, phải đọc completed_scope và log trước khi gọi kết quả là full.

Những file cũ vẫn có thể nằm trong results. Tồn tại trên ổ đĩa không có nghĩa chúng thuộc cùng lần chạy. TV5 cần phân biệt thư mục hiện hành với các thư mục di sản như tables, figures, edge_evaluation_output và dùng manifest để truy nguồn.

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

## 9. Câu hỏi ôn tập có gợi ý trả lời cho TV5

**Câu 1 — Dataset đang có 5538 hay 5548 ảnh?** Có 5538 ảnh khác nhau trong hai lớp chính; 5548 đường dẫn trong `kaggle/data/` vì có 10 bản sao trùng byte. Đánh giá không đếm lặp các bản sao.

**Câu 2 — Thiếu 92 ảnhso với metadata thì nói nguyên nhân gì?** Chưa biết nếu không có bằng chứng. Nêu 30 ảnhlớp 0 và 62 ảnhlớp 1 chênh lệch, không tự khẳng định đã loại ảnh lỗi.

**Câu 3 — Hash khác có nghĩa hai cảnh độc lập không?** Không. Crop chồng lấn hoặc nén lại có thể đổi byte; cần thông tin cảnh/không gian/thời gian để đánh giá độc lập.

**Câu 4 — Class_1 có cho mask dầu không?** Không. Nó là nhãn cấp ảnh; cần gán chuẩn pixel riêng để đánh giá diện tích/biên bằng IoU/Dice.

**Câu 5 — ENL mean 100, variance 400 bằng bao nhiêu?** 25. Nếu variance 100 và mean vẫn 100 thì 100; phải kiểm ROI và việc mất chi tiết trước khi gọi là cải thiện tổng thể.

**Câu 6 — ENL 999 có phải 999 look thật?** Không. Đó là giá trị code trả khi variance gần 0, một sentinel cần diễn giải riêng.

**Câu 7 — SSI 0,5 có nghĩa loại đúng 50% nhiễu?** Không. SSI 0,5 là tỷ số hệ số biến thiên sau/trước bằng 0,5. Biên thật cũng tác động std.

**Câu 8 — Entropy 8 bit có chứng minh ảnh tốt nhất?** Không. Histogram rất đa dạng, kể cả nhiễu, có thể cho entropy cao. Chỉ số không hiểu hình dạng dầu.

**Câu 9 — AMBE 0 có nghĩa ảnh không đổi?** Không. Chỉ mean bằng nhau; [80,120] và [0,200] là phản ví dụ.

**Câu 10 — EPI 1 có chứng minh đúng vị trí biên?** Không. Nó so tổng trị tuyệt đối Laplacian, không so vị trí. Nhiễu có thể bù đáp ứng bị mất.

**Câu 11 — Metrics có đổi khi bật unsharp không?** Có thể, vì đo displayed; mask có thể giữ nguyên do nhánh xử lý khác.

**Câu 12 — Tại sao so lọc lại tắt enhancement?** Để giảm yếu tố gây nhiễu khi muốn xem tác động riêng của bộ lọc. Nếu đổi nhiều bước, không biết tác dụng đến từ đâu.

**Câu 13 — Seed 2026 có đảm bảo mọi máy cho runtime giống nhau?** Không. Seed giúp chuỗi ngẫu nhiên, không cố định tải CPU, phiên bản thư viện hay điều kiện phần cứng.

**Câu 14 — Nhiễu Gaussian bổ sung có phải toàn bộ speckle SAR?** Không. Đây là một phép khảo sát độ nhạy đơn giản, không thay thế mô hình vật lý đầy đủ.

**Câu 15 — Vì sao precision / recall không phải ML?** Chúng chỉ chia các số đếm đúng/sai. Quy tắc cổ điển cũng có thể được đánh giá; không có bước học được thêm vào bởi phép đo.

**Câu 16 — TP + FN và FP + TN phải bằng gì?** Lần lượt 1843 và 3695, đúng số nhãn hai lớp. Nếu không khớp, cần kiểm dữ liệu thiếu/trùng hoặc logic đếm.

**Câu 17 — Recall 88,93% nhưng precision 36,23% nói điều gì?** Quy tắc tìm ứng viên ở phần lớn ảnh có dầu theo nhãn, nhưng nhiều ảnh bị báo dương là Class_0. Không thể kết luận đáng tin cậy chỉ vì recall cao.

**Câu 18 — Accuracy của “luôn âm” có thể cao hơn hiện tại?** Có, do Class_0 chiếm khoảng 66,72%; nhưng recall 0 nên không tìm dầu. Đây là lý do phải đọc ma trận nhầm lẫn và mục tiêu.

**Câu 19 — `--samples-only` có đủ để dựng báo cáo toàn tập không?** Không. Phạm vi samples không chứng minh 5538 ảnh đã chạy; builder yêu cầu full và hash khớp.

**Câu 20 — Tổng pipeline_ms có phải thời gian chờ của batch 4 worker?** Không. Các khoảng đo chồng nhau khi chạy song song; còn chi phí khởi tạo và ghi file.

**Câu 21 — Sửa MD có cần chạy lại toàn dataset không?** Không nếu thuật toán/ input / config không đổi. Cần dựng lại PDF và kiểm tài liệu; không tạo một lần chạy thuật toán giả trong manifest.

**Câu 22 — Ảnh kết quả của 5538 ảnh nằm ở đâu?** Hiện có CSV từng ảnh; chưa có 5538 bộ PNG. PNG sẵn trong reproducible là ca mẫu/ca lỗi; demo cho tải ảnh được chọn.

## 10. Thực hành và trình bày của TV5

### 10.1. Năm bài có đáp án kiểm tra

**Bài A — Tính chỉ số trên dãy nhỏ.** Với [80,120] và [90,110], tính mean, std, SSI, RMS, AMBE và entropy bằng tay. Mean đều 100; std 20 và 10; SSI 0,5; AMBE 0; entropy đều 1 bit. Giải thích vì sao entropy giống nhau dù độ tương phản giảm.

**Bài B — Tái tính confusion.** Đọc CSV, lọc bốn tổ hợp (label, prediction), đếm và so với `confusion.json`. Không dùng số tổng hợp làm đầu vào để tạo ngược hàng chi tiết.

**Bài C — Tìm một FP và một FN.** Từ CSV lấy đúng đường dẫn, mở demo ở cấu hình mặc định, đọc số vùng và phân tích lý do có thể sai. Nếu thay config, ghi rõ không còn so cùng điều kiện với CSV.

**Bài D — Kiểm kê file.** Chạy `audit_dataset`, giải thích 5538 ảnh chính,10 bản sao trong `kaggle/data/sample/` và 10 mẫu demo. Đưa một cặp hash trùng làm bằng chứng, đồng thời nói rõ nó chưa chứng minh độc lập cảnh.

**Bài E — Tái lập và nguồn gốc.** Mở manifest, chỉ ra completed_scope, config, source_sha256, git_head, git_dirty, executed_at. Giải thích trường nào xác định nội dung code, trường nào xác định thời điểm và trường nào chỉ là mô tả phạm vi.

### 10.2. Kịch bản nói

Slide 4 trong 50 giây: nguồn, số lượng và giới hạn dữ liệu. Slide 15 trong 50 giây: thiết kế thí nghiệm, cách tái lập và hàng theo ảnh. Slide 17 trong 70 giây: ma trận nhầm lẫn, FP cao và phạm vi cấp ảnh. Tổng 170 giây.

Trong 30 giây demo, mở một ảnh Class_0 có ứng viên và nói đó là báo nhầm theo nhãn nguồn. Dẫn tới CSV nếu được hỏi số liệu. Không chỉ dùng 00013 thành công để thay cho đánh giá toàn tập và không gọi precision / recall là bằng chứng đã dùng ML.

### 10.3. Tiêu chí hiểu sâu

Đạt khi bạn tự tính được các chỉ số đơn giản, truy được một con số báo cáo về hàng ảnh cụ thể, phân biệt pixel-level và image-level, giải thích được một ca lỗi và nói rõ giới hạn của từng phép đo. Chưa đạt nếu chỉ thuộc những con số tổng hợp.
