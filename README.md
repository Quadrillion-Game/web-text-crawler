# web-text-crawler

Google検索結果を起点にBFSでWebページをクロールし、本文テキストを抽出してCSVに保存するCLIツール。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 使い方

```bash
crawling "検索キーワード"
```

`--depth` でBFS探索の最大深さを指定できる（デフォルト: 0 = シードURLのみ）。

```bash
crawling "検索キーワード" --depth 2
```

結果は `data/urls/` と `data/texts/` にCSVとして出力される。その他のオプションは `crawling --help` で確認。
