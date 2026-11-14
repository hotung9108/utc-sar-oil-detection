// Run with the bundled Artifact Tool runtime. Output is a draft until visually reviewed.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const root = process.cwd();
const runtime = process.env.ARTIFACT_RUNTIME || 'C:/Users/hotung/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const { Presentation, PresentationFile } = await import(pathToFileURL(path.join(runtime, 'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const out = path.join(root, '.cache/slides-v5');
await fs.mkdir(out, {recursive:true});
const read = async p => JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
const results = await read('results/sos/evaluation.json');
const comparison = await read('results/sos/model_comparison.json');
const physical = await read('results/physical/calibration.json');
const wind = await read('results/physical/wind.json');
const dartis = await read('results/dartis/evaluation.json');
const qposd = await read('results/qposd/evaluation.json');
const qclasses = await read('results/qposd/classifier_selection.json');
const qcandidates = await read('results/qposd/detection_selection.json');
if (!qposd.complete || qposd.images.length !== 5) throw new Error('Complete QPOSD evaluation required');
if (!dartis.complete || dartis.completed !== 2290) throw new Error('Complete DARTIS evaluation required');
const deck = Presentation.create({slideSize:{width:1280,height:720}});
const FONT = 'Arial';
function text(s,t,x=72,y=180,w=1136,h=400,size=30,bold=false,color='#243447') {
  const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  shape.text=t; shape.text.style={fontFamily:FONT,fontSize:size,bold,color}; return shape;
}
function slide(title,notes) {
 const s=deck.slides.add(); s.background.fill='#FFFFFF';
 text(s,title,72,52,1136,95,42,true,'#123C56');
 text(s,String(deck.slides.items.length),1180,668,40,24,18,false,'#526777');
 s.speakerNotes.text=notes; return s;
}
function lines(s,values){values.forEach((v,i)=>text(s,v,72,185+i*105,1136,85,30));}
function table(s,values,widths,top=185,height=350){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:72,top,width:1136,height,values,columnWidths:widths});
 for(let r=0;r<values.length;r++) for(let c=0;c<values[r].length;c++) {
  const cell=t.getCell(r,c); cell.text.style={fontFamily:FONT,fontSize:26,bold:r===0,color:r===0?'#FFFFFF':'#243447'};
  cell.fill=r===0?'#123C56':r%2?'#F0F5F7':'#FFFFFF';
 }
 return t;
}
async function image(s,file){s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,file))),contentType:'image/png',alt:file,fit:'contain',position:{left:72,top:150,width:1136,height:470}});}
let s=slide('Phát hiện vết dầu tràn trên biển từ ảnh SAR','Đề 18 — NASA #6 theo tài liệu môn học. Bộ slide dùng kết quả thực nghiệm SOS đã lưu, chưa tuyên bố hoàn thành các yêu cầu còn thiếu.');
text(s,'Thực nghiệm Refined SOS\nThuật toán xử lý ảnh NumPy và đối chứng thư viện',72,250,1100,160,40);
text(s,'Bài tập lớn Xử lý ảnh • Tháng 11/2026',72,540,1000,60,26);
s=slide('Bài toán và mục tiêu ứng dụng','Nguồn: tài liệu Đề 18; NASA, https://www.nasa.gov/centers-and-facilities/jpl/nasa-noaa-tech-will-aid-marine-oil-spill-response/ (2021). MOST là bối cảnh ứng dụng; chưa xác minh đồng nhất với thử thách NASA #6.');
lines(s,['Phát hiện sớm vùng nghi dầu ngoài khơi để hỗ trợ kiểm tra.','NASA–NOAA MOST hướng tới phát hiện, bản đồ phạm vi và đặc trưng độ dày dầu.','Nhóm đánh giá vùng trên SOS; chưa đo độ dày hoặc dự báo dầu vào bờ.']);
s=slide('Yêu cầu Đề 18 và phạm vi đã kiểm chứng','Nguồn: docs/MUC_TIEU_DU_AN.md; docs/management/completion_audit.json.');
table(s,[['Yêu cầu','Trạng thái'],['Lọc và chuẩn hóa góc tới','Đã lọc SOS, hiệu chuẩn SAR minh họa riêng'],['Ngưỡng thích nghi và đặc trưng vùng','Có Niblack, 8 đặc trưng; validation riêng'],['SVM/CART, dầu và tương tự dầu','Có dầu/nền SOS; thiếu nhãn loại look-alike']], [420,716]);
s=slide('Dữ liệu và nhãn tham chiếu','Nguồn: https://zenodo.org/records/15298010; docs/management/refined_sos_audit.json. Nhãn được tác giả hiệu chỉnh; không coi là xác nhận hóa học hay hiện trường.');
lines(s,['8.070 cặp PNG–mask, kích thước 256×256.','Mask nhị phân chính: giá trị ≥128 là dầu; kiểm tra thêm 64 và 192.','Thiếu mã cảnh, góc tới, thời gian và tọa độ để ghép gió.','Kiểm tra trùng hoàn toàn không loại trừ patch chồng lấn.']);
s=slide('Chia dữ liệu trước khi chọn cấu hình','Nguồn: data/manifest.json; docs/GIAO_THUC_THUC_NGHIEM.md. Seed 2026. Publisher Sentinel val được dùng làm test dự án; không phải validation chọn cấu hình. PALSAR train 3101 ảnh chưa dùng fit.');
table(s,[['Tập','Số ảnh','Vai trò'],['Sentinel train','2.683','Fit và chuẩn hóa đặc trưng'],['Sentinel validation','671','Chọn cấu hình'],['Sentinel test','839','Đánh giá cấu hình đã khóa'],['PALSAR external test','776','Khảo sát chuyển sensor']], [440,200,496]);
s=slide('Đánh giá mức đối tượng','Nguồn: src/sar_oil/evaluation.py. Ghép một-một ưu tiên số cặp hợp lệ, sau đó tổng IoU. Không dùng IoU pixel thay F1 đối tượng.');
lines(s,['Đối tượng: thành phần liên thông 8 trên mask.','Ghép một–một khi IoU ≥0,5; tính tổng TP, FP, FN.','Precision = TP/(TP+FP)     Recall = TP/(TP+FN)','F1 = 2TP/(2TP+FP+FN); mẫu số 0 được ghi không xác định.']);
s=slide('Không gian khảo sát và quy tắc lựa chọn','Nguồn: results/sos/screen.json; validation.json; selected.json. Tìm kiếm theo giai đoạn, không phải mọi tổ hợp. Khoảng F1 0,005 là quy ước, không phải định lý hay tương đương thống kê.');
lines(s,['110 cấu hình lọc × ngưỡng trên 671 ảnh validation.','Giữ 3 cấu hình ứng viên → 729 tổ hợp hậu xử lý, đặc trưng và classifier.','Trong khoảng F1 cách cực đại ≤0,005: ưu tiên Recall rồi thời gian.','Phân tích bổ sung công bố cả cấu hình chỉ tối đa F1.']);
s=slide('Lee chưa được chứng minh vượt mean7','Nguồn: results/sos/selection_evidence/evidence.json. Cùng Otsu, không morphology, min_area16; đây là F1 ứng viên, chưa qua classifier. Bootstrap 2000 lần theo patch, phân tích sau lựa chọn.');
table(s,[['Bộ lọc','F1 ứng viên'],['Không lọc','0,02435'],['Median 7','0,07513'],['Mean 7','0,08412'],['Lee 7, L=1','0,08426'],['Lee 7, L=4','0,08552']],[800,336],165,350);
text(s,'Khoảng 95% của Lee L4 − mean7 chứa 0: chưa đủ bằng chứng vượt trội.',72,555,1136,80,28,true);
s=slide('Cơ chế Lee và ví dụ kiểm chứng','Nguồn: src/sar_oil/core.py; results/sos/worked_example/example.json; Lee 1980 DOI 10.1109/TPAMI.1980.4766994. Biến thể cụ thể dùng noise=m²/L. L là tham số thử nghiệm PNG, không phải số looks vật lý đã biết.');
lines(s,['n = m²/L;  w = max(v−n, 0)/max(v, ε)','J = m + w(I−m): trọng số nhỏ đưa pixel về trung bình cục bộ.','Ví dụ 5×5, nền 0,2 và tâm 0,9 → giá trị tâm 0,651984.','NumPy và bản ghép SciPy: sai số lớn nhất khoảng 1,94×10⁻¹⁶.']);
s=slide('Tám đặc trưng cho mỗi vùng','Nguồn: src/sar_oil/core.py, FEATURES và features; src/sar_oil/reference.py. Chu vi theo cạnh lưới pixel. Chuẩn hóa chỉ fit trên train.');
table(s,[['Hình dạng','Cường độ'],['Tỷ lệ diện tích','Trung bình'],['Độ thuôn dài','Độ lệch chuẩn'],['Tỷ lệ lấp đầy hộp bao','Gradient Sobel ở biên'],['Độ phức tạp P²/(4πA)','Tương phản với vành nền']], [568,568]);
s=slide('CART và SVM tự cài so với thư viện','Nguồn: results/sos/model_comparison.json. Cùng đặc trưng validation; agreement=1 trên mẫu đã kiểm tra, không chứng minh tương đương mọi đầu vào.');
table(s,[['Mô hình','F1 NumPy','F1 thư viện','Agreement'],...comparison.map(r=>[r.kind.toUpperCase(),r.metrics.f1.toFixed(6),r.reference_metrics.f1.toFixed(6),r.agreement.toFixed(6)])],[290,280,280,286],185,235);
text(s,'CART: giảm Gini • SVM: squared hinge, L2 và kiểm tra hội tụ',72,480,1136,100,30);
s=slide('Kết quả trên tập kiểm tra SOS','Nguồn: results/sos/evaluation.json. 839 Sentinel test; mô hình đã khóa. Pixel IoU không phản ánh trực tiếp số đối tượng đúng.');
const m=results.test_final.metrics;
table(s,[['Precision đối tượng','Recall đối tượng','F1 đối tượng','IoU pixel'],[m.precision.toFixed(5),m.recall.toFixed(5),m.f1.toFixed(5),m.pixel_iou.toFixed(5)]],[284,284,284,284],195,180);
text(s,`TP ${m.tp}     FP ${m.fp}     FN ${m.fn}\nF1 đối tượng còn thấp dù IoU pixel đạt ${m.pixel_iou.toFixed(3)}.`,72,450,1136,140,34);
s=slide('Tác dụng và đánh đổi của bộ phân lớp','Nguồn: results/sos/evaluation.json, test_no_classifier và test_final. Giữ nguyên tạo ứng viên; không suy ra tác dụng riêng của Lee từ ablation này.');
const ab=results.test_no_classifier.metrics;
table(s,[['Cấu hình','TP','FP','F1'],['Bỏ classifier',String(ab.tp),String(ab.fp),ab.f1.toFixed(5)],['Có classifier',String(m.tp),String(m.fp),m.f1.toFixed(5)]],[480,210,210,236],185,235);
text(s,`Giảm ${ab.fp-m.fp} báo sai, đồng thời mất ${ab.tp-m.tp} phát hiện đúng.`,72,490,1136,100,34,true);
s=slide('Niblack: validation và phép thử PALSAR bổ sung','Nguồn: results/sos/adaptive/selected.json; validation_full_numpy.json; results/sos/external_palsar_train/{protocol,otsu,niblack}.json; notebook 09. Hai pipeline cố định chạy đủ 3101 external_train PALSAR, không fit lại hoặc chọn mô hình từ phép thử. Không có mã cảnh để chứng minh độc lập theo cảnh; không quy chênh lệch riêng cho ngưỡng vì Lee và classifier cũng khác.');
text(s,'Niblack51 k=0,2 + Lee7 L1 + CART depth3/leaf5.\n27 cấu hình đã khảo sát; F1 validation Sentinel = 0,14466.',72,165,1136,100,29);
const palsarRows=[['Pipeline cố định','F1 trên 3.101 patch PALSAR']];
for(const [name,label] of [['otsu','Otsu–SVM'],['niblack','Niblack–CART']]) {
 const result=await read(`results/sos/external_palsar_train/${name}.json`);
 if(!result.complete || result.completed!==3101) throw new Error('Incomplete PALSAR evaluation');
 palsarRows.push([label,result.metrics.f1.toFixed(5)]);
}
table(s,palsarRows,[568,568],300,220);
text(s,'Phép thử chuyển sensor; chưa chứng minh độc lập theo cảnh.\nKhông diễn giải thành ưu thế riêng của thuật toán ngưỡng.',72,555,1136,90,27,true);
s=slide('Phân mảnh làm F1 đối tượng thấp','Nguồn: results/sos/diagnostics/diagnostics.json; test image val/sentinel_440. GT phủ toàn patch. 35 FP đối tượng có thể nằm trong pixel dầu nhưng không ghép được với GT lớn.');
await image(s,'results/sos/diagnostics/failure_1.png');
text(s,'GT phủ patch, dự đoán bị phân mảnh: TP=0, FP=35, FN=1.',72,635,1136,45,25);
s=slide('Bỏ sót vùng dầu lớn','Nguồn: results/sos/diagnostics/diagnostics.json; test image val/sentinel_591. Không suy đoán nguyên nhân vật lý từ ảnh PNG.');
await image(s,'results/sos/diagnostics/failure_3.png');
text(s,'Classifier loại hết ứng viên: TP=0, FP=0, FN=1.',72,635,1136,45,25);
s=slide('Hiệu chuẩn Sentinel-1 và gió ERA5','Nguồn: results/physical/calibration.json, wind.json; notebooks/external/07_sentinel_calibration.ipynb. Tham chiếu nội suy SciPy dùng cùng lưới/công thức, chưa đối chiếu SNAP độc lập. Chưa loại nhiễu nhiệt. Gió ô lưới cách tâm tile 13,6223 km, không phải đo hiện trường.');
lines(s,[`Tile ${physical.shape.join('×')}, góc tới ${physical.angle_min.toFixed(4)}–${physical.angle_max.toFixed(4)} độ.`,
 `NumPy và SciPy: sai số gamma0 tối đa ${physical.checks.gamma_calibrated.max_abs.toExponential(2)}.`,
 `Gió ERA5 ghép theo tâm tile: ${wind.speed_m_s.toFixed(4)} m/s.`,
 'Chưa có nhãn dầu trên tile để đo tác động lên F1.']);
