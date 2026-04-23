# Project Structure

このファイルは、`machine_trouble_ai` の基本フォルダ構成を整理するためのものです。

```text
machine_trouble_ai/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ ollama_client.py
│  ├─ rag_pipeline.py
│  ├─ prompt_builder.py
│  └─ models.py
├─ data/
│  ├─ manuals/
│  ├─ cases/
│  └─ alarms/
├─ db/
│  └─ chroma/
├─ scripts/
│  ├─ ingest_manuals.py
│  ├─ ingest_cases.py
│  └─ rebuild_index.py
├─ tests/
├─ docs_for_ai/
│  ├─ file_roles.md
│  ├─ library_selection.md
│  └─ project_structure.md
├─ .env
├─ .gitignore
├─ README.md
└─ requirements.txt
```

## data/manuals
PDF マニュアルを配置するフォルダです。

## data/cases
過去不具合事例の CSV / Excel を配置するフォルダです。

## data/alarms
アラーム一覧や将来の補助データを配置するフォルダです。

## db/chroma
ChromaDB の永続データ保存先です。

## docs_for_ai
AI 開発用の設計メモ、役割一覧、方針書を置くフォルダです。
