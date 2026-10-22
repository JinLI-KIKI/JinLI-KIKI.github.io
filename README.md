# jinli-kiki.github.io

Personal site of Jin Li (李津). Live at <https://jinli-kiki.github.io/>.

Plain HTML and CSS with a little JavaScript, hosted on GitHub Pages. No framework.

## Pages

| URL | Page |
| --- | --- |
| `/` | Home: entry points to everything |
| `/lenovo/` | The Lenovo year, with five case pages under it |
| `/lenovo/planning-role/` | North America master planning |
| `/lenovo/excess-inventory/` | Excess inventory clean-up |
| `/lenovo/tariff-pull-in/` | Tariff pull-in |
| `/lenovo/vietnam-transition/` | China to Vietnam motherboards |
| `/lenovo/commit-automation/` | Parts-to-box commit tool |
| `/research/` | Research overview, with four pages under it |
| `/projects/` | Supply chain digital twin, lab logger, literature map |
| `/publications/` | Papers, thesis, talks |
| `/experience/` | Magna, Weilun, undergraduate research |
| `/cv/` | One-page résumé, with the PDF |

## 怎么改

所有页面的正文都在 `_src/pages/` 里，一个文件对应一页。页头、导航、页脚和图表由 `_src/build.py` 统一生成。

1. 改 `_src/pages/` 里对应的文件。
2. 在这个文件夹里运行：`python3 _src/build.py`（只需要 Python 3，不用装任何包）。
3. 用 GitHub Desktop 提交并推送。

小改动（改一个字、换一个数字）也可以直接改生成好的 `index.html`，但下次运行 build 会被覆盖，所以最好改 `_src/pages/`。

- **换照片**：把新照片命名为 `jin-li.jpg`，覆盖 `assets/img/jin-li.jpg`。竖版 3:4，宽度至少 600 px。
- **改时间轴**（联想那一年的甘特图、关税节点）：改 `_src/build.py` 顶部的 `YEAR` 和 `TARIFF`。
- **更新 PDF 简历**：在 Chrome 打开 `/cv/` 页面 → 打印 → 另存为 PDF，A4，勾选“背景图形” → 保存为 `assets/Jin_Li_CV.pdf`。

## Fonts

Archivo, SIL Open Font License (`assets/fonts/OFL.txt`).
