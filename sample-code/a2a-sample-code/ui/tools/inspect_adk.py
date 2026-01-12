import inspect
from google.adk.models.lite_llm import LiteLlm
print("Found LiteLlm")
try:
    print(inspect.getsource(LiteLlm.__init__))
except Exception:
    print(inspect.signature(LiteLlm))
