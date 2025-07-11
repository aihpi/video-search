import chromadb
import logging
import os
from typing import Optional
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.models.transcription import Transcript
from app.models.search import (
    KeywordSearchResponse,
    LLMSearchResponse,
    QueryResult,
    QuestionResponse,
    SearchType,
    SemanticSearchResponse,
)
from app.models.llms import LlmAnswer
from app.services.llms import llm_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "transcript_embeddings")


class SearchService:
    _instance = None
    _db = None
    _collection = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of EmbeddingService exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_service()
        return cls._instance

    @classmethod
    def _initialize_service(cls):
        """Initialize the vector database with a custom embedding function."""
        logger.info(f"Initializing Question Answering Service.")
        try:
            cls._db = chromadb.PersistentClient(path=CHROMA_DB_DIR)

            # Create embedding function compatible with Chroma
            embedding_function = SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL_NAME
            )

            cls._collection = cls._db.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
                embedding_function=embedding_function,  # Use our model for storing and querying data
            )

            logger.info("Question Answering Service initialized successfully.")

            logger.info(
                f"Model: {EMBEDDING_MODEL_NAME}, Database Path: {CHROMA_DB_DIR}, Collection: {COLLECTION_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Question Answering Service: {e}")
            raise

    def index_transcript(self, transcript: Transcript):
        """Index a transcript by generating embeddings of the segments and storing them in the vector database."""

        try:
            if not transcript.segments:
                logger.warning("No transcript segments provided for indexing.")
                return

            logger.info(
                f"Indexing {len(transcript.segments)} transcript segments from transcript {transcript.id}."
            )

            documents = [segment.text for segment in transcript.segments]
            metadatas = [
                {
                    "transcript_id": transcript.id,
                    "start_time": segment.start,
                    "end_time": segment.end,
                    "id": segment.id,
                }
                for segment in transcript.segments
            ]
            ids = [segment.id for segment in transcript.segments]

            self._collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logger.info(
                f"Indexed transcript {transcript.id} with {len(transcript.segments)} segments successfully."
            )
        except Exception as e:
            logger.error(f"Failed to index transcript segments: {e}")
            raise

    def get_transcript_text_by_id(self, transcript_id: str) -> Optional[str]:
        """Retrieve the full text of a transcript by its ID by reconstructing from segments."""
        try:
            logger.info(f"Retrieving transcript text for ID: {transcript_id}")
            where_filter = {"transcript_id": transcript_id}

            results = self._collection.get(where=where_filter)
            if not results or not results["documents"]:
                logger.warning(f"No segments found for transcript ID: {transcript_id}")
                return None

            documents = results["documents"]
            metadatas = results["metadatas"]

            # Sort segments by start time to ensure proper order
            segment_pairs = list(zip(documents, metadatas))
            segment_pairs.sort(key=lambda x: x[1]["start_time"])

            # Reconstruct full transcript by joining segments
            full_transcript = " ".join([segment[0] for segment in segment_pairs])
            
            logger.info(f"Successfully reconstructed transcript for ID: {transcript_id}")
            return full_transcript

        except Exception as e:
            logger.error(f"Failed to retrieve transcript text: {e}")
            raise

    def query_transcript(
        self,
        question: str,
        transcript_id: Optional[str],
        top_k: Optional[int] = 5,
        search_type: Optional[SearchType] = SearchType.KEYWORD,
    ) -> QuestionResponse:
        logger.info(
            f"Querying transcript with {search_type} search for question: {question}"
        )

        if search_type == SearchType.KEYWORD:
            return self._keyword_search(question, transcript_id, top_k)
        elif search_type == SearchType.SEMANTIC:
            return self._semantic_search(question, transcript_id, top_k)
        elif search_type == SearchType.LLM:
            return self._llm_search(question, transcript_id, top_k)
        else:
            logger.warning(
                f"Unsupported search type: {search_type}. Defaulting to keyword search."
            )
            return self._keyword_search(question, transcript_id, top_k)

    def _keyword_search(
        self, question: str, transcript_id: Optional[str], top_k: Optional[int] = None
    ) -> KeywordSearchResponse:
        """Perform a keyword search on transcript segments."""

        try:
            logger.info(f"Performing keyword search for question: {question}")

            # Get all segments for the transcript
            where_filter = {"transcript_id": transcript_id} if transcript_id else None

            results = self._collection.get(where=where_filter)

            if not results or not results["documents"]:
                logger.warning(f"No segments found for transcript ID: {transcript_id}")
                return KeywordSearchResponse(
                    question=question, transcript_id=transcript_id, results=[]
                )

            documents = results["documents"]
            metadatas = results["metadatas"]

            # Filter documents based on keyword match and keep track of indices
            filtered_results = [
                (i, doc)
                for i, doc in enumerate(documents)
                if question.lower() in doc.lower()
            ]

            if not filtered_results:
                logger.warning(f"No keyword matches found for question: {question}")
                return KeywordSearchResponse(
                    question=question, transcript_id=transcript_id, results=[]
                )

            if top_k:
                filtered_results = filtered_results[:top_k]

            query_results = [
                QueryResult(
                    segment_id=metadatas[i]["id"],
                    start_time=metadatas[i]["start_time"],
                    end_time=metadatas[i]["end_time"],
                    text=document,
                    transcript_id=metadatas[i]["transcript_id"],
                    relevance_score=None,
                )
                for i, document in filtered_results
            ]

            logger.info(
                f"Found {len(query_results)} keyword matches for question: {question}"
            )

            response = KeywordSearchResponse(
                question=question, transcript_id=transcript_id, results=query_results
            )

            return response
        except Exception as e:
            logger.error(f"Failed to perform keyword search: {e}")
            raise

    def _semantic_search(
        self, question: str, transcript_id: Optional[str], top_k: Optional[int] = 5
    ) -> SemanticSearchResponse:
        """Perform a semantic search on the vector database using embeddings."""

        try:
            logger.info(f"Performing semantic search for question: {question}")

            # Restrict results to a specific transcript if transcript_id is provided
            where_filter = {"transcript_id": transcript_id} if transcript_id else None

            results = self._collection.query(
                query_texts=[question], n_results=top_k, where=where_filter
            )
            documents = (
                results["documents"][0] if results and results["documents"] else []
            )

            if not documents:
                logger.warning(f"No semantic matches found for question: {question}")
                return SemanticSearchResponse(
                    question=question, transcript_id=transcript_id, results=[]
                )

            distances = results["distances"][0]

            metadatas = results["metadatas"][0]

            query_results = [
                QueryResult(
                    segment_id=metadatas[i]["id"],
                    start_time=metadatas[i]["start_time"],
                    end_time=metadatas[i]["end_time"],
                    text=document,
                    transcript_id=metadatas[i]["transcript_id"],
                    relevance_score=round((1 - distances[i]) * 100, 2),
                )
                for i, document in enumerate(documents)
            ]

            logger.info(
                f"Found {len(query_results)} semantic matches for question: {question}"
            )

            response = SemanticSearchResponse(
                question=question, results=query_results, transcript_id=transcript_id
            )

            return response
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            raise

    def _llm_search(
        self, question: str, transcript_id: Optional[str], top_k: Optional[int] = 5
    ) -> LLMSearchResponse:
        """Use an LLM to synthesize an answer from semantic search results."""

        try:
            # First, get semantic search results (for returning in response)
            semantic_search_response: SemanticSearchResponse = self._semantic_search(
                question, transcript_id, top_k
            )

            # Second, get all segments for the transcript (for LLM context)
            where_filter = {"transcript_id": transcript_id} if transcript_id else None
            all_segments_result = self._collection.get(where=where_filter)

            if not all_segments_result or not all_segments_result["documents"]:
                logger.warning(f"No transcript found for LLM synthesis: {question}")
                return LLMSearchResponse(
                    question=question,
                    transcript_id=transcript_id,
                    results=[],
                    summary="No transcript found.",
                    not_addressed=True,
                    model_id="none",
                )

            # Convert all segments to QueryResult format and sort by start time
            all_segments = []
            for i, doc in enumerate(all_segments_result["documents"]):
                metadata = all_segments_result["metadatas"][i]
                all_segments.append(
                    QueryResult(
                        segment_id=metadata["id"],
                        start_time=metadata["start_time"],
                        end_time=metadata["end_time"],
                        text=doc,
                        transcript_id=metadata["transcript_id"],
                        relevance_score=None,
                    )
                )

            # Sort by start time to maintain chronological order
            all_segments.sort(key=lambda x: x.start_time)

            logger.info(f"Generating LLM synthesis for question: {question}")
            logger.info(f"Using {len(all_segments)} segments for full context")

            # Pass all segments to LLM for synthesis
            answer: LlmAnswer = llm_service.generate_answer(question, all_segments)

            answer_response = LLMSearchResponse(
                question=question,
                transcript_id=transcript_id,
                summary=answer.summary,
                not_addressed=answer.not_addressed,
                model_id=answer.model_id,
                results=semantic_search_response.results,
            )

            return answer_response

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise


search_service = SearchService()
