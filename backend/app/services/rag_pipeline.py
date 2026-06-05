import json
import logging
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings

logger = logging.getLogger(__name__)

# Used when Pinecone IS configured (Phase 4)
SYSTEM_PROMPT_WITH_CONTEXT = """You are a clinical triage assistant. Your role is to assess symptom urgency
based on the provided medical guidelines and patient information.

IMPORTANT RULES:
- You are NOT diagnosing. You are triaging urgency.
- Always recommend professional medical evaluation.
- When in doubt, escalate to a higher urgency level.
- Base your reasoning on the retrieved medical guidelines provided.

Context from medical guidelines:
{context}"""

# Used when Pinecone is NOT configured (Phase 1 — LLM-only mode)
SYSTEM_PROMPT_DIRECT = """You are a clinical triage assistant. Your role is to assess symptom urgency.

IMPORTANT RULES:
- You are NOT diagnosing. You are triaging urgency only.
- Always recommend professional medical evaluation.
- When in doubt, escalate to a higher urgency level."""

USER_PROMPT = """Patient symptoms: {symptoms}
Patient context: {patient_context}

Respond ONLY with valid JSON in this exact format:
{{
    "urgency_level": "er|urgent_care|gp|self_care",
    "confidence_score": 0.0-1.0,
    "conditions_suggested": [
        {{"name": "condition", "probability": "high/medium/low", "description": "brief description"}}
    ],
    "reasoning": "step-by-step clinical reasoning",
    "recommended_actions": ["action 1", "action 2"],
    "follow_up_questions": ["question if more info needed"],
    "disclaimer": "This is not a medical diagnosis. Please consult a healthcare professional."
}}"""


def _parse_json(raw: str) -> dict:
    """Strip markdown code fences if present, then parse JSON."""
    text = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


class MedicalRAGPipeline:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.1, api_key=settings.anthropic_api_key)
        self._pinecone_enabled = bool(
            settings.pinecone_api_key and settings.pinecone_api_key != "your_pinecone_api_key_here"
        )

        if self._pinecone_enabled:
            self._init_rag_chain()
            logger.info("RAG pipeline initialized with Pinecone retrieval")
        else:
            logger.info("RAG pipeline running in direct LLM mode (no Pinecone configured)")

    def _init_rag_chain(self):
        """Wire up Pinecone retrieval — only called when API key is present."""
        from langchain_pinecone import PineconeVectorStore
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = PineconeVectorStore(index_name=settings.pinecone_index_name, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_WITH_CONTEXT),
            ("human", USER_PROMPT),
        ])
        doc_chain = create_stuff_documents_chain(self.llm, prompt)
        self._chain = create_retrieval_chain(retriever, doc_chain)

    async def run_triage(self, symptoms_structured: dict, patient_context: dict) -> dict:
        if self._pinecone_enabled:
            result = await self._chain.ainvoke({
                "input": str(symptoms_structured),
                "symptoms": str(symptoms_structured),
                "patient_context": str(patient_context),
            })
            raw = result["answer"]
        else:
            # Direct LLM call — no retrieval
            user_text = USER_PROMPT.format(
                symptoms=str(symptoms_structured),
                patient_context=str(patient_context),
            )
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT_DIRECT),
                HumanMessage(content=user_text),
            ])
            raw = response.content

        return _parse_json(raw)


_pipeline: MedicalRAGPipeline | None = None


def get_rag_pipeline() -> MedicalRAGPipeline:
    """Lazy singleton — avoids loading at import time."""
    global _pipeline
    if _pipeline is None:
        _pipeline = MedicalRAGPipeline()
    return _pipeline
