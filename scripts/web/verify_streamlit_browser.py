"""Optional browser smoke check. Start Streamlit at 127.0.0.1:8501 first.

Run: uv run --no-project --with playwright python scripts/web/verify_streamlit_browser.py
Uses installed Microsoft Edge; screenshots remain under ignored .cache/.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path('.cache/streamlit_ux')
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1050}, device_scale_factor=1)
    page.goto('http://127.0.0.1:8501')
    page.get_by_role('button', name='Phân tích ảnh', exact=True).wait_for(timeout=60000)
    page.screenshot(path=str(out/'01_input.png'), full_page=True)
    page.get_by_role('button', name='Phân tích ảnh', exact=True).click()
    page.get_by_text('2. Đọc kết quả phân tích', exact=True).wait_for(timeout=60000)
    page.get_by_text('2. Đọc kết quả phân tích', exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(out/'02_result.png'), full_page=True)
    page.get_by_role('tab', name='Đối chiếu nhãn', exact=True).click()
    page.get_by_text('Phát hiện đúng:', exact=False).scroll_into_view_if_needed()
    page.screenshot(path=str(out/'03_truth.png'), full_page=True)
    assert page.get_by_text('Phát hiện đúng:', exact=False).count() > 0
    page.get_by_text('Bằng chứng thực nghiệm', exact=True).click()
    page.get_by_text('Chất lượng trên tập kiểm tra', exact=True).wait_for()
    page.get_by_text('Chất lượng trên tập kiểm tra', exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(out/'04_evidence.png'), full_page=True)
    page.get_by_test_id('stRadioGroup').get_by_text('Phạm vi và hướng dẫn', exact=True).click()
    page.get_by_text('Tôi nên chọn màn hình nào?', exact=True).wait_for()
    page.get_by_text('Tôi nên chọn màn hình nào?', exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(out/'05_help.png'), full_page=True)
    for name, action, output in [
        ('Dầu và look-alike', 'Phân tích QPOSD', '07_qposd.png'),
        ('Sentinel-1 vật lý', 'Phân tích Sentinel-1', '08_physical.png'),
    ]:
        page.get_by_test_id('stRadioGroup').get_by_text(name, exact=True).click()
        page.get_by_role('button', name=action, exact=True).click(timeout=60000)
        page.get_by_test_id('stDownloadButton').wait_for(timeout=120000)
        page.get_by_test_id('stDownloadButton').scroll_into_view_if_needed()
        assert page.get_by_test_id('stException').count() == 0
        assert page.get_by_test_id('stAlert').filter(has_text='Không thể xử lý').count() == 0
        page.screenshot(path=str(out/output), full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.reload()
    page.get_by_role('button', name='Phân tích ảnh', exact=True).wait_for()
    page.screenshot(path=str(out/'06_mobile_input.png'), full_page=True)
    assert page.locator('[data-testid="stException"]').count() == 0
    browser.close()
print('Browser flows passed; screenshots:', out)
