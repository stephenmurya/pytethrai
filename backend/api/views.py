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

# Pricing Dict (Cost per 1k tokens)
# Note: These are rough estimates for MVP
MODEL_PRICING = {
    'openai/gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'openai/gpt-4': {'input': 0.03, 'output': 0.06},
    'google/gemini-pro': {'input': 0.000125, 'output': 0.000375},
    'anthropic/claude-3-opus': {'input': 0.015, 'output': 0.075},
}

DEFAULT_PRICING = {'input': 0.001, 'output': 0.002}

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
        
    
    # Resolve Workspace Context
    workspace_id = request.query_params.get('workspace')
    final_workspace = None
    if workspace_id:
        try:
            from teams.models import WorkspaceMember, Workspace
            if WorkspaceMember.objects.filter(workspace_id=workspace_id, user=request.user).exists():
                final_workspace = Workspace.objects.get(id=workspace_id)
        except Exception as e:
            print(f"Error resolving workspace: {e}")

    # Get or create chat
    if chat_id:
        try:
            chat = Chat.objects.get(id=chat_id)
            
            # Access Verification
            has_access = (chat.user == request.user)
            if not has_access and chat.workspace:
                 from teams.models import WorkspaceMember
                 has_access = WorkspaceMember.objects.filter(workspace=chat.workspace, user=request.user).exists()
            
            if not has_access:
                 return Response({"error": "Access denied"}, status=403)

        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)
    else:
        chat = Chat.objects.create(user=request.user, title=content[:30], workspace=final_workspace)
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
        
        # Post-stream processing: Logging
        try:
            # 1. Estimate Tokens
            # Simple char-count estimation (1 token ~= 4 chars)
            input_tokens = len(content) // 4  # content is user prompt from outer scope
            output_tokens = len(full_response) // 4
            
            # 2. Calculate Cost
            pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
            input_cost = (input_tokens / 1000) * pricing['input']
            output_cost = (output_tokens / 1000) * pricing['output']
            total_cost = input_cost + output_cost
            
            
            # 3. Get Workspace Context
            # Already resolved in outer scope as final_workspace
            
            # 4. Create Log
            from analytics.models import UsageLog
            UsageLog.objects.create(
                user=request.user,
                workspace=final_workspace,
                model_name=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_estimate=total_cost
            )
            
        except Exception as e:
            print(f"Error logging usage: {e}")
        
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
    workspace_id = request.query_params.get('workspace')
    
    if workspace_id:
        # Verify Membership for Collaboration
        from teams.models import WorkspaceMember
        if not WorkspaceMember.objects.filter(workspace_id=workspace_id, user=request.user).exists():
             return Response({"error": "Access denied"}, status=403)

        # Shared: Return ALL chats in this workspace (collaboration mode)
        chats = Chat.objects.filter(workspace_id=workspace_id).order_by('-updated_at')
    else:
        # Personal view - show PRIVATE chats (no workspace)
        chats = Chat.objects.filter(user=request.user, workspace__isnull=True).order_by('-updated_at')
        
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_chat(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Access Verification
        has_access = (chat.user == request.user)
        if not has_access and chat.workspace:
             from teams.models import WorkspaceMember
             has_access = WorkspaceMember.objects.filter(workspace=chat.workspace, user=request.user).exists()
        
        if not has_access:
             return Response({"error": "Access denied"}, status=403)

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
