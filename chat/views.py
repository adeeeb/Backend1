from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import logging
from .models import ChatMessage
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            # تحليل البيانات المرسلة من الفرونت إند
            data = json.loads(request.body)
            message = data.get('message')
            session_id = data.get('session_id')
            user_id = data.get('user_id')
            summary = data.get('summary', '')

            logger.info(f"Received data from frontend: {data}")

            # التحقق من صحة البيانات الأساسية
            if not message or session_id is None:
                return JsonResponse({
                    "message": "Message and session_id are required.",
                    "summary": "",
                    "session_id": session_id if session_id is not None else ""
                }, status=400)

            # إعداد الحمولة (payload) لإرسالها إلى الذكاء الاصطناعي
            payload = {
                "message": message,
                "summary": summary,
                "session_id": session_id
            }
            if user_id:
                payload["user_id"] = user_id

            logger.info(f"Payload to AI: {payload}")

            try:
                ai_response_raw = requests.post(
                    "https://syrian-heritage-website.onrender.com/chat",
                    json=payload,
                    timeout=60
                )
                logger.info(f"AI API Status Code: {ai_response_raw.status_code}")
                logger.info(f"AI API Raw Response: {ai_response_raw.text}")

                try:
                    ai_response = ai_response_raw.json()
                    logger.info(f"Parsed AI response: {ai_response}")
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding AI API response: {e}")
                    return JsonResponse({
                        "message": "Invalid response format from AI service.",
                        "summary": summary,
                        "session_id": session_id
                    }, status=500)

                # استخراج الرد من الذكاء الاصطناعي
                response_text = ai_response.get('message')
                new_summary = ai_response.get('summary', summary)

                if response_text is None:
                    response_text = "Sorry, I couldn't generate a response."

                # إذا كان المستخدم مسجلاً، نقوم بتخزين الرسالة في قاعدة البيانات
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        user = None
                    ChatMessage.objects.create(
                        user=user,
                        session_id=session_id,
                        message=message,
                        response=response_text,
                        summary=new_summary
                    )

                return JsonResponse({
                    "message": response_text,
                    "summary": new_summary,
                    "session_id": session_id,
                    "user_id": user_id
                })

            except requests.exceptions.RequestException as e:
                logger.error(f"AI Connection Error: {e}")
                return JsonResponse({
                    "message": "Sorry, we couldn't connect to the AI service. Please try again later.",
                    "summary": summary,
                    "session_id": session_id
                }, status=500)

        except json.JSONDecodeError:
            return JsonResponse({
                "message": "Invalid JSON data.",
                "summary": "",
                "session_id": ""
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            return JsonResponse({
                "message": "Sorry, something went wrong. Please try again later.",
                "summary": "",
                "session_id": session_id if session_id else ""
            }, status=500)

    return JsonResponse({
        "message": "Invalid request method.",
        "summary": "",
        "session_id": ""
    }, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage

@csrf_exempt
def get_chat_history(request, user_id):
    if request.method == 'GET':
        try:
            # استرجاع جميع الرسائل الخاصة بالمستخدم
            chat_messages = ChatMessage.objects.filter(user_id=user_id).order_by('timestamp')
            messages_list = []
            for msg in chat_messages:
                messages_list.append({
                    "message": msg.message,
                    "response": msg.response,
                    "summary": msg.summary,
                    "session_id": msg.session_id,                    "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # استخدام timestamp بدلاً من created_at
                })

            return JsonResponse({
                "messages": messages_list,
                "user_id": user_id
            })

        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return JsonResponse({
                "message": "Sorry, something went wrong while retrieving chat history.",
                "user_id": user_id
            }, status=500)

    return JsonResponse({
        "message": "Invalid request method.",
        "user_id": user_id
    }, status=405)