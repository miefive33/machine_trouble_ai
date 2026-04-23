# Library Selection

このファイルは、PoC 段階で使用する Python ライブラリの選定理由を整理するためのものです。

## 最小構成

- `ollama`
  - ローカル Ollama サーバーとの通信
  - 回答モデル呼び出し
  - 埋め込みモデル呼び出し

- `chromadb`
  - ベクトル検索用データベース
  - マニュアルや過去事例の保存
  - metadata フィルタ検索

- `pypdf`
  - PDF マニュアルからのテキスト抽出

- `pandas`
  - CSV / Excel 事例データの読み込みと整形

- `openpyxl`
  - Excel (`.xlsx`) 読み込み

- `python-dotenv`
  - `.env` による設定管理

- `streamlit`
  - 簡易 Web UI 構築

## 現時点の requirements.txt

```txt
ollama
chromadb
pypdf
pandas
openpyxl
python-dotenv
streamlit
```

## 後から追加候補

- `python-docx`
  - Word マニュアル読込が必要になった場合

- `langchain`
- `langchain-ollama`
  - テキスト分割や RAG パイプライン抽象化を強化したい場合

## いったん入れないもの

- `torch`
- `transformers`
- `faiss`
- OCR 系ライブラリ

これらは初期 PoC では過剰になりやすいため、まずは導入しない方針とする。
