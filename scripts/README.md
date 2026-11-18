# Scripts — tìm theo việc cần làm

Đã bỏ 12 script sinh/vá/chạy riêng notebook và 21 script Python tạm dùng một lần trong `.cache/`. Chỉnh trực tiếp các file trong `notebooks/`, chạy lại bằng `python scripts/run_notebooks.py --all`. `run_experiments.py` sử dụng notebook đã lưu, không sinh đè nội dung.

## Các lệnh thường dùng

```powershell
python scripts/tasks.py list
python scripts/tasks.py list --group cantarell
python scripts/tasks.py run sos/sos -- --help
python scripts/tasks.py run notebooks/run_notebooks -- --all
```

`list` chỉ đọc danh mục, không chạy thí nghiệm. `run` chạy đúng công cụ đã chọn và chuyển tiếp tham số; xem hướng dẫn công cụ trước khi chạy vì các lệnh train/build/download có tác dụng ghi tệp. Dùng Python trong `.venv` hoặc `uv run --frozen --extra web python` nếu terminal chưa kích hoạt môi trường.

## Cấu trúc vật lý

| Thư mục | Nội dung |
|---|---|
| `web/` | Adapter và giải thích Streamlit; kiểm tra trình duyệt |
| `publishing/` | Công cụ báo cáo, LaTeX, slide, video; tách khỏi công việc xử lý ảnh |
| `packaging/` | Đóng gói bàn giao và kiểm tra bản lưu |
| `nasa_crawler/` | Công cụ thu thập nguồn NASA có sẵn |
| `sos_experiments/` | Benchmark, phân tích và kiểm chứng SOS/PALSAR; dùng tên khác `sos.py` để tránh xung đột import |
| `cantarell/` | Sentinel-1 vật lý: dữ liệu → huấn luyện → đánh giá |
| `qposd/` | Dầu / tương tự dầu, đặc trưng và phân lớp |
| `dartis/` | Dữ liệu và đánh giá báo động giả |
| `physical/` | Metadata Sentinel-1, hiệu chuẩn và gió |
| `validation/` | Kiểm tra output và tái tạo bằng chứng |
| `desktop/` | Demo Qt cũ và engine dùng chung |
| File tại gốc `scripts/` | Chỉ còn ba lệnh `sos.py`, `run_notebooks.py`, `tasks.py`, hai module nội bộ `_paths.py`/`_provenance.py` và danh mục/hướng dẫn |

Đã chuyển tổng cộng 98 file vào nhóm chức năng. Không còn giữ 67 script nghiên cứu ở cấp gốc như phương án trước. Import, notebook và các lệnh gọi nhau dùng đường dẫn mới.

Kết quả thực nghiệm cũ giữ nguyên. Bản đồ di chuyển ghi riêng SHA-256 cũ và mới; `_provenance.py` chỉ chấp nhận nguồn đã chuyển khi nội dung hiện tại khớp chính xác bản ghi này. Hash mới không bị giả thành hash cũ. Đổi thuật toán sau lần di chuyển sẽ làm kiểm tra thất bại; dữ liệu, mô hình và giao thức vẫn kiểm tra hash thực như trước. Xem [chi tiết chuyển cấu trúc](../docs/CAU_TRUC_DU_AN.md).

Các đường dẫn cũ của công cụ đã chuyển được ghi trong [bản đồ di chuyển](../docs/management/script_reorganization.json); sử dụng đường dẫn mới. Lệnh chính `scripts/sos.py`, `scripts/run_notebooks.py` vẫn hoạt động.

