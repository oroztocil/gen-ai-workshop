import os
import base64
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("ENDPOINT_URL", "https://discoveryhub2384343378.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

# Initialize Azure OpenAI Service client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)


def get_completion_from_messages(messages, model="gpt-4o", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
    )
    # print(response)
    return response.choices[0].message.content


def get_system_messages(movie_data, watchlist):
    return [
        {
            "role": "system",
            "content": "You are a recommendation system and watchlist manager for films. Help the user select films to watch. Ask them to describe the kind of film they want to watch and give them recommendations. Ask if the want to add the film or films to their watchlist. You will receive a list of film data containing name, rating and genres of the film in the next message. You will receive the current state of watchlist in message after that.",
        },
        {"role": "system", "content": f"Film data: {json.dumps(movie_data)}"},
        {
            "role": "system",
            "content": f"Current watchlist: {', '.join([movie for movie in watchlist])}",
        },
        {
            "role": "system",
            "content": "ALWAYS output each response as JSON which has field 'answer' containing textual response to the user, and 'watchlist' which contains the updated watchlist. ALWAYS format the output as valid JSON string that can be parsed by Python's json.load(). Don't output markdown code block!",
        },
    ]


def main():
    with open("movies.json", "r") as file:
        movie_data = json.load(file)

    print(
        "Welcome to the AI-driven movie watchlist! We burn only 2.5 dinosaurs per query :-)"
    )
    print(
        "What kind of film would you like to watch? Ask me for recommendations, or type 'exit' to quit."
    )

    watchlist = []
    conversation = []

    while True:
        user_query = input("Query: ")

        if user_query.lower() == "exit":
            if len(watchlist) > 0:
                print("Here are the films in your watchlist:")
                for movie in watchlist:
                    print(f"- {movie}")
            print("Goodbye!")
            break

        conversation.append({"role": "user", "content": user_query})

        system_messages = get_system_messages(movie_data, watchlist)
        request_messages = system_messages + conversation

        ai_completion = get_completion_from_messages(request_messages)
        # print(ai_completion)
        try:
            json_response = json.loads(ai_completion)
        except:
            print(
                "Error: AI response is not valid JSON. Retrying with added instruction."
            )
            retry_messages = request_messages + [
                {
                    "role": "user",
                    "content": "Output the response as JSON which has field 'answer' containing textual response to the user, and 'watchlist' which contains the updated watchlist as JSON array",
                }
            ]
            ai_completion = get_completion_from_messages(retry_messages)
            json_response = json.loads(ai_completion)

        ai_answer = json_response["answer"]
        watchlist = json_response["watchlist"]

        conversation.append({"role": "assistant", "content": ai_answer})

        print(f"Response: {ai_answer}")
        print(f"Watchlist: {watchlist}")


if __name__ == "__main__":
    main()
