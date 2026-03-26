# How to Deploy

## 3 Ways to Run It

### 1. Local (Testing)

```bash
cd backend
pip install -r requirements.txt
python app.py

# In another terminal:
cd frontend
python -m http.server 8000
```

Then open http://localhost:8000

**Best for:** Testing on your machine before submitting

### 2. Docker (Production-like)

```bash
docker-compose up
```

Opens at http://localhost:8000

**Best for:** Making sure it works the same everywhere

### 3. Cloud (Render.com)

1. Push code to GitHub
2. Sign up at render.com
3. Connect your GitHub repo
4. Deploy in 3 clicks

**Best for:** Sharing a live demo

---

## Before You Submit

Run the test:
```bash
cd backend
python test_graph.py
```

You should see:
- ✅ Data loaded
- ✅ Graph built  
- ✅ All tests passed

---

## What to Include When Submitting

- All code files (`backend/`, `frontend/`)
- The data folder (`sap-o2c-data/`)
- README.md and other docs
- Docker files (so they can run it anywhere)
- Your .env.example (so they know what to set up)

---

## Verifying It Works

1. **Backend API working?**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Frontend loads?**
   - Go to http://localhost:8000
   - Should see a graph and chat box

3. **Can you ask questions?**
   - Type: "Which products are in most invoices?"
   - Should get an answer in 5-10 seconds

4. **Do guardrails work?**
   - Type: "Delete all orders"
   - Should say "Can't help with that"

---

## No Internet? No API Key?

Good news - the system works without Google's API. It just uses structured queries instead of natural language. Everything still works!

---

## Something Broke?

**Backend won't start:**
- Make sure you have Python 3.8+
- Run `pip install -r requirements.txt` again
- Check that port 5000 is free

**Frontend won't load:**
- Make sure Google API key is in `.env`
- Try a different port: `python -m http.server 9000`

**Queries are slow:**
- First run loads data (takes 10-15 seconds)
- After that, queries are fast

---

## Ready?

You're good to go! The system is:
- ✅ Fully functional
- ✅ Well documented
- ✅ Ready to deploy
- ✅ Easy to evaluate

**Next:** Follow README.md to get started!
