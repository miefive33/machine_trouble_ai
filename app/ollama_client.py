from __future__ import annotations

from dataclasses import dataclass

import requests

from config import AppConfig


@dataclass
class OllamaClient:
    config: AppConfig

    def health_check(self) -> tuple[bool, str]:
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/tags"
        try:
            response = requests.get(url, timeout=self.config.request_timeout_sec)
            response.raise_for_status()
            return True, "接続OK"
        except requests.RequestException as exc:
            return False, f"Ollama接続エラー: {exc}"

    def generate_answer(self, prompt: str, system_prompt: str) -> str:
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.num_predict,
            },
        }
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.request_timeout_sec,
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            return "Ollamaへのリクエストがタイムアウトしました。時間を置いて再試行してください。"
        except requests.RequestException as exc:
            return f"Ollama通信エラーが発生しました: {exc}"
        except ValueError:
            return "Ollamaのレスポンス解析に失敗しました。"

        answer = data.get("response", "")
        if not isinstance(answer, str) or not answer.strip():
            return "モデルから有効な回答を取得できませんでした。"
        return answer.strip()