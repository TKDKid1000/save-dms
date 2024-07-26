import tiktoken
import sys

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

with open(sys.argv[1], encoding="utf8") as f:
    tokens = encoding.encode(f.read())

print(len(tokens))
