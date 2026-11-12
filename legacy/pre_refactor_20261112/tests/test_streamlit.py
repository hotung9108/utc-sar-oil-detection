"""Exercise the actual demo across image and edge-mode changes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_demo_switches_between_candidate_masks_and_edge_maps():
    app = AppTest.from_file(Path("streamlit_app.py").resolve(), default_timeout=30).run()
    assert not app.exception
    assert len(app.tabs) == 4

    edge = next(widget for widget in app.selectbox if widget.label == "Phương pháp biên")
    edge.set_value("canny").run()
    assert not app.exception
    assert not any(metric.label == "Số vùng ứng viên" for metric in app.metric)

    edge = next(widget for widget in app.selectbox if widget.label == "Phương pháp biên")
    edge.set_value("morphology").run()
    sample = next(widget for widget in app.selectbox if widget.label == "Hoặc chọn ảnh mẫu")
    sample.set_value(Path("kaggle/data/Class_1/class_1_00013.jpg").resolve()).run()
    assert not app.exception
    count = next(metric for metric in app.metric if metric.label == "Số vùng ứng viên")
    assert count.value == "1"
    assert len(app.dataframe) >= 2

    app.radio[0].set_value("Dataset Kaggle").run()
    assert not app.exception
    dataset = next(w for w in app.selectbox if w.label == "Chọn ảnh Kaggle")
    assert len(dataset.options) == 3695
    next(w for w in app.selectbox if w.label == "Lớp dữ liệu").set_value("Class_1").run()
    dataset = next(w for w in app.selectbox if w.label == "Chọn ảnh Kaggle")
    assert len(dataset.options) == 1843
    dataset.set_value(Path("kaggle/data/Class_1/class_1_00013.jpg").resolve()).run()
    assert not app.exception
    assert next(m for m in app.metric if m.label == "Số vùng ứng viên").value == "1"
    assert "Tiến Sơn Trần" in app.table[0].value.to_string()
