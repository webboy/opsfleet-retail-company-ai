"""Golden Bucket trio store: load, retrieve, and capture candidates."""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import yaml

from retail_agent.config import Settings, get_settings

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 3
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Trio:
    id: str
    question: str
    sql: str
    report: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    source_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "sql": self.sql,
            "report": self.report,
            "tags": list(self.tags),
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Trio:
        return cls(
            id=data["id"],
            question=data["question"],
            sql=data["sql"],
            report=data["report"],
            tags=tuple(data.get("tags") or ()),
            source_path=data.get("source_path"),
        )


@dataclass(frozen=True)
class RetrievalResult:
    trios: list[Trio]
    method: str  # embedding | keyword


class Embedder(Protocol):
    def embed_query(self, text: str) -> list[float]: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class GeminiEmbedder:
    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for Gemini embeddings.")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        self._client = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=settings.google_api_key,
        )

    def embed_query(self, text: str) -> list[float]:
        return self._client.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._client.embed_documents(texts)


class FakeEmbedder:
    """Deterministic embedder for tests keyed by question tokens."""

    def embed_query(self, text: str) -> list[float]:
        return self._vectorize(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(text) for text in texts]

    def _vectorize(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        # Simple bag-of-words hash vector
        vec = [0.0] * 32
        for token in tokens:
            vec[hash(token) % 32] += 1.0
        return _normalize(vec)


class TrioStore:
    def __init__(
        self,
        bucket_dir: Path | str | None = None,
        *,
        embedder: Embedder | None = None,
        settings: Settings | None = None,
        top_k: int = DEFAULT_TOP_K,
        embedding_enabled: bool = True,
    ) -> None:
        self.settings = settings or get_settings()
        self.bucket_dir = Path(bucket_dir or _default_bucket_dir())
        self.candidates_dir = self.bucket_dir / "candidates"
        self.top_k = top_k
        self.embedding_enabled = embedding_enabled
        self._embedder = embedder
        self._trios = load_trios(self.bucket_dir)
        self._question_vectors: list[list[float]] | None = None

    @property
    def embedder(self) -> Embedder | None:
        if self._embedder is not None:
            return self._embedder
        if not self.embedding_enabled:
            return None
        try:
            self._embedder = GeminiEmbedder(self.settings)
        except Exception:  # noqa: BLE001
            logger.warning("Gemini embedder unavailable; keyword fallback only.")
            self._embedder = None
        return self._embedder

    def retrieve(self, question: str, *, k: int | None = None) -> RetrievalResult:
        k = k or self.top_k
        if not self._trios:
            return RetrievalResult(trios=[], method="keyword")

        embedder = self.embedder
        if embedder is not None:
            try:
                return self._retrieve_by_embedding(question, embedder, k)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Embedding retrieval failed, using keyword fallback: %s", exc)

        return RetrievalResult(
            trios=_retrieve_by_keywords(question, self._trios, k),
            method="keyword",
        )

    def capture_candidate(
        self,
        *,
        question: str,
        sql: str,
        report: str,
        retrieved_trio_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> Path:
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "question": question,
            "sql": sql,
            "report": report,
            "retrieved_trio_ids": retrieved_trio_ids or [],
        }
        path = self.candidates_dir / "candidates.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
        return path

    def _retrieve_by_embedding(
        self,
        question: str,
        embedder: Embedder,
        k: int,
    ) -> RetrievalResult:
        if self._question_vectors is None:
            self._question_vectors = embedder.embed_documents(
                [trio.question for trio in self._trios]
            )
        query_vector = embedder.embed_query(question)
        scored = [
            (_cosine_similarity(query_vector, vector), trio)
            for vector, trio in zip(self._question_vectors, self._trios, strict=True)
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return RetrievalResult(trios=[trio for _, trio in scored[:k]], method="embedding")


def load_trios(bucket_dir: Path) -> list[Trio]:
    trios: list[Trio] = []
    if not bucket_dir.exists():
        return trios
    for path in sorted(bucket_dir.glob("*.md")):
        trios.append(load_trio_file(path))
    return trios


def load_trio_file(path: Path) -> Trio:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Trio file must start with YAML front matter: {path}")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid trio front matter in {path}")

    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    trio_id = str(meta["id"])
    question = str(meta["question"])
    sql = str(meta["sql"]).strip()
    report = str(meta.get("report") or body).strip()
    tags = tuple(str(tag) for tag in (meta.get("tags") or []))

    return Trio(
        id=trio_id,
        question=question,
        sql=sql,
        report=report,
        tags=tags,
        source_path=str(path),
    )


def format_trios_for_prompt(trios: list[Trio]) -> str:
    if not trios:
        return "(no similar historical examples retrieved)"

    blocks: list[str] = []
    for index, trio in enumerate(trios, start=1):
        blocks.append(
            "\n".join(
                [
                    f"Example {index}:",
                    f"Question: {trio.question}",
                    "SQL:",
                    trio.sql.strip(),
                    f"Analyst note: {trio.report.strip()}",
                ]
            )
        )
    return "\n\n".join(blocks)


def trios_from_state(raw: list[dict] | None) -> list[Trio]:
    if not raw:
        return []
    return [Trio.from_dict(item) for item in raw]


def _retrieve_by_keywords(question: str, trios: list[Trio], k: int) -> list[Trio]:
    scored = [
        (_keyword_score(question, trio.question), trio)
        for trio in trios
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [trio for score, trio in scored[:k] if score > 0] or [trio for _, trio in scored[:k]]


def _keyword_score(left: str, right: str) -> float:
    left_tokens = set(_tokenize(left))
    right_tokens = set(_tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(intersection) / len(union)


def _tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def _default_bucket_dir() -> Path:
    from os import getenv

    configured = getenv("GOLDEN_BUCKET_DIR")
    if configured:
        return Path(configured)
    return Path.cwd() / "golden_bucket"
