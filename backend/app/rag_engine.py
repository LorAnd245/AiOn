import os
import re
import json
from typing import List, Tuple, Dict, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import httpx
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import settings


class RelevanceLevel(Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class SearchResult:
    content: str
    source: str
    score: float
    relevance: RelevanceLevel
    chunk_index: int
    confidence: float


@dataclass
class SearchAnalysis:
    results: List[SearchResult]
    has_relevant: bool
    best_score: float
    relevance_distribution: Dict[RelevanceLevel, int]
    recommended_strategy: str
    confidence: float


class RAGEngine:
    THRESHOLDS = {'very_high': 9.0, 'high': 14.0, 'medium': 18.0, 'low': 21.0}

    SKIP_RAG_PATTERNS = [
        r'^(ciao|salve|buongiorno|buonasera|hey|hi|hello)[\s!?.]*$',
        r'^(grazie|thanks|ok|va bene|perfetto|bene)[\s!?.]*$',
        r'^(arrivederci|a presto|addio|bye)[\s!?.]*$',
        r'^(come stai|come va)[\s!?.]*$',
        r'^[\s!?.]*$',
    ]

    def __init__(self):
        # Delay creating the heavy HuggingFaceEmbeddings instance until first use
        self.embeddings = None
        self._hf_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self._hf_model_kwargs = {'device': 'cpu'}
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
            length_function=len,
        )
        print(f"🔧 RAG Engine ready | chunk={settings.RAG_CHUNK_SIZE} overlap={settings.RAG_CHUNK_OVERLAP}")

    def _ensure_embeddings(self):
        """Initialize the HuggingFaceEmbeddings instance on first use.

        Raises a RuntimeError with a helpful message if the model cannot be downloaded.
        """
        if self.embeddings is not None:
            return
        try:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings as _HFE
            except Exception:
                from langchain_community.embeddings import HuggingFaceEmbeddings as _HFE

            self.embeddings = _HFE(
                model_name=self._hf_model_name,
                model_kwargs=self._hf_model_kwargs,
            )
        except Exception as e:
            msg = (
                f"Failed to initialize HuggingFace embeddings ({self._hf_model_name}): {e}\n"
                "If you're offline, pre-download the model or configure a local embedding.\n"
                "Run: python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')\""
            )
            print(msg)
            raise RuntimeError(msg)

    def _should_skip_rag(self, query: str) -> bool:
        q = query.lower().strip()
        for pattern in self.SKIP_RAG_PATTERNS:
            if re.match(pattern, q, re.IGNORECASE):
                return True
        return len(q) < 8

    def get_vector_store_path(self, agent_id: int) -> str:
        return os.path.join(settings.VECTOR_STORE_DIR, f"agent_{agent_id}")

    async def process_document(self, file_path: str, agent_id: int, filename: str) -> Dict:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext in ['.docx', '.doc']:
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')

        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        total_chars = 0
        for i, chunk in enumerate(chunks):
            chunk_len = len(chunk.page_content)
            total_chars += chunk_len
            chunk.metadata.update({
                'source': filename, 'chunk_index': i,
                'total_chunks': len(chunks), 'chunk_size': chunk_len, 'agent_id': agent_id,
            })

        path = self.get_vector_store_path(agent_id)
        # Ensure embeddings are ready before interacting with FAISS
        self._ensure_embeddings()
        if os.path.exists(path):
            vs = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            vs.add_documents(chunks)
            vs.save_local(path)
            mode = "updated"
        else:
            vs = FAISS.from_documents(documents=chunks, embedding=self.embeddings)
            vs.save_local(path)
            mode = "created"

        print(f"✅ Vector store {mode}: {filename} | {len(chunks)} chunks | {total_chars:,} chars")
        return {
            'filename': filename, 'chunks': len(chunks),
            'total_characters': total_chars,
            'avg_chunk_size': total_chars // len(chunks) if chunks else 0,
            'mode': mode,
        }

    def _get_relevance_level(self, score: float) -> RelevanceLevel:
        score = float(score)
        if score < self.THRESHOLDS['very_high']: return RelevanceLevel.VERY_HIGH
        if score < self.THRESHOLDS['high']:      return RelevanceLevel.HIGH
        if score < self.THRESHOLDS['medium']:    return RelevanceLevel.MEDIUM
        if score < self.THRESHOLDS['low']:       return RelevanceLevel.LOW
        return RelevanceLevel.NONE

    def _calculate_confidence(self, score: float, relevance: RelevanceLevel) -> float:
        score = float(score)
        if relevance == RelevanceLevel.VERY_HIGH: return max(90.0, 100 - (score / 9.0) * 10)
        if relevance == RelevanceLevel.HIGH:      return max(75.0, 90 - ((score - 9.0) / 5.0) * 15)
        if relevance == RelevanceLevel.MEDIUM:    return max(50.0, 75 - ((score - 14.0) / 4.0) * 25)
        if relevance == RelevanceLevel.LOW:       return max(25.0, 50 - ((score - 18.0) / 3.0) * 25)
        return max(0.0, 25 - ((score - 21.0) / 5.0) * 25)

    async def search_documents(self, agent_id: int, query: str, k: int = 6) -> SearchAnalysis:
        if self._should_skip_rag(query):
            return SearchAnalysis([], False, 999.0, {}, "skip_simple_query", 0.0)

        path = self.get_vector_store_path(agent_id)
        if not os.path.exists(path):
            return SearchAnalysis([], False, 999.0, {}, "no_documents", 0.0)

        try:
            # Ensure embeddings are initialized before loading/searching
            self._ensure_embeddings()
            vs = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            raw = vs.similarity_search_with_score(query, k=k)

            results: List[SearchResult] = []
            distribution = {level: 0 for level in RelevanceLevel}

            for doc, score in raw:
                relevance = self._get_relevance_level(score)
                confidence = self._calculate_confidence(score, relevance)
                results.append(SearchResult(
                    content=doc.page_content,
                    source=doc.metadata.get('source', 'unknown'),
                    score=round(float(score), 2),
                    relevance=relevance,
                    chunk_index=doc.metadata.get('chunk_index', 0),
                    confidence=round(float(confidence), 1),
                ))
                distribution[relevance] += 1

            strategy, has_relevant, overall_confidence = self._determine_strategy(results, distribution)
            print(f"🔍 Search agent={agent_id} | strategy={strategy} | confidence={overall_confidence:.1f}%")

            return SearchAnalysis(
                results=results, has_relevant=has_relevant,
                best_score=results[0].score if results else 999.0,
                relevance_distribution=distribution,
                recommended_strategy=strategy, confidence=overall_confidence,
            )
        except Exception as e:
            print(f"❌ Search error: {e}")
            return SearchAnalysis([], False, 999.0, {}, "error", 0.0)

    def _determine_strategy(self, results, distribution) -> Tuple[str, bool, float]:
        if not results:
            return ("no_results", False, 0.0)
        vh = distribution[RelevanceLevel.VERY_HIGH]
        h  = distribution[RelevanceLevel.HIGH]
        m  = distribution[RelevanceLevel.MEDIUM]
        if vh >= 2:
            return ("direct_answer", True, float(sum(r.confidence for r in results[:3]) / min(3, len(results))))
        if vh >= 1 or h >= 2:
            top = [r for r in results if r.relevance in (RelevanceLevel.VERY_HIGH, RelevanceLevel.HIGH)]
            return ("document_based", True, float(sum(r.confidence for r in top[:3]) / min(3, len(top))))
        if m >= 2 or (h >= 1 and m >= 1):
            return ("hybrid", True, float(sum(r.confidence for r in results[:3]) / 3))
        if results[0].score < self.THRESHOLDS['medium']:
            return ("cautious_hybrid", True, float(results[0].confidence))
        return ("general_fallback", False, 0.0)


