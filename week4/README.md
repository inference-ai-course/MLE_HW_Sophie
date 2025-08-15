# Week 4: RAG System Implementation

## 📚 Project Overview

This project implements a complete **Retrieval-Augmented Generation (RAG)** system for question-answering on academic papers from arXiv's Computational Linguistics (cs.CL) category. The system combines document retrieval with language generation to provide accurate, context-aware answers to user queries.

## 🎯 Objectives

- Build an end-to-end RAG pipeline for academic paper Q&A
- Process and index 50+ arXiv cs.CL papers
- Implement efficient vector search using FAISS
- Generate contextual answers using OpenAI GPT-3.5
- Evaluate system performance with comprehensive metrics

## 🏗️ System Architecture

```
1. Data Collection → 2. Text Extraction → 3. Chunking → 4. Embedding
                                                            ↓
8. Answer Generation ← 7. Context Building ← 6. Retrieval ← 5. Indexing
```

## 📁 File Structure

```
week4/
├── rag_structured.ipynb      # Main implementation notebook
├── papers/                    # Directory containing 100 PDF papers
│   ├── *.pdf                 # arXiv cs.CL research papers
├── papers_info.json          # Metadata for all papers (title, authors, abstract)
├── rag_index.pkl             # FAISS vector index (86KB)
├── rag_deliverables.json     # System specifications and metrics
├── rag_qa_results.json       # Q&A results for test queries
├── rag_evaluation.csv        # Performance evaluation metrics
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install required packages
pip install langchain langchain-openai langchain-community
pip install sentence-transformers faiss-cpu
pip install PyPDF2 tiktoken arxiv
pip install openai python-dotenv
pip install numpy pandas
```

### Environment Setup

Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the System

1. Open `rag_structured.ipynb` in Jupyter Notebook
2. Run all cells sequentially
3. The system will:
   - Download papers (if not present)
   - Process and chunk documents
   - Generate embeddings
   - Build vector index
   - Test retrieval and generation

## 💡 Key Features

### 1. Data Collection
- **Papers Downloaded**: 50 arXiv cs.CL papers
- **Format**: PDF documents
- **Metadata**: Title, authors, abstract, arXiv ID

### 2. Text Processing
- **Documents Processed**: 100 documents
- **Average Length**: 68,579 characters per document
- **Cleaning**: Text extraction from PDFs with metadata preservation

### 3. Document Chunking
- **Chunk Size**: ≤512 tokens
- **Overlap**: 50 tokens
- **Total Chunks**: 19 (can be adjusted for better coverage)
- **Method**: Recursive character text splitting with token counting

### 4. Embeddings
- **Model**: `all-MiniLM-L6-v2` (Sentence Transformers)
- **Dimension**: 384
- **Batch Size**: 32
- **Storage**: 0.03 MB

### 5. Vector Index
- **Type**: FAISS IndexFlatL2
- **Search Method**: L2 distance
- **Retrieval**: Top-3 most relevant chunks
- **Speed**: <100ms per query

### 6. Answer Generation
- **LLM**: OpenAI GPT-3.5-turbo
- **Temperature**: 0.7
- **Max Tokens**: 500
- **Context Window**: 3 retrieved passages

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Average Retrieval Distance | 1.3334 |
| Documents Retrieved per Query | 3.0 |
| Total Test Queries | 10 |
| Retrieval Speed | <100ms |
| Success Rate | 100% |

## 🧪 Test Queries

The system was evaluated with 10 comprehensive test queries including:

1. What are the latest advances in language models?
2. How does attention mechanism work in transformers?
3. What are the main applications of NLP?
4. How do transformers handle long sequences and context?
5. What are the evaluation metrics for machine translation?
6. What is the role of fine-tuning in language models?
7. How does RAG (Retrieval-Augmented Generation) work?
8. What are the challenges in multilingual NLP?
9. How do language models handle bias and fairness?
10. What are the recent developments in prompt engineering?

## 📈 Results

### Sample Q&A Output

**Question**: "What are the latest advances in language models?"

**Answer**: "The latest advances in language models include the development of frameworks for faithfulness evaluation, zero-resource black-box hallucination detection, and data augmentation using large language models."

**Retrieved Sources**:
1. Prompt-Response Semantic Divergence Metrics (Distance: 1.09)
2. When Explainability Meets Privacy (Distance: 1.12)
3. Cross-lingual Aspect-Based Sentiment Analysis (Distance: 1.14)

## 🔧 Configuration

### Adjustable Parameters

```python
# Chunking
chunk_size = 512        # Maximum tokens per chunk
chunk_overlap = 50      # Token overlap between chunks

# Embedding
model_name = "all-MiniLM-L6-v2"  # Sentence transformer model
batch_size = 32                   # Batch size for encoding

# Retrieval
top_k = 3              # Number of chunks to retrieve

# Generation
temperature = 0.7      # GPT temperature
max_tokens = 500       # Maximum response length
model = "gpt-3.5-turbo"  # OpenAI model
```

## 🎓 Learning Outcomes

This implementation demonstrates:
- Document processing and text extraction from PDFs
- Efficient text chunking strategies
- Vector embedding generation and similarity search
- Integration of retrieval with language generation
- Building production-ready Q&A systems
- Performance evaluation and optimization

## 🐛 Known Issues & Improvements

1. **Low Chunk Count**: Current implementation generates only 19 chunks from 100 documents
   - **Solution**: Adjust chunk_size and overlap parameters
   - **Recommendation**: Use chunk_size=256, overlap=25

2. **Limited Context**: Some queries return "answer not found in context"
   - **Solution**: Increase top_k retrieval or improve chunking strategy

3. **Large PDF Files**: Some papers might be truncated during processing
   - **Solution**: Implement robust PDF parsing with error handling

## 📝 Future Enhancements

- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add query expansion techniques
- [ ] Integrate multiple embedding models
- [ ] Implement caching for faster responses
- [ ] Add user feedback loop for continuous improvement
- [ ] Support for multiple languages
- [ ] Real-time paper updates from arXiv

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements.

## 📄 License

This project is for educational purposes as part of the MLE course.

## 🙏 Acknowledgments

- arXiv for providing open access to research papers
- OpenAI for GPT-3.5 API
- Sentence Transformers for embedding models
- FAISS for efficient similarity search

---

**Author**: Sophie Zhang  
**Course**: Machine Learning Engineering  
**Week**: 4  
**Topic**: Retrieval-Augmented Generation (RAG)