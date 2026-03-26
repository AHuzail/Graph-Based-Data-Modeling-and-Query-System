# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.8+
- A text editor
- ~2GB free disk space (includes dataset)

### Step 1: Get Google API Key (2 minutes)

1. Visit https://ai.google.dev
2. Click "Get API Key"
3. Create a new API key (free tier - no credit card needed)
4. Copy the API key

### Step 2: Configure API Key (1 minute)

Edit `backend/.env`:
```
GOOGLE_API_KEY=paste_your_key_here
```

### Step 3: Install & Run (2 minutes)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run the system
python app.py
```

In another terminal:
```bash
# Start frontend
cd frontend
python -m http.server 8000
```

### Step 4: Open in Browser

Visit: http://localhost:8000

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
→ Run: `pip install -r requirements.txt`

**"GOOGLE_API_KEY environment variable not set"**
→ Edit `backend/.env` and add your API key

**"Address already in use"**
→ Change port in `.env` or use different terminal

**Backend responds slowly**
→ Normal on first run (loading 690 nodes takes 10-15s)

## What You Can Do

- 🔍 Explore the SAP data graph
- 💬 Ask questions in natural language
- 📊 Trace orders through delivery→billing→payment
- 📈 Find top products by billing frequency
- ⚠️ Identify incomplete order flows

## Example Queries

1. "Which products have the most invoices?"
2. "Trace order 740506 from creation to payment"
3. "Show me orders with deliveries but no billing"
4. "What's the total revenue for customer 310000108?"

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions
- Explore the codebase in `backend/` and `frontend/`

## Need Help?

Check the troubleshooting section in README.md or review the test script:
```bash
cd backend
python test_graph.py
```