s=slide('Ứng dụng demo và video','Nguồn: scripts/demo_qt.py; docs/management/gui_audit.json; deliverables/video/SAR_demo_v1.mp4; video_audit.json và video_visual_review.json. Kiểm tra Qt tự động, chưa kiểm tra thủ công hộp thoại hệ điều hành. Video ghi tự động, không thay thế thuyết trình của thành viên.');
lines(s,['PyQt chạy mô hình NumPy đã khóa, có hai nhánh Otsu và Niblack.',
 'Hiển thị ảnh trung gian, đặc trưng vùng và đối chiếu mask.',
 'Xuất mask, overlay, JSON. Thay mask tham chiếu không đổi dự đoán.',
 'Video 6 phút có phụ đề tiếng Việt, không âm thanh.']);
s=slide('DARTIS: báo nhầm khi chuyển miền dữ liệu','Nguồn: results/dartis/evaluation.json, REPORT.md, protocol.json; notebook 06. Đủ 2.290 ảnh no-oil, mô hình SOS cố định, giữ ảnh 640×640. Reporter đã kiểm tra hash và tổng hợp lại từng ảnh. Đây là tỷ lệ báo nhầm mức ảnh, không phải Recall dầu hoặc F1 đối tượng. Không chỉnh tham số theo kết quả này.');
const negativeGroups=[['Toàn bộ',dartis.overall],['Bờ',dartis.by_subset.nc],['Biển',dartis.by_subset.nw]];
table(s,[['Tập no-oil','Ảnh báo nhầm / tổng','Tỷ lệ'],...negativeGroups.map(([name,r])=>[name,`${r.false_alarm_images} / ${r.images}`,`${(100*r.false_alarm_rate).toFixed(2)}%`])],[340,480,316],175,290);
text(s,'Báo nhầm cao: chưa phù hợp triển khai trực tiếp ngoài tập SOS.\nKhông dùng tỷ lệ này thay F1 đối tượng hoặc nhãn nguyên nhân.',72,510,1136,120,29,true);
s=slide('QPOSD bổ sung nhãn dầu và tương tự dầu','Nguồn: https://zenodo.org/records/19258036 (CC BY 4.0); results/qposd/protocol.json; docs/management/qposd_overlap_all24.json. Đã kiểm tra CRC/hash, hữu hạn và xem toàn bộ 24 cặp hợp lệ. V1 bị từ chối trước fit vì giao trùng 21/22 vượt split. V2 giữ nhóm {19,20}, {21,22,33,35}; chưa chứng minh độc lập cảnh. Test đã được xem để kiểm tra ảnh–nhãn, không phải đánh giá mù.');
lines(s,['UAVSAR L-band: dùng 24 cặp khớp kích thước, loại 17 cặp lệch.',
 '14 ảnh train / 5 validation / 5 test; giữ nhóm giao trùng cùng tập.',
 'Nhãn tương tự dầu chung; chưa có nhãn nguyên nhân vật lý.',
 'SOS vẫn là tập chính; chưa đánh giá trên biển miền Trung.']);
