import os
import sys
# Attempt to import from google.genai (new SDK) or google.generativeai (old SDK)
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    import google.generativeai as genai_old
    HAS_GENAI_OLD = True
except ImportError:
    HAS_GENAI_OLD = False

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    # Try to find it in .env if python-dotenv is available, but unlikely in this env
    print("GOOGLE_API_KEY not set in environment.")
    # We can't proceed without key
    sys.exit(1)

print(f"Using API Key: {api_key[:4]}...{api_key[-4:]}")

if HAS_GENAI:
    print("Using google.genai SDK...")
    try:
        client = genai.Client(api_key=api_key)
        for model in client.models.list():
            if "generateContent" in (model.supported_actions or []):
                print(f"Model: {model.name}")
    except Exception as e:
        print(f"Error with google.genai: {e}")

if HAS_GENAI_OLD:
    print("\nUsing google.generativeai SDK...")
    try:
        genai_old.configure(api_key=api_key)
        for model in genai_old.list_models():
            if "generateContent" in model.supported_generation_methods:
                print(f"Model: {model.name}")
    except Exception as e:
        print(f"Error with google.generativeai: {e}")
