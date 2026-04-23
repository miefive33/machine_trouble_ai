from __future__ import annotations

import streamlit as st

from config import load_config
from models import CauseCandidateResult, TroubleInput
from ollama_client import OllamaClient
from rag_pipeline import RagPipeline


def _render_list(title: str, items: list[str], ordered: bool = False) -> None:
    st.markdown(f"#### {title}")
    if not items:
        st.write("- なし")
        return
    for idx, item in enumerate(items, start=1):
        prefix = f"{idx}." if ordered else "-"
        st.write(f"{prefix} {item}")


def _render_evidence_status(result: CauseCandidateResult, rag_enabled: bool) -> None:
    st.markdown("### 根拠表示")
    if not rag_enabled:
        st.warning("現在はRAG無効のため、入力情報のみから原因候補を生成しています。")
        return

    if not result.retrieved_documents:
        st.warning("現在は参考文書未登録のため、入力情報のみから原因候補を生成しています。")
        return

    st.success(f"参考文書 {len(result.retrieved_documents)} 件を取得しました。")
    for i, doc in enumerate(result.retrieved_documents, start=1):
        with st.expander(f"[{i}] {doc.title}", expanded=False):
            st.write(f"**文書種別:** {doc.source_type}")
            st.write(f"**抜粋:** {doc.snippet}")
            if doc.score is not None:
                st.write(f"**類似度距離:** {doc.score:.4f}")
            if doc.metadata:
                st.write("**metadata:**")
                st.json(doc.metadata)


def main() -> None:
    config = load_config()
    st.set_page_config(page_title=config.app_title, layout="wide")

    st.title(config.app_title)
    st.caption("ローカル保全支援AI PoC")
    st.info("この結果は原因候補の提示です。最終判断は実機確認・マニュアル確認・担当者判断で行ってください。")

    client = OllamaClient(config)
    pipeline = RagPipeline(config=config, ollama_client=client)

    ok, message = client.health_check()

    with st.sidebar:
        st.subheader("設定")
        st.write(f"**Model:** {config.ollama_model}")
        st.write(f"**RAG:** {'有効' if config.rag_enabled else '無効'}")
        st.write(f"**Top-K:** {config.top_k}")
        st.write(f"**Timeout:** {config.request_timeout_sec}s")
        if ok:
            st.success(f"Ollama: {message}")
        else:
            st.error(message)

    st.markdown("### 入力")
    symptom = st.text_area("症状内容（必須）", height=140, placeholder="例: 加工中に急停止し、再起動後も同じ位置で停止する")

    col1, col2 = st.columns(2)
    with col1:
        alarm_code = st.text_input("アラームコード（任意）")
        machine_model = st.text_input("機種名（任意）")
        material = st.text_input("材質（任意）")
    with col2:
        thickness = st.text_input("板厚（任意）")
        timing = st.selectbox(
            "発生タイミング（任意）",
            options=["", "加工開始直後", "加工中", "加工終了時", "段取り中"],
        )

    if st.button("原因候補を出す", type="primary"):
        if not symptom.strip():
            st.error("症状内容は必須です。入力してから実行してください。")
            return

        trouble_input = TroubleInput(
            symptom=symptom.strip(),
            alarm_code=alarm_code.strip(),
            machine_model=machine_model.strip(),
            material=material.strip(),
            thickness=thickness.strip(),
            timing=timing.strip(),
        )

        with st.spinner("原因候補を生成中..."):
            try:
                result = pipeline.run_pipeline(trouble_input)
            except Exception as exc:
                st.error(f"処理中にエラーが発生しました: {exc}")
                return

        st.markdown("### 回答ステータス")
        st.success("回答を生成しました。")

        _render_list("原因候補", result.causes, ordered=True)
        _render_list("まず確認すべき点", result.checks)
        _render_list("根拠", result.evidences)
        _render_list("注意", result.cautions)

        _render_evidence_status(result=result, rag_enabled=config.rag_enabled)


if __name__ == "__main__":
    main()