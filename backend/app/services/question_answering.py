import chromadb
import logging
import os
from typing import List, Optional
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.models.transcription import Transcript
from app.models.question_answering import QueryResult

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


class QuestionAnsweringService:
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

    def query_transcript(
        self,
        question: str,
        transcript_id: Optional[str],
        top_k: Optional[int] = 5,
        search_type: Optional[str] = "keyword",
    ) -> List[QueryResult]:
        logger.info(
            f"Querying transcript with {search_type} search for question: {question}"
        )

        if search_type == "keyword":
            return self._keyword_search(question, transcript_id)
        elif search_type == "semantic":
            return self._semantic_search(question, transcript_id, top_k)
        else:
            logger.warning(
                f"Unsupported search type: {search_type}. Defaulting to keyword search."
            )
            return self._keyword_search(question, transcript_id, top_k)

    def _keyword_search(
        self, question: str, transcript_id: Optional[str]
    ) -> List[QueryResult]:
        """Perform a keyword search on transcript segments."""

        try:
            logger.info(f"Performing keyword search for question: {question}")

            # Get all segments for the transcript
            where_filter = {"transcript_id": transcript_id} if transcript_id else None

            results = self._collection.get(where=where_filter)

            if not results or not results["documents"]:
                logger.warning(f"No segments found for transcript ID: {transcript_id}")
                return []

            documents = results["documents"]
            metadatas = results["metadatas"]

            # Filter documents based on keyword match
            filtered_documents = [
                doc for doc in documents if question.lower() in doc.lower()
            ]

            if not filtered_documents:
                logger.warning(f"No keyword matches found for question: {question}")
                return []

            query_results = [
                QueryResult(
                    segment_id=metadatas[i]["id"],
                    start_time=metadatas[i]["start_time"],
                    end_time=metadatas[i]["end_time"],
                    text=document,
                    transcript_id=metadatas[i]["transcript_id"],
                    relevance_score=None,
                )
                for i, document in enumerate(filtered_documents)
            ]

            logger.info(
                f"Found {len(query_results)} keyword matches for question: {question}"
            )
            return query_results
        except Exception as e:
            logger.error(f"Failed to perform keyword search: {e}")
            raise

    def _semantic_search(
        self, question: str, transcript_id: Optional[str], top_k: Optional[int] = 5
    ) -> List[QueryResult]:
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
                return []

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

            return query_results
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            raise


question_answering_service = QuestionAnsweringService()
