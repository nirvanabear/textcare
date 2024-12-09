from openai import OpenAI
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# print(f"{env('RECAPTCHA_SECRET')}")
# my_phone = f"{env('MY_PHONE')}"
# print(my_phone)
# print(f"{env('OPENAI_API_KEY')}")
# account_sid = f"{env('TWILIO_ACCOUNT_SID')}"

client = OpenAI(api_key = f"{env('OPENAI_API_KEY')}")
# client.api_key = f"{env('OPENAI_API_KEY')}"

completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)