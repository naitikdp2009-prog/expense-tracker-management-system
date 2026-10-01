from flask import Blueprint, render_template, request, jsonify
from services.chatbot import process_chat_message

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_view():
    return render_template('chat.html')

@chat_bp.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'reply': 'Please type a question about your expenses or budget.'})

    response_data = process_chat_message(user_message)
    return jsonify(response_data)
