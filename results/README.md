# Kết quả mới

Kết quả mới được script tạo trong `sos/`:

- `screen.json`: 110 cấu hình lọc/ngưỡng trên validation.
- `validation.json`: 729 cấu hình vùng/đặc trưng/classifier.
- `verification.json`, `verification_real.json`: kiểm chứng NumPy/thư viện trên ca biên và ảnh SOS thật.
- `model_comparison.json`: CART/SVM NumPy và sklearn, agreement, F1, objective/hội tụ.
- `selected.json`, `cart_model.json`, `svm_model.json`: cấu hình đóng băng và mô hình portable.
- `evaluation.json` và các file theo split: test, baseline, bỏ classifier, PALSAR và độ nhạy mask; số đếm từng ảnh, seed, phiên bản thư viện.

Không chỉnh tay số liệu để tạo kết luận. CLI `reproduce` tái tạo từ dữ liệu cục bộ, dùng checkpoint cùng lần thực nghiệm. `prediction/` chứa mask/overlay/regions của một ảnh người dùng. Kết quả cũ nằm trong legacy và không được dùng như bằng chứng mới.
