# File Roles

このファイルは `machine_trouble_ai` プロジェクト内の各ファイルの役割を整理するためのものです。

## app/main.py
アプリの入口です。  
Streamlit UI を起動し、ユーザー入力を受け取り、RAG パイプラインを呼び出して結果を表示します。

想定役割:
- 症状文入力
- アラームコード入力
- 機種入力
- 材質入力
- 板厚入力
- 発生タイミング入力
- 結果表示

## app/config.py
設定を集約するファイルです。

想定役割:
- Ollama の回答モデル名
- Ollama の埋め込みモデル名
- ChromaDB の保存先
- データフォルダの場所
- 検索件数
- chunk サイズ

## app/ollama_client.py
Ollama との通信を担当するファイルです。

想定役割:
- 回答生成
- 埋め込み生成
- モデル呼び出し処理の集約

## app/rag_pipeline.py
RAG 処理の中核です。

想定役割:
- 入力条件の整理
- ChromaDB 検索
- マニュアルと過去事例の統合
- プロンプト生成用の材料整理
- 最終回答生成

## app/prompt_builder.py
LLM に渡すプロンプトを組み立てる専用ファイルです。

想定役割:
- システムプロンプト定義
- ユーザープロンプト組み立て
- 出力形式固定
- 危険な断定を避ける制御

## app/models.py
データ構造を定義するファイルです。

想定役割:
- TroubleInput
- RetrievedDocument
- CauseCandidateResult

## scripts/ingest_manuals.py
マニュアル文書の取り込みスクリプトです。

想定役割:
- PDF 読み込み
- ページや章単位での分割
- metadata 付与
- ChromaDB 登録

## scripts/ingest_cases.py
過去事例の取り込みスクリプトです。

想定役割:
- CSV / Excel 読み込み
- 1事例ごとのテキスト化
- metadata 付与
- ChromaDB 登録

## scripts/rebuild_index.py
インデックス再構築用スクリプトです。

想定役割:
- ChromaDB 再作成
- manuals と cases の再登録
- 埋め込み再生成

## requirements.txt
使用ライブラリ一覧です。

## .env
環境ごとの設定値を保持するファイルです。

## .gitignore
Git 管理対象外ファイルを定義するファイルです。

## README.md
プロジェクト概要、セットアップ手順、起動方法を記載するファイルです。
