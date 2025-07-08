# Question Answering Feature

This feature gives a semantic search system that understands the meaning behind questions, not just keywords.

## Conceptual Approach

### Overall Architecture

The QA system will work in two main phases:

- Indexing Phase: Process and store transcript data
- Query Phase: Answer user questions

### Indexing Phase

When a video is transcribed:

1. Text Chunking:

   - Split transcript into meaningful segments (sentences or paragraphs)
   - Preserve timestamps for each chunk

2. Embedding Generation:

   - Convert each text chunk into a vector embedding
   - These vectors capture the semantic meaning of the text

3. Storage:

   - Store embeddings in Chroma vector database
   - Keep metadata like timestamps, segment IDs, and original text

### Query Phase

When a user asks a question:

1. Query Embedding:

   - Convert the question to a vector using the same embedding model

2. Semantic Search:

   - Find the most similar transcript chunks by comparing vector similarity
   - Retrieve top N relevant chunks

3. Answer Generation:

   - Either return the relevant chunks directly (simpler approach)
   - Or use a language model to generate a synthesized answer from retrieved chunks (more advanced)

4. Result Presentation:

   - Display answer with relevant transcript segments
   - Show timestamps for navigating to those points in the video

## Implementation Steps

### Backend

- Create an API endpoint for handling QA requests (indexing and querying)
- Use an embedding model (BGE-M3 or similar multilingual model) to convert transcript segments to vector embeddings
- Store these embeddings in a vector database like Chroma
- Implement retrieval logic to find relevant segments based on semantic similarity

### Frontend

- Add a question input component with examples to guide users
- Display answers with highlighted text snippets and timestamps
- Allow clicking answers to jump to that video timestamp
- Show confidence scores or relevance ratings for transparency
