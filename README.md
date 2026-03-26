# Graph-Based Data Modeling and Query System

A knowledge graph system for exploring SAP Order-to-Cash (O2C) data using natural language queries. Built with Python/Flask (backend), HTML/JS (frontend), and Google Gemini (LLM).

## 🚀 Quick Start

**See [QUICKSTART.md](QUICKSTART.md) for 5-minute setup**

```bash
# Terminal 1: Start backend (asks to set API key on first run)
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2: Start frontend
cd frontend  
python -m http.server 8000

# Open: http://localhost:8000
```

## 📊 What It Does

Converts fragmented SAP data (orders, deliveries, invoices, payments) into a queryable knowledge graph.

### Architecture

The system consists of:

1. **Backend (Python/Flask)**
   - Data Loader: Ingests JSONL files from the dataset
   - Graph Builder: Constructs a networkx graph representing entities and relationships
   - Query Engine: Translates high-level queries into graph operations
   - LLM Service: Uses Google Gemini to convert natural language to structured queries
   - REST API: Exposes endpoints for graph exploration and querying

2. **Frontend (HTML/CSS/JavaScript)**
   - Graph Visualization: Uses Vis.js to display the knowledge graph
   - Chat Interface: Natural language query interface with guardrails
   - Real-time Response: Shows results as they're computed
   - Quick Actions: Pre-defined queries for common analysis

### Data Modeling

**Entities:**
- Sales Orders (root documents)
- Outbound Deliveries
- Billing Documents
- Payments
- Customers (Business Partners)
- Products
- Journal Entries
- Plants

**Relationships:**
- Order → Delivery (creates)
- Order → Invoice (billed_by)
- Order → Customer (placed_by)
- Order → Product (contains)
- Delivery → Product (contains)
- Invoice → Payment (paid_by)
- Invoice → Journal Entry (recorded_in)

### Setup

