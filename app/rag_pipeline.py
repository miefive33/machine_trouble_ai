from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import chromadb

from config import AppConfig
from models import CauseCandidateResult, RetrievedDocument, TroubleInput
from ollama_client import OllamaClient
from prompt_builder import (
    build_system_prompt,
    build_user_prompt_with_rag,
    build_user_prompt_without_rag,
)


@dataclass
class RagPipeline:
    config: AppConfig
    ollama_client: OllamaClient

    def run_pipeline(self, trouble_input: TroubleInput) -> CauseCandidateResult:
        retrieved_docs = self._retrieve_documents(trouble_input) if self.config.rag_enabled else []

        system_prompt = build_system_prompt()
        if retrieved_docs:
            user_prompt = build_user_prompt_with_rag(trouble_input, retrieved_docs)
        else:
            user_prompt = build_user_prompt_without_rag(trouble_input)

        raw_response = self.ollama_client.generate_answer(user_prompt, system_prompt)
        return self._normalize_output(raw_response=raw_response, retrieved_docs=retrieved_docs)

    def _retrieve_documents(self, trouble_input: TroubleInput) -> list[RetrievedDocument]:
        chroma_dir = Path(self.config.chroma_path)
        if not chroma_dir.exists():
            return []

        query = " ".join(
            [
                trouble_input.symptom,
                trouble_input.alarm_code,
                trouble_input.machine_model,
                trouble_input.material,
                trouble_input.thickness,
                trouble_input.timing,
            ]
        ).strip()

        try:
            client = chromadb.PersistentClient(path=self.config.chroma_path)
            collection = client.get_collection("machine_trouble_docs")
            result = collection.query(query_texts=[query], n_results=self.config.top_k)
        except Exception:
            return []

        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        retrieved: list[RetrievedDocument] = []
        for doc_text, metadata, distance in zip(docs, metadatas, distances):
            metadata = metadata or {}
            snippet = _shorten_text(doc_text)
            retrieved.append(
                RetrievedDocument(
                    source_type=str(metadata.get("source_type", "unknown")),
                    title=str(metadata.get("title", metadata.get("file_name", "(無題)"))),
                    snippet=snippet,
                    metadata={str(k): str(v) for k, v in metadata.items()},
                    score=float(distance) if distance is not None else None,
                )
            )
        return retrieved

    def _normalize_output(
        self,
        raw_response: str,
        retrieved_docs: list[RetrievedDocument],
    ) -> CauseCandidateResult:
        text = (raw_response or "").replace("<think>", "").replace("</think>", "").strip()
        if not text:
            return CauseCandidateResult(
                causes=["回答生成に失敗しました。入力内容を見直して再実行してください。"],
                checks=["Ollama の接続状態を確認してください。"],
                evidences=["根拠不足"],
                cautions=["結果が空のため、再実行または設定確認が必要です。"],
                raw_response=raw_response,
                retrieved_documents=retrieved_docs,
            )

        sections = _extract_sections(text)
        causes = _clean_bullets(sections.get("原因候補", []), default_prefix="候補")
        checks = _clean_bullets(sections.get("まず確認すべき点", []), default_prefix="確認")
        evidences = _clean_bullets(sections.get("根拠", []), default_prefix="根拠")
        cautions = _clean_bullets(sections.get("注意", []), default_prefix="注意")

        return CauseCandidateResult(
            causes=causes or ["根拠不足のため候補を限定できません。"],
            checks=checks or ["現場安全を確保し、基本点検を実施してください。"],
            evidences=evidences or ["根拠不足"],
            cautions=cautions or ["最終判断は実機確認・マニュアル確認・担当者判断で行ってください。"],
            raw_response=text,
            retrieved_documents=retrieved_docs,
        )


def _extract_sections(text: str) -> dict[str, list[str]]:
    keys = ["原因候補", "まず確認すべき点", "根拠", "注意"]
    section_map: dict[str, list[str]] = {k: [] for k in keys}

    current = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        normalized = line.replace(" ", "")
        matched = None
        for key in keys:
            if normalized.startswith(f"【{key}】"):
                matched = key
                break
        if matched:
            current = matched
            continue
        if current:
            section_map[current].append(line)

    if any(section_map.values()):
        return section_map

    section_map["原因候補"] = [text]
    return section_map


def _clean_bullets(lines: list[str], default_prefix: str) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        normalized = re.sub(r"^[-・*\d.\s]+", "", line).strip()
        if not normalized:
            continue
        wrapped = _wrap_sentence(normalized)
        cleaned.extend(wrapped)

    if not cleaned:
        return []

    unique: list[str] = []
    for item in cleaned:
        if item not in unique:
            unique.append(item)
    return unique[:5]


def _wrap_sentence(text: str, max_len: int = 80) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    for i in range(0, len(text), max_len):
        chunks.append(text[i : i + max_len])
    return chunks


def _shorten_text(text: str, limit: int = 140) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + "…"