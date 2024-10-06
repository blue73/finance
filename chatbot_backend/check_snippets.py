import json

def print_snippets():
    with open('/home/ubuntu/chatbot_project/text_snippets.json', 'r', encoding='utf-8') as f:
        snippets = json.load(f)
    for key, value in snippets.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    print_snippets()
