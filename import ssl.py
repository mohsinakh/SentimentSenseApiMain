# # Use a pipeline as a high-level helper
# from transformers import pipeline

# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]
# pipe = pipeline("text-generation", model="deepseek-ai/deepseek-llm-67b-chat")
# pipe(messages)

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxx",
)

result = client.text_classification(
    inputs="I like you. I love you",
    model="j-hartmann/emotion-english-distilroberta-base",
)