#### Prerequisites
- Python 3.8+
- Google Gemini API Key (free tier available at https://ai.google.dev)
- SAP O2C dataset (JSONL format)

#### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. Update data directory path in `.env` or in `app.py`

4. Run the backend:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Frontend Setup

1. Open `frontend/index.html` in a web browser
2. Or serve with a local server:
```bash
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

### API Endpoints

#### Graph Operations
- `GET /api/graph/summary` - Get graph statistics
- `GET /api/graph/node/<node_id>` - Get node details
- `GET /api/graph/subgraph/<node_id>` - Get subgraph around a node

#### Predefined Queries
- `GET /api/query/products-by-billing` - Products with most billing documents
- `GET /api/query/trace-flow/<document_id>` - Trace document flow
- `GET /api/query/incomplete-flows` - Find incomplete workflows
- `GET /api/query/customer/<customer_id>` - Get customer data

#### LLM-Powered Interface
- `POST /api/chat` - Natural language query
  - Request: `{"message": "Which products have the most invoices?"}`
  - Response: Natural language answer with data backing

### Query Examples

**Example 1: Top Products by Billing**
```
"Which products are associated with the highest number of billing documents?"
```
Response: System queries all billing documents, finds connected products, and returns ranked list.

**Example 2: Document Flow Tracing**
```
"Trace the complete flow of sales order 740506 through delivery, billing, and payment"
```
Response: System follows the path Order → Delivery → Invoice → Payment with all details.

**Example 3: Incomplete Flows**
```
"Show me orders that have deliveries but no billing"
```
Response: System identifies broken workflows and returns details for investigation.

### Guardrails

The system implements several safeguards:

1. **Query Validation**: Checks if query contains blacklisted terms (delete, hacks, etc.)
2. **Domain Restriction**: LLM validates that questions are about the dataset
3. **Off-Topic Detection**: Rejects general knowledge or creative writing requests
4. **Safe Response**: Returns clear message when query is outside scope:
   > "This system is designed to answer questions related to the provided dataset only."

### Design Decisions

#### Graph Storage
- **Choice**: NetworkX (in-memory graph library)
- **Rationale**: Fast for moderate datasets (< 1M nodes), no database setup needed, good for prototyping
- **Trade-off**: Limited to RAM; for production, would use Neo4j or Amazon Neptune

#### LLM Provider
- **Choice**: Google Gemini (free tier)
- **Rationale**: High quality, reasonable rate limits, good for initial development
- **Alternative**: Could swap for Groq, OpenAI, or Claude for different cost/quality profiles

#### Query Translation
- **Approach**: LLM-to-JSON instruction generation
- **Rationale**: Flexible, allows handling varied natural language phrasings
- **Alternative**: Could use Langchain or other LLM framework for production

#### Graph Visualization
- **Choice**: Vis.js
- **Rationale**: Lightweight, no build step, good for DAGs and relationships
- **Alternative**: D3.js (more powerful but steeper learning curve)

### Extensions Implemented

1. **Semantic Understanding**: LLM interprets user questions and maps to appropriate query types
2. **Conversation Memory**: Chat interface maintains conversation history
3. **Streaming Responses**: LLM responses shown as they're generated
4. **Graph Clustering**: System groups related entities (orders → deliveries → invoices)
5. **Natural Language Fallback**: If structured query fails, LLM provides analysis-based response

### Deployment

#### Local Testing
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend (in separate terminal)
cd frontend
python -m http.server 8000
```

#### Cloud Deployment (Render.com)

Backend:
```
Environment: Python 3.9
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
```

Frontend: Deploy to Vercel or GitHub Pages

#### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "app.py"]
```

### Performance Considerations

- **Data Loading**: ~10-15 seconds for full SAP O2C dataset
- **Query Response**: < 1 second for structured queries
- **LLM Response**: 2-5 seconds depending on Gemini rate limits
- **Graph Operations**: O(V + E) complexity using NetworkX algorithms

### Testing

Pre-defined test queries to validate functionality:

1. ✓ "What are the top 10 products by billing document count?"
2. ✓ "Trace order 740506 from creation to payment"
3. ✓ "Show me all incomplete orders (delivered but not billed)"
4. ✓ "What orders did customer 310000108 place?"
5. ✗ "What is the capital of France?" (Rejected - off-topic)
6. ✗ "Delete all orders" (Rejected - unsafe operation)

### Future Enhancements

1. **Multi-Graph Support**: Handle multiple business units or time periods
2. **Anomaly Detection**: Identify unusual patterns (late deliveries, overpayments)
3. **Predictive Analytics**: Forecast payment delays based on historical data
4. **Advanced Visualizations**: Timeline view, Sankey diagrams for flow analysis
5. **API Authentication**: OAuth2 for production deployments
6. **Caching Layer**: Redis for frequently accessed queries

### Troubleshooting

**Issue**: "GOOGLE_API_KEY environment variable not set"
- **Solution**: Create `.env` file with your API key from https://ai.google.dev

**Issue**: "Data directory not found"
- **Solution**: Update `DATA_DIR` in `.env` or `app.py` to point to JSONL files

**Issue**: Backend responds slowly
- **Solution**: Graph is being computed; initial load takes 10-15s. Consider implementing graph caching.

**Issue**: Frontend chat not connecting to backend
- **Solution**: Ensure backend is running on port 5000. Check browser console for CORS errors.

### Dependencies

**Backend**:
- Flask 2.3.0 - Web framework
- networkx 3.2 - Graph algorithms
- google-generativeai 0.3.0 - LLM API
- pandas 2.0.0 - Data processing

**Frontend**:
- Vis.js 4.21.0 - Graph visualization
- Vanilla JavaScript (no build tools required)

### Author & Attribution

- Built using AI-assisted development
- Dataset: SAP Order-to-Cash (sap-o2c-data)
- Graph Library: NetworkX
- Visualization: Vis.js
- LLM: Google Gemini

---

## License & Usage

This system is provided as-is for educational and business analysis purposes.
