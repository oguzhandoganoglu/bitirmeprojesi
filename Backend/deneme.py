import openai

clientOpenAi = openai.OpenAI(api_key="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")

thread = clientOpenAi.beta.threads.create(
    messages = [
    {
        "role": "user",
        "content": ""
    } 
    ]
)
thread_id = thread.id
message = "vegetarian"
message = clientOpenAi.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message
)
runs = clientOpenAi.beta.threads.runs.list(
    thread_id
)
print(thread)

messages= clientOpenAi.beta.threads.messages.list(thread_id=thread_id)
new_message = messages.data[0].content[0].text.value

#print(new_message)