## Thực nghiệm Sentinel-1 vật lý

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `cantarell/analyze_cantarell_failures` | [cantarell/analyze_cantarell_failures.py](cantarell/analyze_cantarell_failures.py) |
| `cantarell/audit_cantarell_all` | [cantarell/audit_cantarell_all.py](cantarell/audit_cantarell_all.py) |
| `cantarell/audit_cantarell_source` | [cantarell/audit_cantarell_source.py](cantarell/audit_cantarell_source.py) |
| `cantarell/cantarell_experiment_data` | [cantarell/cantarell_experiment_data.py](cantarell/cantarell_experiment_data.py) |
| `cantarell/cantarell_pipeline` | [cantarell/cantarell_pipeline.py](cantarell/cantarell_pipeline.py) |
| `cantarell/check_cantarell_registration` | [cantarell/check_cantarell_registration.py](cantarell/check_cantarell_registration.py) |
| `cantarell/check_cantarell_transfer` | [cantarell/check_cantarell_transfer.py](cantarell/check_cantarell_transfer.py) |
| `cantarell/evaluate_cantarell` | [cantarell/evaluate_cantarell.py](cantarell/evaluate_cantarell.py) |
| `cantarell/fetch_cantarell_native` | [cantarell/fetch_cantarell_native.py](cantarell/fetch_cantarell_native.py) |
| `cantarell/fetch_cantarell_physical_metadata` | [cantarell/fetch_cantarell_physical_metadata.py](cantarell/fetch_cantarell_physical_metadata.py) |
| `cantarell/fetch_cantarell_wind` | [cantarell/fetch_cantarell_wind.py](cantarell/fetch_cantarell_wind.py) |
| `cantarell/freeze_cantarell_data_protocol` | [cantarell/freeze_cantarell_data_protocol.py](cantarell/freeze_cantarell_data_protocol.py) |
| `cantarell/freeze_cantarell_model_protocol` | [cantarell/freeze_cantarell_model_protocol.py](cantarell/freeze_cantarell_model_protocol.py) |
| `cantarell/map_cantarell_native_grid` | [cantarell/map_cantarell_native_grid.py](cantarell/map_cantarell_native_grid.py) |
| `cantarell/prepare_cantarell_physical` | [cantarell/prepare_cantarell_physical.py](cantarell/prepare_cantarell_physical.py) |
| `cantarell/report_cantarell_inventory` | [cantarell/report_cantarell_inventory.py](cantarell/report_cantarell_inventory.py) |
| `cantarell/report_cantarell_physical` | [cantarell/report_cantarell_physical.py](cantarell/report_cantarell_physical.py) |
| `cantarell/resolve_cantarell_scenes` | [cantarell/resolve_cantarell_scenes.py](cantarell/resolve_cantarell_scenes.py) |
| `cantarell/screen_cantarell` | [cantarell/screen_cantarell.py](cantarell/screen_cantarell.py) |
| `cantarell/select_cantarell_required_filter` | [cantarell/select_cantarell_required_filter.py](cantarell/select_cantarell_required_filter.py) |
| `cantarell/train_cantarell` | [cantarell/train_cantarell.py](cantarell/train_cantarell.py) |
| `cantarell/verify_cantarell_operators` | [cantarell/verify_cantarell_operators.py](cantarell/verify_cantarell_operators.py) |
| `cantarell/verify_cantarell_results` | [cantarell/verify_cantarell_results.py](cantarell/verify_cantarell_results.py) |

## Kiểm tra báo động giả

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `dartis/audit_dartis` | [dartis/audit_dartis.py](dartis/audit_dartis.py) |
| `dartis/audit_dartis_geolocation` | [dartis/audit_dartis_geolocation.py](dartis/audit_dartis_geolocation.py) |
| `dartis/dartis_results` | [dartis/dartis_results.py](dartis/dartis_results.py) |
| `dartis/download_dartis` | [dartis/download_dartis.py](dartis/download_dartis.py) |
| `dartis/evaluate_dartis` | [dartis/evaluate_dartis.py](dartis/evaluate_dartis.py) |
| `dartis/report_dartis` | [dartis/report_dartis.py](dartis/report_dartis.py) |

## Demo desktop cũ

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `desktop/demo_engine` | [desktop/demo_engine.py](desktop/demo_engine.py) |
| `desktop/demo_qt` | [desktop/demo_qt.py](desktop/demo_qt.py) |
| `desktop/verify_demo_qt` | [desktop/verify_demo_qt.py](desktop/verify_demo_qt.py) |

## Chạy notebook

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `notebooks/run_notebooks` | [run_notebooks.py](run_notebooks.py) |

## Đóng gói và lưu trữ

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `packaging/build_review_package` | [packaging/build_review_package.py](packaging/build_review_package.py) |
| `packaging/verify_archive` | [packaging/verify_archive.py](packaging/verify_archive.py) |
| `packaging/verify_package_environment` | [packaging/verify_package_environment.py](packaging/verify_package_environment.py) |
| `packaging/verify_review_package` | [packaging/verify_review_package.py](packaging/verify_review_package.py) |

## Metadata, hiệu chuẩn và gió

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `physical/fetch_scene_wind` | [physical/fetch_scene_wind.py](physical/fetch_scene_wind.py) |
| `physical/fetch_sentinel_metadata` | [physical/fetch_sentinel_metadata.py](physical/fetch_sentinel_metadata.py) |
| `physical/fetch_sentinel_window` | [physical/fetch_sentinel_window.py](physical/fetch_sentinel_window.py) |
| `physical/sentinel_calibration_demo` | [physical/sentinel_calibration_demo.py](physical/sentinel_calibration_demo.py) |

## Xuất bản tài liệu (không cần để chạy dự án)

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `publishing/audit_report_render` | [publishing/audit_report_render.py](publishing/audit_report_render.py) |
| `publishing/build_report` | [publishing/build_report.py](publishing/build_report.py) |
| `publishing/build_slides` | [publishing/build_slides.mjs](publishing/build_slides.mjs) |
| `publishing/finalize_slides` | [publishing/finalize_slides.mjs](publishing/finalize_slides.mjs) |
| `publishing/generate_latex_figures` | [publishing/generate_latex_figures.py](publishing/generate_latex_figures.py) |
| `publishing/import_report_fields` | [publishing/import_report_fields.py](publishing/import_report_fields.py) |
| `publishing/inspect_report_template` | [publishing/inspect_report_template.py](publishing/inspect_report_template.py) |
| `publishing/record_demo_video` | [publishing/record_demo_video.py](publishing/record_demo_video.py) |
| `publishing/report_figures` | [publishing/report_figures.py](publishing/report_figures.py) |
| `publishing/update_report_fields` | [publishing/update_report_fields.ps1](publishing/update_report_fields.ps1) |
| `publishing/verify_demo_video` | [publishing/verify_demo_video.py](publishing/verify_demo_video.py) |
| `publishing/verify_report_sources` | [publishing/verify_report_sources.py](publishing/verify_report_sources.py) |

