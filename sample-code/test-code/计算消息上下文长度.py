import transformers

# 创建分词器
tokenizer = transformers.AutoTokenizer.from_pretrained(
    "../resources/tokenizer",
    trust_remote_code=True
)

prompt = "你好，你是?"
messages = [{"role": "user", "content": "帮我计算下45243*123"}]

print("prompt: ", len(tokenizer.encode("你好，你是?")))
print("messages: ", len(tokenizer.apply_chat_template(messages)))
