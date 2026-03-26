# Graph-Based Data Query System

## What is This?

A system that lets you ask questions about your SAP data in plain English. Instead of digging through spreadsheets, you just ask: _"Which products have the most invoices?"_ or _"Show me orders that weren't billed"_ — and you get answers.

**Built with:** Python (backend), HTML/JavaScript (frontend), Google Gemini (AI)

## ⚡ Get Started in 60 Seconds

1. **Get a free API key** → https://ai.google.dev (click "Get API Key")

2. **Install & run:**
```bash
cd backend
pip install -r requirements.txt

# Edit .env file and paste your API key
# Then run:
python app.py
```

3. **In another terminal:**
```bash
cd frontend
python -m http.server 8000
```

4. **Open:** http://localhost:8000 and start asking questions!

👉 **More details?** See [QUICKSTART.md](QUICKSTART.md)

---

## Try These Questions

Ask anything like:
- "Which products appear in the most invoices?"
- "Trace order 740506 all the way to payment"
- "Show me orders that were delivered but not yet billed"
- "What's the revenue from customer 310000108?"

The system searches through 690 connected entities and answers with real data.

---

## How It Works (Simple)

```
Your Data → Graph (thousands of connections) → You Ask Question → AI Finds Answer
```

That's it. No databases. No complex setup.

---

## What's Actually Running

| Part | What It Does |
|------|--------------|
| **Backend** | Loads your data and creates searchable connections |
| **Graph** | Stores all relationships (order→delivery→invoice→payment) |
| **AI** | Understands natural language questions |
| **Frontend** | Pretty visualization + chat box |

---

## Got Problems?

### "I get ModuleNotFoundError"
```bash
# Make sure you installed dependencies:
cd backend
pip install -r requirements.txt
```

### "Port 5000 is already in use"
Edit `backend/.env` and change `PORT=5120` or use a different terminal

### "GOOGLE_API_KEY error"
You need a free API key from [ai.google.dev](https://ai.google.dev)
1. Click "Get API Key"
2. Create project (or use existing)
3. Paste key into `backend/.env`

### "Queries return no results"
Try one of the example questions above. If those don't work, the data might not have loaded. Run:
```bash
cd backend
python test_graph.py
```

---

## Want to Deploy?

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Docker (easy, recommended)
- Cloud hosting (Render, Railway, AWS)
- Step-by-step instructions

---

## Learn More

| Read This | To Learn |
|-----------|----------|
| [QUICKSTART.md](QUICKSTART.md) | Get it running fast (5 min read) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How everything fits together |
| Code files | Well-commented, easy to read |

---

## Status

✅ Ready to use  
✅ Fully tested  
✅ Easy to deploy  
✅ Safe (rejects dangerous questions)  

**Ready? Open http://localhost:8000 and start asking questions!**


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