## Thực nghiệm dầu / tương tự dầu

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `qposd/audit_qposd` | [qposd/audit_qposd.py](qposd/audit_qposd.py) |
| `qposd/audit_qposd_objects` | [qposd/audit_qposd_objects.py](qposd/audit_qposd_objects.py) |
| `qposd/audit_qposd_overlap` | [qposd/audit_qposd_overlap.py](qposd/audit_qposd_overlap.py) |
| `qposd/audit_qposd_shapes` | [qposd/audit_qposd_shapes.py](qposd/audit_qposd_shapes.py) |
| `qposd/benchmark_qposd_features` | [qposd/benchmark_qposd_features.py](qposd/benchmark_qposd_features.py) |
| `qposd/evaluate_qposd_test` | [qposd/evaluate_qposd_test.py](qposd/evaluate_qposd_test.py) |
| `qposd/extract_qposd_regions` | [qposd/extract_qposd_regions.py](qposd/extract_qposd_regions.py) |
| `qposd/inspect_qposd_features` | [qposd/inspect_qposd_features.py](qposd/inspect_qposd_features.py) |
| `qposd/prepare_qposd_protocol` | [qposd/prepare_qposd_protocol.py](qposd/prepare_qposd_protocol.py) |
| `qposd/preview_qposd_pairs` | [qposd/preview_qposd_pairs.py](qposd/preview_qposd_pairs.py) |
| `qposd/qposd_fast_features` | [qposd/qposd_fast_features.py](qposd/qposd_fast_features.py) |
| `qposd/qposd_labels` | [qposd/qposd_labels.py](qposd/qposd_labels.py) |
| `qposd/qposd_metrics` | [qposd/qposd_metrics.py](qposd/qposd_metrics.py) |
| `qposd/qposd_pipeline` | [qposd/qposd_pipeline.py](qposd/qposd_pipeline.py) |
| `qposd/report_qposd` | [qposd/report_qposd.py](qposd/report_qposd.py) |
| `qposd/select_qposd_detection` | [qposd/select_qposd_detection.py](qposd/select_qposd_detection.py) |
| `qposd/train_qposd_classifiers` | [qposd/train_qposd_classifiers.py](qposd/train_qposd_classifiers.py) |

## Thực nghiệm SOS

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `sos/adaptive_experiment` | [sos_experiments/adaptive_experiment.py](sos_experiments/adaptive_experiment.py) |
| `sos/analyze_failures` | [sos_experiments/analyze_failures.py](sos_experiments/analyze_failures.py) |
| `sos/audit_palsar_holdout` | [sos_experiments/audit_palsar_holdout.py](sos_experiments/audit_palsar_holdout.py) |
| `sos/audit_refined_sos` | [sos_experiments/audit_refined_sos.py](sos_experiments/audit_refined_sos.py) |
| `sos/evaluate_palsar_holdout` | [sos_experiments/evaluate_palsar_holdout.py](sos_experiments/evaluate_palsar_holdout.py) |
| `sos/explain_selection` | [sos_experiments/explain_selection.py](sos_experiments/explain_selection.py) |
| `sos/report_palsar_holdout` | [sos_experiments/report_palsar_holdout.py](sos_experiments/report_palsar_holdout.py) |
| `sos/sos` | [sos.py](sos.py) |
| `sos/summarize_results` | [sos_experiments/summarize_results.py](sos_experiments/summarize_results.py) |
| `sos/verify_real_data` | [sos_experiments/verify_real_data.py](sos_experiments/verify_real_data.py) |
| `sos/worked_example` | [sos_experiments/worked_example.py](sos_experiments/worked_example.py) |

## Kiểm tra kết quả

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `validation/rebuild_evidence` | [validation/rebuild_evidence.py](validation/rebuild_evidence.py) |
| `validation/verify_outputs` | [validation/verify_outputs.py](validation/verify_outputs.py) |

## Giao diện web

| Tên lệnh sau `tasks.py run` | File |
|---|---|
| `web/streamlit_physical` | [web/streamlit_physical.py](web/streamlit_physical.py) |
| `web/streamlit_qposd` | [web/streamlit_qposd.py](web/streamlit_qposd.py) |
| `web/streamlit_service` | [web/streamlit_service.py](web/streamlit_service.py) |
| `web/streamlit_ux` | [web/streamlit_ux.py](web/streamlit_ux.py) |
| `web/verify_streamlit_browser` | [web/verify_streamlit_browser.py](web/verify_streamlit_browser.py) |
