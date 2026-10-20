"""「すずしくなると」公開版をつくる。原本（ローカル）から写し、学級名・人数・日付・校時・学校の行事を外す。2026-10-20
    python3 _build/build.py
原本：~/Desktop/LiFE with/05 R8授業/理科/9 すずしくなると/（授業計画.md、板書とノート/out_kit のPDFとお手本）
形は「くらしの中の和と洋」の公開版（kurashi-wa-to-yo/_build/build.py）と同じ。教科書の紙面の画像は使わない。"""
import re, shutil
from pathlib import Path
import markdown
from PIL import Image

SRC = Path.home() / "Desktop/LiFE with/05 R8授業/理科/9 すずしくなると"
KIT = SRC / "板書とノート/out_kit"
OUT = Path(__file__).resolve().parent.parent
URL = "https://a-tozak.github.io/rika4-suzushiku/"
TITLE = "すずしくなると　板書とノート（4年理科）"
DESC = "4年理科「すずしくなると」（季節と生物）の授業計画（全7時間）、板書計画、5mm方眼の見開きノート（配る紙・記入例・書き方のこつつきのお手本）。視写をしないノートの作り方の例です。"


def sub(s, a, b, regex=False):
    n = len(re.findall(a, s, flags=re.M)) if regex else s.count(a)
    assert n, f"見つからない：{a}"
    return re.sub(a, b, s, flags=re.M) if regex else s.replace(a, b)


def clean(s):
    # 単元情報（学級と人数、本校の組み方、ローカルの参照ファイルを外す）
    s = sub(s, r"\A# .*?\n\n作成 .*?\n", "", True)
    s = sub(s, "- 学年: 第4学年　4年1組 32名", "- 学年: 第4学年")
    s = sub(s, "（年間指導計画は4(5)時間。**本校は秋の観察を11月に2回足して7時間**）", "（年間指導計画は4(5)時間。**秋の観察を11月にもう1回入れて7時間**にした組み方）")
    s = sub(s, r"^- 参照: .*\n", "", True)
    # 日付を時間の番号や「単元に入る前」に言いかえる
    s = sub(s, "**10/6までにそろえるもの**", "**単元に入る前にそろえるもの**")
    s = sub(s, "9月末に見に行く", "前の月に見に行く")
    s = sub(s, "| 1〜5 | 10/6・10/9・10/13・10/20・10/23 | 秋の観察と整理 |", "| 1〜5 | 10月 | 秋の観察と整理 |")
    s = sub(s, "| **6〜7** | **11/16・11/17** |", "| **6〜7** | **11月** |")
    s = sub(s, "11/16の冒頭で10月の記録を必ず返す", "第6時の冒頭で10月の記録を必ず返す")
    s = sub(s, "（assess.py と一致）", "")
    s = sub(s, r"^(### 第\d時)　\d+/\d+（.）\d校時　", r"\1　", True)
    s = sub(s, r"^- \*\*10/6は運動会.*\n", "", True)
    s = sub(s, r"^- \*\*10/13は運動会.*\n", "", True)
    s = sub(s, r"^- \*\*11/13が秋の遠足。.*\n", "- 校外学習などで外の景色を見てきたあとなら、見てきたものを聞いてよい\n", True)
    s = sub(s, "**10/6までに児童のファイルから出させる。**なければ教師が撮った写真で代用。**9月末に確認する**",
            "**単元に入る前に児童のファイルから出させる。**なければ教師が撮った写真で代用。**前の月に確認する**")
    # 準備物：いつまでの列と学級の人数を外す
    head, rest = s.split("## 準備物", 1)
    mid, tail = rest.split("## 次単元へのつなぎ", 1)
    mid = sub(mid, "| 物 | 数 | いつまで | 備考 |", "| 物 | 数 | 備考 |")
    mid = sub(mid, "|---|---|---|---|", "|---|---|---|")
    mid = sub(mid, r"^(\| [^|]+ \| [^|]+ \|) [^|]+ \|(.*\|)$", r"\1\2", True)   # 「いつまで」の列を外す（準備物の表だけ）
    s = head + "## 準備物" + mid + "## 次単元へのつなぎ" + tail
    s = sub(s, "| 32×2回＋予備 |", "| 人数×2回＋予備 |")
    s = sub(s, r"^(\| 整理用の表（春夏秋を並べる） \|) 32 ", r"\1 人数分 ", True)
    s = sub(s, "| 16 |", "| 班に1つ |")
    # 次単元へのつなぎ
    s = sub(s, "- 第5時（10/23）の次は **10 とじこめた空気と水**（10/26〜11/10）。", "- 第5時の次は **とじこめた空気と水**。")
    s = sub(s, "- 11/16・11/17でこの単元に戻る。", "- 11月の第6・7時で、この単元に戻る。")
    s = sub(s, "- 第7時（11/17）で書いた", "- 第7時で書いた")
    return s


def check(s, name):
    bad = [k for k in ("1組", "32", "校時", "運動会", "遠足", "本校", "9/", "10/", "11/", "（月）", "（火）", "（水）", "（木）", "（金）", ".py", ".md", "`") if k in s]
    assert not bad, f"{name} に残っている：{bad}"


CSS = (OUT.parent / "kurashi-wa-to-yo/_build/build.py").read_text(encoding="utf-8").split('CSS = """', 1)[1].split('"""', 1)[0]


def page(fname, title, body, desc=DESC):
    html = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="robots" content="noindex"><meta name="description" content="{desc}">
