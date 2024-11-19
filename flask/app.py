from flask import Flask, request, jsonify, render_template_string, redirect
import requests
from datetime import datetime

app = Flask(__name__)

models = [
    "yanzgpt-revolution-25b-v3.0",  # Default model
    "yanzgpt-legacy-72b-v3.0"       # Pro model
]

model_names = {
    "yanzgpt-revolution-25b-v3.0": "FARAI-PRO-MINI",
    "yanzgpt-legacy-72b-v3.0": "FARAI-PRO"
}

current_model_index = 0
chat_history = []  # Menyimpan seluruh pesan dari pengguna dan bot


def yanzgpt_revolution_system_prompt():
    return """Kamu adalah ChatFARAI, asisten AI yang ramah dan cerdas, diciptakan oleh Farrel. Berikan jawaban yang informatif, mendalam, dan sesuai konteks."""


def yanzgpt_legacy_system_prompt():
    return """Kamu adalah ChatFARAI versi Pro, asisten AI yang mendalam dan akurat. Berikan jawaban yang informatif dan membantu dalam berbagai topik."""


def YanzGPT(query, model):
    headers = {
        "authorization": "Bearer yzgpt-sc4tlKsMRdNMecNy",
        "content-type": "application/json"
    }

    if any(keyword in query.lower() for keyword in ['jam', 'waktu', 'sekarang pukul']):
        current_time = datetime.now().strftime("%H:%M:%S")
        return f"Saat ini jam {current_time}."

    system_prompt = yanzgpt_revolution_system_prompt() if model == "yanzgpt-revolution-25b-v3.0" else yanzgpt_legacy_system_prompt()

    data = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "model": model
    }

    response = requests.post("https://yanzgpt.my.id/chat", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatFARAI</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: #ffffff;
        }
        .chat-container {
            width: 100%;
            max-width: 600px;
            height: 100%;
            max-height: 100%;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }
        .header {
            background: #333;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header .title {
            font-size: 20px;
            font-weight: bold;
        }
        .header .model-switch button {
            background: #2575fc;
            color: #fff;
            border: none;
            padding: 5px 15px;
            font-size: 14px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .header .model-switch button:hover {
            background: #6a11cb;
        }
        .chat-area {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .chat-area .message {
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            animation: fadeIn 0.3s ease-in-out;
        }
        .chat-area .user {
            align-self: flex-end;
            background: #2575fc;
        }
        .chat-area .bot {
            align-self: flex-start;
            background: #444;
        }
        .chat-area .loading {
            align-self: center;
            padding: 10px;
            background: #444;
            border-radius: 10px;
            animation: fadeIn 0.3s ease-in-out;
        }
        .input-container {
            display: flex;
            padding: 10px;
            background: #333;
            gap: 10px;
        }
        .input-container input {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        .input-container button {
            background: #6a11cb;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .input-container button:hover {
            background: #2575fc;
        }
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div class="title">ChatFARAI</div>
            <div class="model-switch">
                <form action="/switch-model" method="post">
                    <button type="submit">{{ model_name }}</button>
                </form>
            </div>
        </div>
        <div class="chat-area" id="chat-area">
            {% for message in chat_history %}
                <div class="message {{ message['sender'] }}">
                    {{ message['content'] }}
                </div>
            {% endfor %}
            <div id="loading" class="loading" style="display: none;">
                <p>AI sedang memproses pesan...</p>
            </div>
        </div>
        <div class="input-container">
            <form action="/send-message" method="post" style="display: flex; width: 100%; gap: 10px;" id="chat-form">
                <input type="text" name="user_input" placeholder="Ketik pesan Anda di sini..." required>
                <button type="submit">Kirim</button>
            </form>
            <form action="/delete-all-messages" method="post" style="margin: 0;">
                <button type="submit" style="background-color: red; color: white;">Hapus Semua Pesan</button>
            </form>
        </div>
    </div>
    <script>
        // Menambahkan event listener untuk menunjukkan indikator loading
        document.getElementById("chat-form").addEventListener("submit", function() {
            document.getElementById("loading").style.display = "block"; // Menampilkan loading indicator
        });
    </script>
</body>
</html>"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        HTML_TEMPLATE,
        chat_history=chat_history,
        model_name=model_names[models[current_model_index]]
    )


@app.route("/send-message", methods=["POST"])
def send_message():
    user_input = request.form.get("user_input")
    print(f"Received message from user: {user_input}")  # Debug log to see the input received
    if user_input:
        chat_history.append({"sender": "user", "content": user_input})
        model = models[current_model_index]
        response = YanzGPT(user_input, model)
        chat_history.append({"sender": "bot", "content": response})
        print(f"Bot response: {response}")  # Debug log for the bot's response
    else:
        print("No user input received.")  # Log in case no input was received
    return redirect("/")

@app.route("/delete-all-messages", methods=["POST"])
def delete_all_messages():
    global chat_history
    chat_history = []
    print("All messages deleted.")  # Log message deletion
    return redirect("/")  
    
@app.route("/switch-model", methods=["POST"])
def switch_model():
    global current_model_index
    current_model_index = (current_model_index + 1) % len(models)
    print(f"Model switched to: {models[current_model_index]}")  # Log when model is switched
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
