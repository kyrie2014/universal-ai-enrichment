# Architecture

This document describes the architecture of the Universal AI Data Enrichment Tool.

## Overview

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                       GUI Layer (Tkinter)                    │
│                      AgentApp (agent_main.py)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Application Logic Layer                   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  UniversalAIAgent (agent_main.py)                    │   │
│  │  - query_single()    - query_batch()                 │   │
│  │  - generate_prompt() - parse_json_response()         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AgentConfigManager (agent_main.py)                  │   │
│  │  - load_config()     - save_config()                 │   │
│  │  - get_active_schema() - add_schema()                │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                      AI Integration Layer                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OpenAICompatibleClient (openai_compatible_client.py) │  │
│  │  - chat()           - test_connection()               │  │
│  │  - _parse_ai_response()                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCPClient (mcp_client.py)                            │  │
│  │  - enhance_prompt() - is_enabled()                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TencentYuanbaoClient (tencent_yuanbao.py)            │  │
│  │  - chat()           - test_connection()               │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                     External Services                        │
│                                                               │
│  • OpenAI API          • DeepSeek API                        │
│  • Alibaba Qwen API    • Custom OpenAI-compatible APIs       │
│  • Web Search (via MCP)                                      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. GUI Layer

**File:** `src/agent/agent_main.py` (Class: `AgentApp`)

**Responsibilities:**
- User interface with Tkinter
- File selection and output configuration
- Progress display and logging
- Settings dialogs

**Key Methods:**
- `create_widgets()` - Build UI components
- `start_processing()` - Initiate data processing
- `process_file()` - Main processing loop

### 2. Application Logic Layer

#### 2.1 UniversalAIAgent

**File:** `src/agent/agent_main.py`

**Responsibilities:**
- Core business logic
- Prompt generation
- Response parsing
- Batch processing coordination

**Key Methods:**
- `query_single(input_data)` - Process single record
- `query_batch(input_data_list)` - Process multiple records
- `generate_prompt(input_data, is_batch)` - Create AI prompts
- `parse_json_response(response)` - Extract structured data

#### 2.2 AgentConfigManager

**File:** `src/agent/agent_main.py`

**Responsibilities:**
- Configuration persistence
- Schema management
- AI settings storage

**Configuration Structure:**
```json
{
  "active_schema": "schema_name",
  "schemas": {
    "schema_name": {
      "name": "Display Name",
      "description": "Schema description",
      "input_columns": [...],
      "output_columns": [...],
      "prompt_template": "...",
      "batch_prompt_template": "..."
    }
  },
  "ai_settings": {
    "provider": "openai_compatible",
    "api_key": "...",
    "base_url": "...",
    "model": "...",
    "enable_mcp": true,
    "enable_deep_thinking": false
  }
}
```

### 3. AI Integration Layer

#### 3.1 OpenAICompatibleClient

**File:** `src/agent/openai_compatible_client.py`

**Responsibilities:**
- OpenAI-compatible API communication
- Streaming and non-streaming responses
- Response parsing
- Error handling

**Features:**
- Supports DeepSeek, Qwen, GPT-4, and other OpenAI-compatible APIs
- Deep thinking mode for reasoning models
- Web search integration
- Automatic retry logic

#### 3.2 MCPClient

**File:** `src/agent/mcp_client.py`

**Responsibilities:**
- Model Context Protocol integration
- Web search enhancement
- Real-time information retrieval

#### 3.3 TencentYuanbaoClient

**File:** `src/agent/tencent_yuanbao.py`

**Responsibilities:**
- Tencent Yuanbao AI integration
- Cookie-based authentication
- Response parsing

### 4. Supporting Components

#### 4.1 Schema Editor

**File:** `src/agent/schema_editor.py`

**Responsibilities:**
- Visual schema configuration
- Input/output column management
- Prompt template editing

#### 4.2 Cache Manager

**File:** `src/agent/cache_manager.py`

**Responsibilities:**
- Query result caching
- Reduce redundant API calls
- Improve performance

## Data Flow

### Single Record Processing

