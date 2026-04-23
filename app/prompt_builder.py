from __future__ import annotations

from models import RetrievedDocument, TroubleInput


def build_system_prompt() -> str:
    return (
        "あなたは工作機械保全支援AIです。"
        "回答は必ず日本語で、簡潔かつ実務的にしてください。"
        "原因候補の提示にとどめ、修理確定診断の表現は禁止です。"
        "根拠が不足する場合は明示的に『根拠不足』と書いてください。"
        "思考過程・検討メモ・内部推論は出力しないでください。"
        "出力は必ず次の見出し構造を守ってください。"
        "【原因候補】\n1.\n2.\n3.\n\n"
        "【まず確認すべき点】\n-\n-\n-\n\n"
        "【根拠】\n-\n-\n\n"
        "【注意】\n-"
    )


def _input_summary(trouble: TroubleInput) -> str:
    return "\n".join(
        [
            f"症状内容: {trouble.symptom}",
            f"アラームコード: {trouble.alarm_code or '未入力'}",
            f"機種名: {trouble.machine_model or '未入力'}",
            f"材質: {trouble.material or '未入力'}",
            f"板厚: {trouble.thickness or '未入力'}",
            f"発生タイミング: {trouble.timing or '未入力'}",
        ]
    )


def build_user_prompt_without_rag(trouble: TroubleInput) -> str:
    return (
        "以下の入力情報のみから、保全作業で最初に当たるべき原因候補を整理してください。\n"
        "不確かな事項は断定せず、確認観点を優先してください。\n\n"
        f"{_input_summary(trouble)}"
    )


def build_user_prompt_with_rag(trouble: TroubleInput, documents: list[RetrievedDocument]) -> str:
    doc_lines = []
    for index, doc in enumerate(documents, start=1):
        meta = ", ".join([f"{k}={v}" for k, v in doc.metadata.items()]) or "なし"
        score = f"{doc.score:.4f}" if isinstance(doc.score, float) else "N/A"
        doc_lines.append(
            f"[{index}] 種別={doc.source_type} / タイトル={doc.title} / 類似度距離={score}\n"
            f"抜粋: {doc.snippet}\n"
            f"metadata: {meta}"
        )

    evidence_block = "\n\n".join(doc_lines) if doc_lines else "参照文書なし"

    return (
        "以下の入力と参考文書を使って、原因候補を整理してください。\n"
        "参考文書に根拠が薄い場合は『根拠不足』と明記してください。\n\n"
        f"[入力]\n{_input_summary(trouble)}\n\n"
        f"[参考文書]\n{evidence_block}"
    )