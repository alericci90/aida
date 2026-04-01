import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"   # con AI Inference spesso coincide col model name

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

# Client corretto per endpoint cognitive-services
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(subscription_key)
)

def call_azure_llm(system_prompt: str, messages: list) -> str:
    # Struttura analoga alla OpenAI chat.completions.create
    response = client.complete(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            *messages
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0
    )

    return response.choices[0].message["content"]