```
1. User selects file and starts processing
2. AgentApp reads Excel file with pandas
3. For each row:
   a. Extract input data based on schema
   b. Generate prompt via UniversalAIAgent
   c. Call AI API via OpenAICompatibleClient
   d. Parse response to extract structured data
   e. Write results back to DataFrame
4. Save enriched data to Excel
```

### Batch Processing

```
1. User enables batch mode and sets batch size
2. AgentApp collects multiple rows
3. For each batch:
   a. Aggregate input data
   b. Generate batch prompt
   c. Single API call for entire batch
   d. Parse batch response
   e. Map results back to individual rows
4. Save enriched data to Excel
```

## Configuration Management

### Schema Configuration

Schemas define:
- **Input columns**: Required fields from Excel
- **Output columns**: Fields to be generated by AI
- **Prompt templates**: Instructions for AI
- **Batch prompt templates**: Optimized for batch processing

### AI Settings

- Provider selection (OpenAI, DeepSeek, Qwen, etc.)
- API credentials
- Model selection
- Processing modes
- Feature toggles (MCP, deep thinking, etc.)

## Processing Modes

### 1. Standard Batch Mode
- Suitable for 100-1000 records
- Medium speed and cost
- High accuracy
- Batch size: 10-20 records

### 2. One-Shot Mode
- Suitable for <100 records
- Fast processing
- Low cost (single API call)
- High accuracy

### 3. Turbo Mode
- Suitable for 1000+ records
- Very fast (concurrent processing)
- High cost
- Medium accuracy
- Batch size: 60-80 records
- Concurrent requests: 3-5

## Error Handling

### API Errors
- Authentication failures (401)
- Rate limiting (429)
- Timeout errors
- Insufficient balance (402)

**Strategy:**
- Automatic retry with exponential backoff
- Detailed error messages
- Graceful degradation

### Data Errors
- Missing required columns
- Invalid data formats
- Parsing failures

**Strategy:**
- Validation before processing
- Skip invalid records with logging
- Fallback to default values

## Performance Optimization

### Caching
- Cache query results
- Avoid duplicate API calls
- LRU eviction policy

### Batch Processing
- Reduce API call overhead
- Better token efficiency
- Lower costs (93% savings)

### Concurrent Processing
- Thread pool for I/O operations
- Parallel API calls (Turbo mode)
- Progress tracking

## Security Considerations

### API Keys
- Never hardcoded in source
- Stored in configuration files
- Configuration files in .gitignore
- Masked in UI (password fields)

### Data Privacy
- Local processing only
- No data uploaded except to AI API
- User controls AI provider
- No telemetry or tracking

## Extensibility

### Adding New AI Providers

1. Create client class implementing standard interface:
   ```python
   class NewAIClient:
       def __init__(self, api_key, **kwargs): pass
       def chat(self, prompt, stream=False): pass
       def test_connection(self): pass
   ```

2. Add to provider selection in UI
3. Update configuration handling
4. Add tests

### Adding New Schemas

1. Use Schema Editor UI, or
2. Manually edit configuration JSON
3. Define input/output columns
4. Create prompt templates

### Adding New Features

- Follow modular design
- Add to appropriate layer
- Update configuration if needed
- Document in README
- Add tests

## Testing Strategy

### Unit Tests
- Test individual components
- Mock external dependencies
- Focus on business logic

### Integration Tests
- Test component interaction
- Use test AI provider
- Verify data flow

### Manual Testing
- Test with sample Excel files
- Verify UI functionality
- Test all processing modes

## Deployment

### Desktop Application
- Build with PyInstaller
- Single executable
- Bundle all dependencies
- Platform-specific builds

### Distribution
- GitHub Releases
- Versioned builds
- Release notes
- Installation guides

## Future Enhancements

### Planned Features
- More AI providers
- Advanced caching strategies
- Improved error recovery
- Performance monitoring
- Plugin system
- API server mode

### Performance Improvements
- Async I/O
- Database backend for caching
- Streaming Excel processing
- Memory optimization

### User Experience
- Better progress indication
- More templates
- Tutorial system
- Export formats (CSV, JSON)