s=slide('Lựa chọn QPOSD dựa trên validation','Nguồn: results/qposd/classifier_selection.json, detection_selection.json. Bảng chỉ trích bốn dòng; toàn bộ 10 classifier và 10 cấu hình tạo vùng có trong notebook 10. Hàng phân lớp dùng hình học GT; hàng tạo vùng dùng macro-F1 đối tượng IoU>=0.5, cùng CART đã khóa, không so trực tiếp hai phép đo. Cả 10 classifier NumPy hội tụ; chọn CART depth5/min_leaf1. Không lọc + Otsu thắng tìm vùng; ảnh đặc trưng vẫn dùng Lee7L4. Không chứng minh Lee luôn tốt hơn.');
const qclass8=qclasses.configurations[8],qclass9=qclasses.configurations[9];
const qdet0=qcandidates.configurations[0],qdet4=qcandidates.configurations[4];
table(s,[['Phép đo / cấu hình','F1 NumPy','F1 thư viện'],
 ['Có sẵn vùng: CART d5, lá1',qclass8.numpy_validation.macro_f1.toFixed(5),qclass8.reference_validation.macro_f1.toFixed(5)],
 ['Có sẵn vùng: CART d5, lá5',qclass9.numpy_validation.macro_f1.toFixed(5),qclass9.reference_validation.macro_f1.toFixed(5)],
 ['Tìm vùng: không lọc + Otsu',qdet0.numpy_summary.macro_f1.toFixed(5),qdet0.reference_summary.macro_f1.toFixed(5)],
 ['Tìm vùng: Niblack 51, k=0,5',qdet4.numpy_summary.macro_f1.toFixed(5),qdet4.reference_summary.macro_f1.toFixed(5)]],[650,243,243],175,330);
