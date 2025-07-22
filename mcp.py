from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return (data['current']['temperature_2m'] * (9/5)) + 32

def send_email(to, body):
    with open(f'emailto{to}.txt', 'a') as file:
        file.write(body + "\n\n")
    return f"Email has been sent to {to}."

client = OpenAI()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "send_email",
    "description": "Send an email message to a specified person",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "body": {"type": "string"}
        },
        "required": ["to", "body"],
        "additionalProperties": False
    },
    "strict": True
}]

def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    if name == "send_email":
        return send_email(**args)

input_messages = [{"role": "user", "content": "Can you check the weather in West Jordan, UT for me? If its above 70, email joeyboboey@gmail.com and tell him we can go hiking. Otherwise, email julibobooley34@hotmail.net and tell her I want to take her on a video game date."}]

response = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tools,
)
print(response.output)

for tool_call in response.output:
    if tool_call.type != "function_call":
        continue

    input_messages.append(tool_call)
    name = tool_call.name
    args = json.loads(tool_call.arguments)

    result = call_function(name, args)
    print(f"result for {name}: " + str(result))
    input_messages.append({
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(result)
    })
    
print(input_messages)
    
response = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tools,
)
print("Final response: " + response.output_text)

# print(response.output_text)

# tool_call = response.output[0]
# print(tool_call)
# args = json.loads(tool_call.arguments)

# result = get_weather(args["latitude"], args["longitude"])
# print(result)

# input_messages.append(tool_call)  # append model's function call message
# input_messages.append({                               # append result message
#     "type": "function_call_output",
#     "call_id": tool_call.call_id, # if theres many calls, this helps the ai keep track of which output was for which requested call
#     "output": str(result)
# })

# print(input_messages)

# response_2 = client.responses.create(
#     model="gpt-4.1",
#     input=input_messages,
#     tools=tools,
# )
# print("response 2:" + response_2.output_text)

