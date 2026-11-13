"""Record real interactions with the local Streamlit app; no application edits."""
import asyncio,sys,os,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.cache/video_deps'))
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.cache/video_browsers')
from playwright.async_api import async_playwright
CACHE=ROOT/'.cache/video_demo'; OUT=ROOT/'docs/video'
CACHE.mkdir(parents=True,exist_ok=True);(OUT/'demo_exports').mkdir(exist_ok=True)
FAST='--preflight' in sys.argv

async def run():
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,channel='chromium')
        options=dict(viewport={'width':1600,'height':800},device_scale_factor=1,accept_downloads=True,color_scheme='light')
        if not FAST: options.update(record_video_dir=str(CACHE/'raw'),record_video_size={'width':1600,'height':800})
        context=await browser.new_context(**options)
        opened=time.monotonic()
        page=await context.new_page()
        await page.goto('http://127.0.0.1:8501')
        await page.get_by_role('tab',name='Kết quả ảnh',exact=True).wait_for(timeout=60000)
        await page.wait_for_timeout(1800)
        t0=time.monotonic(); events=[]
        async def settle():
            await page.wait_for_timeout(1000)
            assert not await page.get_by_test_id('stException').count(),'Application exception'
        async def select(label,value):
            loc=page.get_by_role('combobox',name=label,exact=True)
            await loc.scroll_into_view_if_needed(); await loc.click(); await loc.fill(value)
            await page.get_by_role('option',name=value,exact=True).click()
            await settle()
            assert await loc.input_value()==value
        async def main_scroll(y):
            await page.get_by_test_id('stMain').evaluate('(e,y)=>e.scrollTo({top:y,behavior:"smooth"})',y)
            await page.wait_for_timeout(600)
        async def sidebar_top():
            await page.get_by_test_id('stSidebarContent').evaluate('(e)=>e.scrollTo({top:0,behavior:"smooth"})')
            await page.wait_for_timeout(500)
        async def slider(label,target):
            loc=page.locator(f'input[aria-label={json.dumps(label,ensure_ascii=False)}]')
            # React Aria exposes a native range input; keyboard input changes the real widget.
            current=float(await loc.input_value())
            step=float(await loc.get_attribute('step') or 1)
            await loc.focus()
            delta=round((target-current)/step)
            if delta:
                await page.keyboard.down('ArrowRight' if delta>0 else 'ArrowLeft')
                await page.keyboard.up('ArrowRight' if delta>0 else 'ArrowLeft')
                for _ in range(abs(delta)-1): await loc.press('ArrowRight' if delta>0 else 'ArrowLeft')
            await settle()
            actual=float(await loc.input_value())
            assert abs(actual-target)<1e-4,(label,actual,target,step)
        async def tab(name):
            await page.get_by_role('tab',name=name,exact=True).click(); await settle(); await main_scroll(0)
        async def at(sec,name,action=None):
            if not FAST:
                delay=sec-(time.monotonic()-t0)
                if delay>0: await asyncio.sleep(delay)
            start=time.monotonic()-t0
            if action: await action()
            events.append({'target':sec,'start':round(start,3),'end':round(time.monotonic()-t0,3),'name':name})
            await page.screenshot(path=str(CACHE/f'{"preflight" if FAST else "shot"}_{sec:03}.png'))
            (CACHE/('preflight_events.json' if FAST else 'events.json')).write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
            print(sec,name,flush=True)
        async def choose_sample():
            await select('Hoặc chọn ảnh mẫu','class_1_00013.jpg'); await main_scroll(0)
        async def edge_canny():
            await select('Phương pháp biên','canny');await main_scroll(470)
        async def edge_morph():
            await select('Phương pháp biên','morphology');await main_scroll(470)
        async def stricter():
            await slider('Tương phản vùng/nền tối thiểu',0.60);await main_scroll(850)
        async def default_contrast():
            await slider('Tương phản vùng/nền tối thiểu',0.10);await main_scroll(850)
        async def metrics():
            await tab('Chỉ số và phân tích');await main_scroll(150);await sidebar_top()
        async def slice_row():
            await slider('Lát cắt hàng',300)
        async def result_stats():
            await tab('Kết quả ảnh');await main_scroll(860)
        async def downloads():
            for label,name in [('Tải mask.png','class_1_00013_mask.png'),('Tải cấu hình và chỉ số','class_1_00013_result.json')]:
                async with page.expect_download() as info:
                    await page.get_by_role('button',name=label,exact=True).click()
                item=await info.value;await item.save_as(OUT/'demo_exports'/name)
                await page.wait_for_timeout(600)
        async def upload_sea():
            await sidebar_top()
            await page.locator('input[type=file]').set_input_files(str(ROOT/'data/sample/sea_surface/sea_surface_01.jpg'))
            await settle();await main_scroll(100)
        async def failure_stats():
            await main_scroll(850)
            (CACHE/'failure_visible.txt').write_text(await page.get_by_test_id('stMain').inner_text(),encoding='utf-8')
        async def back_sample():
            await sidebar_top()
            # Removing the uploaded file restores the selected sample.
            await page.get_by_role('button',name='Remove sea_surface_01.jpg',exact=True).click()
            await settle();await tab('Kết quả ảnh');await main_scroll(470)
            assert '2.08%' in await page.get_by_test_id('stMain').inner_text(),'Expected restored 00013 result'
        try:
            await at(0,'Introduction')
            await at(23,'Select 00013',choose_sample)
            await at(40,'Filter none',lambda:select('Bộ lọc','none'))
            await at(50,'Filter Lee',lambda:select('Bộ lọc','lee'))
            await at(65,'Enhancement none',lambda:select('Tăng tương phản','none'))
            await at(76,'Enhancement CLAHE',lambda:select('Tăng tương phản','clahe'))
            await at(92,'CLAHE clip 5',lambda:slider('CLAHE clip limit',5.0))
            await at(103,'CLAHE clip 2',lambda:slider('CLAHE clip limit',2.0))
            await at(119,'Canny',edge_canny)
            await at(137,'Morphology',edge_morph)
            await at(155,'Contrast 0.60',stricter)
            await at(165,'Contrast 0.10',default_contrast)
            await at(174,'Metrics',metrics)
            await at(192,'Row 300',slice_row)
            await at(202,'Result statistics',result_stats)
            await at(210,'Download mask and JSON',downloads)
            await at(227,'Upload sea surface',upload_sea)
            await at(245,'Failure statistics',failure_stats)
            await at(263,'Library comparison',lambda:tab('Đối chiếu thư viện'))
            await at(287,'Team roles',lambda:tab('Phân công TV1–TV5'))
            await at(300,'Return to 00013',back_sample)
            await at(308,'Final sample statistics',lambda:main_scroll(850))
            await at(326,'Pipeline review',lambda:main_scroll(0))
            await at(343,'Conclusion',sidebar_top)
            await at(360,'End')
            if not FAST:
                await page.wait_for_timeout(1200)
                raw=await page.video.path()
                result={'raw_video':str(raw),'trim_start':round(t0-opened,3),'duration':360,'viewport':[1600,800],'events':events,'voice':False}
                (CACHE/'capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        except Exception:
            await page.screenshot(path=str(CACHE/'error.png'))
            (CACHE/'error_body.txt').write_text(await page.locator('body').inner_text(),encoding='utf-8')
            raise
        finally:
            await context.close();await browser.close()
asyncio.run(run())