text(s,'Trích 4 dòng từ 10 bộ phân lớp và 10 cấu hình tạo vùng.\nF1 phân lớp có sẵn vùng không thay thế F1 phát hiện.',72,540,1136,100,29,true);
s=slide('QPOSD trên toàn bộ năm ảnh test','Nguồn: results/qposd/evaluation.json, REPORT.md; notebook 10. Lựa chọn lưu và commit trước test. Phát hiện dầu TP3 FP35 FN12, tương tự dầu TP6 FP658 FN172. Phân lớp có sẵn vùng: ma trận [look-alike, oil] [[125,53],[6,9]], oil->look-alike40%, look-alike->oil29.7753%. Không dùng ma trận có điều kiện thay Recall phát hiện.');
const qtestRows=[];
for(const [title,result] of [['Có sẵn vùng',qposd.conditional_classification],['Phát hiện',qposd.numpy_summary]])
 for(const [name,r] of Object.entries(result.classes)) qtestRows.push([`${title}: ${name==='oil'?'dầu':'tương tự dầu'}`,...['precision','recall','f1'].map(k=>r[k].toFixed(5))]);
table(s,[['Phép đo / lớp','Precision','Recall','F1'],...qtestRows],[530,202,202,202],175,330);
text(s,'Hai bản cài cho mask giống nhau từng pixel trên 5 ảnh test.\nPhát hiện vẫn kém; không điều chỉnh mô hình từ điểm test.',72,540,1136,100,29,true);
s=slide('QPOSD ảnh 24: tương tự dầu bị gọi là dầu','Nguồn: notebooks/external/10_qposd_classification_detection.ipynb, hình ảnh test24 đã chạy và đối chiếu mask. T11 đổi log chỉ để hiển thị. Nhãn gốc xanh lá=tương tự dầu, đỏ=dầu, xanh lam=nền, đen=đất liền. Dự đoán không dùng GT để che đất. Đây là ví dụ thất bại có chủ đích, không phải mẫu đại diện ngẫu nhiên hoặc bằng chứng nguyên nhân vật lý.');
const qnb=await read('notebooks/external/10_qposd_classification_detection.ipynb');
const qfigs=qnb.cells.flatMap(c=>(c.outputs||[]).filter(o=>o.data?.['image/png']).map(o=>o.data['image/png']));
if(qfigs.length!==7) throw new Error('Expected seven executed QPOSD figures');
await fs.writeFile(path.join(out,'qposd_image24.png'),Buffer.from(qfigs[5],'base64'));
await image(s,'.cache/slides-v5/qposd_image24.png');
text(s,'Nhãn xanh lá: tương tự dầu. Nhiều vùng bị dự đoán đỏ: dầu.',72,635,1136,45,25);
s=slide('Đóng góp và phân công kiểm tra','Nguồn: docs/management/thanh_vien.json; PHAN_CONG_MA_NGUON.md. Đây là phân công dự kiến, không thay cho xác nhận đóng góp cá nhân. Mã và báo cáo có hỗ trợ Codex; thành viên cần đọc, chạy lại và xác nhận.');
table(s,[['Phụ trách','Nội dung'],['TV1 / TV2','Tích hợp pipeline / CART và SVM'],['TV3 / TV4','Lọc, ngưỡng / Vùng và đặc trưng'],['TV5','Dữ liệu, đánh giá và kiểm chứng']], [400,736],175,280);
text(s,'Kết quả có thể chạy lại, so sánh hai cách cài và truy số đếm từng ảnh.\nChưa đủ bằng chứng triển khai cảnh báo dầu ngoài thực địa.',72,515,1136,120,29,true);
if(deck.slides.items.length!==24) throw new Error('Expected 24 slides');
await (await PresentationFile.exportPptx(deck)).save(path.join(out,'SAR_SOS_draft.pptx'));
for(let i=0;i<deck.slides.items.length;i++) {
 const blob=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 console.log(`Rendered ${i+1}/24`);
}
console.log('Draft exported; finalization and visual review remain.');
