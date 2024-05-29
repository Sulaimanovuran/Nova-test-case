# for 1st case
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

# for 2nd case
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

from gdrive.settings import SCOPES, SERVICE_ACCOUNT_FILE, PARENT_FOLDER_ID

"""Вариант 1 нужно каждый раз проходить интерактивную авторизацию что не подходит в нашем случае но знать полезно,
    вроде"""
# Отключаем проверку CSRF для упрощения тестирования
@csrf_exempt
def create_file(request) -> JsonResponse:
    if request.method == "POST":
        try:
            # Преобразуем тело запроса из JSON в словарь
            data: dict = json.loads(request.body)
            name = data.get('name', '')
            data_value = data.get('data', '')

            # Авторизация в аккаунт Google
            auth_obj = GoogleAuth()
            auth_obj.LocalWebserverAuth()

            #Подключаемся к Google Drive
            drive = GoogleDrive(auth_obj)

            # Создаем файл 
            file = drive.CreateFile({'title': f"{name}"})
            # Добавляем содержание в файл
            file.SetContentString(data_value)
            # Загружаем файл
            file.Upload()

            return JsonResponse({"message": f"Файл {name} успешно загружен =)"}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        except Exception as ex:
            return JsonResponse({"error": f"Возникла непредвиденная  ошибка =(\n{ex}"})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)



"""Вариант 2, более подходящий для нашего случая"""

def authenticate():
    # Авторизуемся с помощью сервисного аккаунта и файла авторизации
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

# Отключаем проверку CSRF для упрощения тестирования
@csrf_exempt
def create_upload_file(request) -> JsonResponse:
    if request.method == "POST":
        try:
            # Преобразуем тело запроса из JSON в словарь
            data: dict = json.loads(request.body)
            name = data.get('name', '')
            data_value = data.get('data', '')

            # Преобразуем data_value в байты
            data_bytes = data_value.encode('utf-8')

            # Авторизация в аккаунт Google
            credentials = authenticate()

            #Подключаемся к Google Drive
            service = build('drive', 'v3', credentials=credentials)

            # Определяем имя и целевую папку
            file_metadata = {
                "name": name,
                "parents": [PARENT_FOLDER_ID],
            }

            # Создаем объект файла
            media = MediaIoBaseUpload(BytesIO(data_value.encode()), mimetype='text/plain')
            
            # Загружаем созданный файл
            file = service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()

            return JsonResponse({"message": f"Файл {name} успешно загружен =)"}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        except Exception as ex:
            print(ex)
            return JsonResponse({"error": f"Возникла непредвиденная  ошибка =(\n{ex}"})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)