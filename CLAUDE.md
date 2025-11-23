# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**code-ingest** is a source code RAG (Retrieval-Augmented Generation) indexing system designed for large codebases (100K-1M+ lines). It uses AST-based parsing and vector embeddings to enable semantic code search through Qdrant vector database integration.

**Current Status**: Planning/design phase. The [requirements.md](requirements.md) contains comprehensive specifications, but implementation has not yet begun.

**Primary Language**: Japanese (documentation), Python 3.11+ (planned implementation)

## Architecture

### Planned Module Structure

The system will be organized into these core modules:

1. **AST Parser Layer** - Tree-sitter based parsing for C, C++, Java, Rust, Go, Python
   - Extracts: functions, classes, dependencies, comments, type information
   - Metadata: signatures, modifiers, scope, line numbers, cyclomatic complexity

2. **Embedding Layer** - Code vectorization using Jina Embeddings v2 Base Code
   - Model: `jinaai/jina-embeddings-v2-base-code` (768-dim, 8192-token context)
   - CRITICAL: Must match the same model version used by the MCP search server

3. **Qdrant Integration** - Vector database client
   - Collection management (per-repository collections)
   - Rich metadata storage for filtering

4. **File Processing** - Input filtering and parallel processing
   - `.ragignore` support (.gitignore-compatible syntax)
   - Binary detection, encoding validation (UTF-8)
   - Multi-file parallel processing

5. **CLI Interface** - Command-line tool
   - YAML configuration file driven
   - Progress tracking and structured logging

### Data Flow

```
Source Files → Filter (.ragignore) → Parse (Tree-sitter) → Extract Metadata →
Vectorize (Jina) → Store (Qdrant with metadata)
```

### Key Design Principles

- **Chunk Unit**: Function/method level (not file level)
- **Resilience**: Continue processing on individual file failures
- **Extensibility**: New languages via Tree-sitter parser plugins
- **Observability**: Comprehensive logging at DEBUG/INFO/WARN/ERROR levels

## Configuration

### Main Config File (YAML)

```yaml
input:
  source_dir: "/path/to/source/code"
  ignore_file: ".ragignore"

qdrant:
  url: "http://localhost:6333"
  api_key: "${QDRANT_API_KEY}"  # Environment variable supported
  collection_name: "project-name"  # Defaults to directory name

embedding:
  model_name: "jinaai/jina-embeddings-v2-base-code"
  dimension: 768
  max_length: 8192
  batch_size: 8

processing:
  parallel_workers: 4  # Defaults to CPU count
  languages: [python, rust, go, java, c, cpp]

logging:
  level: "INFO"
  file: "code-rag-indexer.log"
```

### .ragignore File

Follows .gitignore syntax for excluding files:
```
*.pyc
__pycache__/
*_test.go
*.test.js
generated/
```

## Development Commands

### Environment Setup

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies (once requirements.txt exists)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Running the Indexer (Planned)

```bash
# Basic usage
code-rag-indexer -c config.yaml

# Verbose logging
code-rag-indexer -c config.yaml -v

# Show help
code-rag-indexer --help
```

### Testing (Planned)

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_parser.py

# Run with coverage
pytest --cov=code_ingest tests/
```

### Docker Deployment (Planned)

```bash
# Start Qdrant + Indexer
docker-compose up

# Build indexer image
docker build -t code-rag-indexer .

# Run indexer container
docker run -v ./source_code:/source_code:ro \
           -v ./config.yaml:/app/config.yaml:ro \
           -e QDRANT_API_KEY=$QDRANT_API_KEY \
           code-rag-indexer
```

## Key Dependencies

```
transformers==4.35.0       # HuggingFace model integration
torch==2.1.0               # PyTorch for model runtime
qdrant-client==1.7.0       # Vector database client
tree-sitter==0.20.4        # Parser framework
tree-sitter-python==0.20.4 # Python parser
tree-sitter-rust==0.20.4   # Rust parser
tree-sitter-go==0.20.0     # Go parser
tree-sitter-java==0.20.2   # Java parser
tree-sitter-c==0.20.6      # C parser
tree-sitter-cpp==0.20.3    # C++ parser
PyYAML==6.0.1              # Config file parsing
```

## Critical Implementation Notes

### Model Consistency Requirement (VEC-005, MNT-004)

The embedding model used by this indexer MUST match exactly with the MCP search server:
- Same model: `jinaai/jina-embeddings-v2-base-code`
- Same version
- Same configuration

Mismatched models will result in incompatible vector spaces and failed searches.

### Error Handling Strategy (REL-001, REL-002)

- Syntax errors in files: Log warning, skip file, continue processing
- Partial/incomplete code: Log warning, attempt to register
- Connection failures: Log error, fail fast
- Log which files were processed successfully for resumability

### Performance Targets (PRF-002, PRF-003)

- 1M LOC in ≤8 hours (PoC goal)
- ≤32GB memory usage
- File-level parallelization enabled by default

### Collection Management (COL-004)

When processing a repository:
- If collection exists: DELETE and recreate
- No incremental updates in Phase 1
- Phase 2 will add differential updates

## Future Phases

### Phase 2 (Planned)
- Git repository cloning support
- Differential updates (changed files only)
- Contextual vectorization (surrounding code)
- Complete call graph analysis

### Phase 3 (Planned)
- Web UI for progress monitoring
- Multi-repository batch processing
- Custom parser plugins
- Metrics collection and visualization

## Important Constraints

### Technical
- Python 3.11+ required (uses modern type hints)
- Qdrant 1.7.0+ required
- UTF-8 encoding recommended (other encodings generate warnings)
- Embedding model downloads ~several GB on first run

### Operational
- Qdrant must be running before indexer starts
- Collection overwrites are destructive (no backup)
- Model changes require full re-indexing

## Repository Structure (Planned)

```
code-ingest/
├── src/code_ingest/         # Main package
│   ├── __main__.py          # CLI entry point
│   ├── parser/              # AST parsers
│   ├── embedding/           # Vectorization
│   ├── qdrant/              # DB integration
│   ├── config/              # Configuration
│   └── utils/               # Logging, file handling
├── tests/                   # Test suite
│   ├── fixtures/            # Test data
│   └── integration/         # E2E tests
├── config/                  # Example configs
├── docker/                  # Docker files
├── requirements.md          # Detailed requirements (Japanese)
├── README.md                # Project overview (Japanese)
└── CLAUDE.md                # This file
```
