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
        
    return StreamingHttpResponse(generate(), content_type='text/plain')

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
