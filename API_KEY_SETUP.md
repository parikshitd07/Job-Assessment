# Gemini API Key Configuration Guide

## Where is the API Key Stored?

The Gemini API key is **NOT stored in the code** for security. Instead, it's configured via **environment variable**.

## Configuration in `llm_recommendation_engine.py` (Lines 36-42):

```python
def __init__(self, assessments_path='shl_full_catalog.json', api_key=None):
    """Initialize with LLM and embedding models"""
    
    # Configure Gemini API
    if api_key:
        genai.configure(api_key=api_key)
    else:
        # Try to get from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
```

## How to Set Up the API Key

### Option 1: Environment Variable (Recommended)

#### On Mac/Linux:
```bash
# Temporary (current session only)
export GEMINI_API_KEY="your_actual_api_key_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GEMINI_API_KEY="your_actual_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### On Windows:
```cmd
# Temporary
set GEMINI_API_KEY=your_actual_api_key_here

# Permanent (System Properties > Environment Variables)
setx GEMINI_API_KEY "your_actual_api_key_here"
```

### Option 2: .env File (Alternative)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

3. Load it in your code (already supported via python-dotenv):
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Pass Directly (For Testing Only)

```python
from llm_recommendation_engine import LLMRecommendationEngine

engine = LLMRecommendationEngine(api_key="your_key_here")
```

**⚠️ Warning**: Never commit API keys to Git!

## How to Get a Gemini API Key (FREE)

1. Go to: https://ai.google.dev/gemini-api/docs/pricing
2. Click "Get API key in Google AI Studio"
3. Sign in with Google account
4. Click "Create API key"
5. Copy the key

**Free Tier**: 
- 60 requests per minute
- Sufficient for testing and evaluation

## Verify API Key is Working

```bash
# Test the LLM engine
python3 llm_recommendation_engine.py
```

**Expected output if key is configured**:
```
✓ Gemini API initialized
✓ Loaded XX assessments
Building embedding index...
```

**If key is NOT configured**:
```
⚠ Gemini API not available, using fallback
```

## Fallback Behavior

If no API key is provided:
- System still works but uses TF-IDF instead of LLM
- No query understanding via LLM
- No re-ranking via LLM
- Still returns recommendations (but less intelligent)

For **full functionality and assignment compliance**, the API key is needed.

## Security Best Practices

1. ✅ **DO**: Store in environment variables
2. ✅ **DO**: Use .env file (add `.env` to `.gitignore`)
3. ❌ **DON'T**: Hard-code in source files
4. ❌ **DON'T**: Commit to version control
5. ❌ **DON'T**: Share publicly

---

## Quick Setup Commands

```bash
# 1. Get your API key from Google AI Studio
# https://ai.google.dev/gemini-api/docs/pricing

# 2. Set environment variable
export GEMINI_API_KEY="YOUR_ACTUAL_KEY_HERE"

# 3. Test it works
python3 llm_recommendation_engine.py

# 4. Start the API
python3 app.py
```

That's it! The system will automatically use the key from the environment.
