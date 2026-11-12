import sys, json
from pathlib import Path
import numpy as np
root = next(p for p in Path(__file__).resolve().parents
            if (p / "src/tv3/filters.py").exists())
sys.path.insert(0, str(root))
from src.filters import custom_lee_filter
from src.enhancement import global_histogram_equalization
a = np.full((5, 5), 100, dtype=np.uint8)
a[2, 2] = 200
actual = int(custom_lee_filter(a, 3, 4)[2, 2])
assert actual == 111, actual
h = np.repeat(np.arange(4, dtype=np.uint8), 4).reshape(4, 4)
lut = global_histogram_equalization(h)[1][:4]
assert np.array_equal(lut, [0, 85, 170, 255])
result = {"lee_expected": 111, "lee_actual": actual,
          "he_lut": lut.tolist(), "max_abs_error": 0}
Path(__file__).with_name("example_result.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
