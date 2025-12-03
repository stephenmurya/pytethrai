from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chat, Message
from .serializers import UserSerializer, ChatSerializer, MessageSerializer
from .ai import stream_chat_response
import json
import uuid

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response(UserSerializer(user).data)
    return Response({"error": "Invalid credentials"}, status=400)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})

@api_view(['GET'])
def user_view(request):
    return Response(UserSerializer(request.user).data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    login(request, user)
    return Response(UserSerializer(user).data)

@api_view(['POST'])
def chat_send(request):
    chat_id = request.data.get('chatId')
    content = request.data.get('content')
    model = request.data.get('model', 'google/gemini-2.0-flash-exp:free')
    
    if not content:
        return Response({"error": "Content is required"}, status=400)
        
    # Get or create chat
    if chat_id:
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)
    else:
        chat = Chat.objects.create(user=request.user, title=content[:30])
        chat_id = str(chat.id)

    # Save user message
    Message.objects.create(chat=chat, role='user', content=content)
    
    # Prepare messages for AI
    messages = []
    # Add system prompt if needed
    # messages.append({"role": "system", "content": "You are a helpful assistant."})
    
    # Get recent history (optional, for context)
    recent_messages = chat.messages.all().order_by('created_at')
    for msg in recent_messages:
        messages.append({"role": msg.role, "content": msg.content})
        
    # Stream response
    def generate():
        full_response = ""
        for chunk in stream_chat_response(messages, model):
            full_response += chunk
            yield chunk
        
        # Save assistant message after stream
        Message.objects.create(chat=chat, role='assistant', content=full_response)
        
    response = StreamingHttpResponse(generate(), content_type='text/plain')
    response['Chat-Id'] = chat_id

    # Generate title in background if it's a new chat (or title is default)
    if len(messages) <= 2:  # User message + (optional) system prompt
        def generate_title():
            try:
                import requests
                import os
                
                API_KEY = os.getenv('OPENROUTER_API_KEY')
                if not API_KEY:
                    return

                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://tethrai.com", 
                    "X-Title": "TethrAI"
                }
                
                prompt = f"Generate a very short, concise title (max 5 words) for a chat that starts with this message: '{content}'. Return ONLY the title, no quotes or extra text."
                
                data = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    title = resp.json()['choices'][0]['message']['content'].strip().strip('"')
                    chat.title = title
                    chat.save()
            except Exception as e:
                print(f"Error generating title: {e}")

        import threading
        threading.Thread(target=generate_title).start()

    return response

@api_view(['GET'])
def chat_history(request):
    chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_chat(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)
    except Chat.DoesNotExist:
        return Response({"error": "Chat not found"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_models(request):
    """Get available OpenRouter models with fallback to default list."""
    from .models_service import get_models_with_fallback
    
    try:
        models, error_msg = get_models_with_fallback()
        
        response_data = {
            "models": models,
            "error": error_msg  # Will be None if API succeeded
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            "error": f"Failed to retrieve models: {str(e)}",
            "models": []
        }, status=500)