<link rel="canonical" href="{URL}{'' if fname == 'index.html' else fname}">
<meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{URL}{'' if fname == 'index.html' else fname}"><meta property="og:image" content="{URL}og.png"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style></head><body><main>
<nav><a href="./">はじめに</a><a href="keikaku.html">授業計画（全7時間）</a></nav>
{body}
<footer>© 外﨑顯博　教科書の本文と紙面は載せていません。授業計画・板書計画・ノートは自作です。記入例の気温と動物の数は自作の例です。</footer></main></body></html>"""
    (OUT / fname).write_text(html, encoding="utf-8")


def main():
    md = markdown.Markdown(extensions=["tables"])
    s = clean((SRC / "授業計画.md").read_text(encoding="utf-8")); check(s, "授業計画")
    page("keikaku.html", "授業計画（全7時間）｜すずしくなると", "<h1>すずしくなると　授業計画（全7時間）</h1>" + md.convert(s))
    pdfs = [("すずしくなると_板書計画_全時間.pdf", "板書計画（全7時）", "A4よこ。黒板と、発問と予想される反応", "out/04時_板書_p1.png"),
            ("すずしくなると_ノート_配る紙_全時間.pdf", "ノート　配る紙（全7時）", "B4よこ＝5mm方眼ノートの見開き。題名・問題・めあて・問いだけ刷ってあります", "out/01時_ノート_p1.png"),
            ("すずしくなると_ノート_記入例_全時間.pdf", "ノート　記入例（全7時）", "配る紙に、子どもの答えの例を青で入れたもの", "out/04時_ノート_記入例_p1.png"),
            ("すずしくなると_ノートのお手本_全時間.pdf", "ノートのお手本（全7時）", "記入例のまわりに、書き方のこつを矢印で書きそえたもの。A4よこ", "お手本/04時_お手本.png")]
    cards = []
    for i, (f, name, note, png) in enumerate(pdfs):
        shutil.copy(KIT / f, OUT / "files" / f)
        im = Image.open(KIT / png).convert("RGB"); im.thumbnail((900, 900))
        thumb = f"files/card_{i + 1}.jpg"; im.save(OUT / thumb, quality=82)
        cards.append(f'<div class="card"><a href="files/{f}"><img src="{thumb}" alt="{name}の1ページめ" loading="lazy"></a><b><a href="files/{f}">{name}（PDF）</a></b>{note}</div>')
    figs = []
    for k in range(1, 8):
        im = Image.open(KIT / f"お手本/0{k}時_お手本.png").convert("RGB"); im.thumbnail((1600, 1600))
        im.save(OUT / f"files/otehon_0{k}.jpg", quality=84)
        figs.append(f'<figure><figcaption>第{k}時</figcaption><a href="files/otehon_0{k}.jpg"><img src="files/otehon_0{k}.jpg" alt="第{k}時のノートのお手本。記入例のまわりに書き方のこつが書いてある" loading="lazy" style="width:100%;border:1px solid var(--line);border-radius:6px;background:#fff"></a></figure>')
    og = Image.open(KIT / "out/04時_板書_p1.png").convert("RGB")
    w, h = og.size; og = og.crop((0, 0, w, int(w * 630 / 1200))).resize((1200, 630)); og.save(OUT / "og.png")
    body = f"""<h1>すずしくなると<br>板書とノート（4年理科）</h1>
<p class="lead">「季節と生物」の秋の単元（東京書籍　新しい理科4年 p.102〜109）の7時間ぶんです。春と夏の記録とくらべて、すずしくなると植物や動物のようすがどう変わるかを調べます。10月に5時間、11月にもう一度観察する2時間を入れています。</p>
<p>この単元では、黒板を写す時間を取りません。ノートは毎時間、B4の紙を1枚配ります。紙ぜんたいがクラスの5mm方眼ノートと同じマス目で、題名・問題・めあて・問いははじめから刷ってあります。表や囲みは、子どもがじょうぎで引くのと同じように、マス目の上に線を引いて作っています。子どもは空いたマスに、自分の言葉だけを書きます。</p>
<div class="cards">{''.join(cards)}</div>
<h2>ノートのお手本（書き方のこつつき）</h2>
<p>記入例のまわりに、書き方のこつを書きそえました。理科のノートは、問題、観察、結果（見たことだけ）、考察、まとめ、ぎもんの順に書きます。結果は表にして、まだ理由は書きません。考察は「春は気温が（　）、ヘチマは（　）」のような型にそって書きます。終わりに「ふりかえり」の欄があり、分かったことと次にしたいことを書きます。ノートは書いたあとに見直すと力になる、という研究が多いためです。授業のはじめに映して、書き方をそろえるときに使えます。</p>
{''.join(figs)}
<h2>授業計画</h2><p><a href="keikaku.html">授業計画（全7時間）</a>に、単元の目標、評価、毎時間の流れ、つまずきと手立て、準備物をのせています。</p>
<h2>作り方</h2><p>書き方のこつは、ノート指導の公的資料と研究（ノートは見直すと効き目が大きい、自分の考えと友だちの考えを分ける、など）から選びました。</p>
<p>板書計画とノートは、自作の道具「マス目プリントメーカー」で作りました。字はマスに1字ずつ入り、数字は5mmに1字です。記入例の気温や動物の数は自作の例なので、学級の記録に合わせて直して使ってください。授業の日付や学級の情報は外してあります。</p>"""
    page("index.html", TITLE, body)
    (OUT / ".nojekyll").write_text("")
    print("ok", sorted(p.name for p in OUT.iterdir()))


main()
