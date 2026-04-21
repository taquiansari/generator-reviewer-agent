# Generator-Reviewer Agent

AI-powered educational content pipeline using two agents:

1. **Generator Agent** — creates grade-appropriate explanations and MCQs for a given topic  
2. **Reviewer Agent** — evaluates the output for age-appropriateness, correctness, and clarity  
3. **Refinement** — if the reviewer fails the content, the generator re-runs with feedback (1 pass)

## Screenshots:
<img width="2747" height="1248" alt="image" src="https://github.com/user-attachments/assets/fe64213d-c1fe-4a50-a4f6-004a8c78451c" />
<img width="1928" height="1183" alt="image" src="https://github.com/user-attachments/assets/db407873-1da8-4ea3-8616-72de25f0873b" />


## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create a .env file with your Groq API key (free)
cp .env.example .env
# Edit .env and replace "your_api_key_here" with your actual key
# Get a free key at https://console.groq.com/

# 3. Run the app
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

## Project Structure

```
├── agents.py          # GeneratorAgent & ReviewerAgent classes + pipeline
├── app.py             # FastAPI server
├── templates/
│   └── index.html     # Web UI
├── requirements.txt
├── .env.example       # API key template
└── task.txt           # Original task specification
```
