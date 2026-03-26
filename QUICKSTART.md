# Quick Start Guide

## 5 Minutes to Running

### Step 1: Get an API Key (Free)

Go to https://ai.google.dev and:
1. Click "Get API Key"
2. Create a new key (no credit card)
3. Copy it

### Step 2: Set It Up

Edit `backend/.env` and paste your key:
```
GOOGLE_API_KEY=your_key_here
```

### Step 3: Install Stuff

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run It

```bash
# Terminal 1 - Run the backend
python app.py

# Terminal 2 - Run the frontend
cd frontend
python -m http.server 8000
```

### Step 5: Open in Browser

Go to **http://localhost:8000**

Done! Try asking it questions.

---

## What You Can Do Right Now

Ask it things like:
- "Which products show up in the most invoices?"
- "Trace order 740506 all the way through"
- "Show orders that got delivered but not billed"
- "What's the revenue from customer 310000108 so far?"

---

## Stuck?

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| API key error | Make sure you pasted it in `backend/.env` |
| "Port already in use" | Close other Python windows or change port |
| Backend is slow | It's loading data (first time takes 10-15 seconds) |

---

## Learn More

- [README.md](README.md) - Full guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - How it works
- `backend/` folder - Code with explanations

## Validate Your Setup

```bash
cd backend
python test_graph.py
```

Should print: "✅ All tests passed!"

---

Done? Start asking questions in the chat! 🎉