class GroqClient:
    """Groq LLM client — supports both regular and streaming responses."""

    def __init__(self):
        self.api_key  = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_BASE_URL
        self.timeout  = settings.GROQ_TIMEOUT
        self.max_retries = settings.GROQ_MAX_RETRIES

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _build_messages(
        self,
        prompt: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """Build the messages array with optional system prompt and conversation history."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        # Inject last N turns of history (keep context window manageable)
        if history:
            for msg in history[-settings.CHAT_HISTORY_TURNS * 2:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def generate(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        history: Optional[List[Dict]] = None,
    ) -> str:
        model = model or settings.DEFAULT_MODEL
        payload = {
            "model": model,
            "messages": self._build_messages(prompt, system, history),
            "temperature": max(1e-8, float(temperature)),
            "max_tokens": max_tokens,
            "top_p": 0.9,
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload, headers=self._headers(),
                    )
                    response.raise_for_status()
                    data = response.json()
                    result = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("completion_tokens", "?")
                    print(f"✅ Groq | model={model} | tokens={tokens} | attempt={attempt+1}")
                    return result
            except httpx.ReadTimeout as e:
                last_error = e
                if attempt < self.max_retries: continue
            except httpx.HTTPStatusError as e:
                last_error = e
                print(f"❌ Groq HTTP {e.response.status_code}: {e.response.text}")
                if e.response.status_code < 500: break
            except Exception as e:
                last_error = e
                print(f"❌ Groq error: {type(e).__name__}: {e}")
                if attempt < self.max_retries: continue
        raise last_error

    async def stream(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        history: Optional[List[Dict]] = None,
    ) -> AsyncIterator[str]:
        """Yield text chunks as they arrive from Groq SSE stream."""
        model = model or settings.DEFAULT_MODEL
        payload = {
            "model": model,
            "messages": self._build_messages(prompt, system, history),
            "temperature": max(1e-8, float(temperature)),
            "max_tokens": max_tokens,
            "top_p": 0.9,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        chunk = delta.get("content", "")
                        if chunk:
                            yield chunk
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def list_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/models", headers=self._headers())
                response.raise_for_status()
                models = response.json().get("data", [])
                return sorted([
                    m["id"] for m in models
                    if not any(x in m["id"] for x in ["whisper", "tts", "embed"])
                ])
        except Exception as e:
            print(f"⚠️  Could not fetch Groq models: {e}")
            return [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ]


# Singletons
rag_engine   = RAGEngine()
groq_client  = GroqClient()
ollama_client = groq_client  # backward-compat alias
