import chromadb
import logging
import os
from sentence_transformers import SentenceTransformer
from typing import List, Optional

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
    _model = None
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
        """Initialize the embedding model and vector database."""
        logger.info(f"Initializing EmbeddingService with {EMBEDDING_MODEL_NAME} model.")
        try:
            cls._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            cls._db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
            cls._collection = cls._db.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
            )

            logger.info("EmbeddingService initialized successfully.")

            logger.info(
                f"Model: {EMBEDDING_MODEL_NAME}, Database Path: {CHROMA_DB_DIR}, Collection: {COLLECTION_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingService: {e}")
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
                    "id": str(segment.id),
                }
                for segment in transcript.segments
            ]
            ids = [str(segment.id) for segment in transcript.segments]

            self._collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logger.info(
                f"Indexed transcript {transcript.id} with {len(transcript.segments)} segments successfully."
            )
        except Exception as e:
            logger.error(f"Failed to index transcript segments: {e}")
            raise

    def query_transcript(
        self, question: str, transcript_id: Optional[str], top_k: Optional[int] = 5
    ) -> List[QueryResult]:
        """Query the vector database with a question to find relevant transcript segments."""
        try:
            logger.info(f"Querying for segments related to question: {question}")

            # Restrict results to a specific transcript if transcript_id is provided
            where_filter = {"transcript_id": transcript_id} if transcript_id else None

            results = self._collection.query(
                query_texts=[question], n_results=top_k, where=where_filter
            )

            documents = (
                results["documents"][0] if results and results["documents"] else []
            )

            if not documents:
                logger.warning(f"No results found for question: {question}")
                return []

            metadatas = results["metadatas"][0]

            logger.info(f"Found {len(documents)} documents for question: {question}")

            query_results = [
                QueryResult(
                    segment_id=metadatas[i]["id"],
                    start_time=metadatas[i]["start_time"],
                    end_time=metadatas[i]["end_time"],
                    text=document,
                    transcript_id=metadatas[i]["transcript_id"],
                )
                for i, document in enumerate(documents)
            ]

            logger.info(f"Found {len(query_results)} segments for question: {question}")

            return query_results
        except Exception as e:
            logger.error(f"Failed to query transcript segments: {e}")
            raise


question_answering_service = QuestionAnsweringService()
