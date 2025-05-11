import io
import re
import unicodedata
import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
import pandas as pd
from Db_handler.Database import EmailDatabase
from datetime import datetime
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from io import BytesIO


db = EmailDatabase()
def clean_request(s: str):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')
    

    # Suppression des espaces multiples
    s = re.sub(r"\s+", " ", s).strip()
    return s

def convert_excel(res,id_msg):
        df = pd.DataFrame(res)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Response')
        
        # Prepare file for saving
        excel_content = output.getvalue()
        file_name = f"response_{id_msg}.xlsx"
        
        # Save to storage
        file_path = default_storage.save(
            f"excel_responses/{file_name}", 
            ContentFile(excel_content)
        )
        
        return file_path
def read_excel(id_msg):
    path_of_excel = "excel_responses/response_"
    file_path = f"{path_of_excel}{id_msg}.xlsx"
    if default_storage.exists(file_path):
        with default_storage.open(file_path, mode='rb') as excel_file:
            df = pd.read_excel(excel_file, engine='openpyxl',index_col=None)
        return df

def send_request(payload: str):
    import requests
    import json

    url = "http://127.0.0.1:8081/process/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "request": clean_request(payload)
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.status_code)
    try:
        
        return response.json()
    except json.JSONDecodeError:
        print("Réponse non JSON :", response.text)

# Exemple d'appel

# Create your views here.
def index(request):
    
    
    return render(request, 'chat.html')
def all_conversations(request):
    conversations = db.historique()
    return JsonResponse({"conversations": conversations})

def all_msg_by_conv(request, conv_id):
    type_res = "str"
    message = ""
    if conv_id:
        messages = db.get_all_msg_con(conv_id)
        for message in messages:
            if message.get("res_user").endswith(".xlsx"):
                 print(True)
                 message_x = read_excel(message.get("msg_id"))
                 print(message_x.head())
                 message["message"] = message_x.to_dict(orient="records")
                 message["type_res"] = "list"
            else :
                message["type_res"] = "str"

                
        return JsonResponse({"messages": messages})
    return JsonResponse({"error": "conv_id missing"}, status=400)


@csrf_exempt 
def create_conversation(request): 
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    msg = request.POST.get('message')
    conv_id_from_post = request.POST.get('conv_id', None) 

    current_date = datetime.now()
    format_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    user_id = "for_now_mehdi" 

    if not msg:
        return JsonResponse({"error": "No message provided"}, status=400)

    final_conv_id = None 

  
    if conv_id_from_post:
        print(f"Received existing conv_id: {conv_id_from_post}") 
      
        msg_id = db.insert_chat(msg, format_date, user_id, conv_id_from_post)
        print(msg_id)
        final_conv_id = conv_id_from_post 
    else:
        print("No conv_id received, creating new conversation.") 
        new_conv_id = str(uuid.uuid4())
        msg_id = db.insert_chat(msg, format_date, user_id, new_conv_id)
        final_conv_id = new_conv_id 

    
    bot_response = {
        "msg_id": msg_id,
        "role": "bot",
        "content": msg, 
        "timestamp": format_date, 
    }

    return JsonResponse({
        "status": "inserted",
        "conv_id": final_conv_id, 
        "message": bot_response
    })
@csrf_exempt
def update_conversation(request, msg_user, id_msg):
    print(f"update_conversation called with msg_user='{msg_user}', id_msg='{id_msg}'")

    response = send_request(clean_request(msg_user))
    res= response.get("response", "")
    req_sql = response.get("sql_query", "")
    print("le type de res est ",type(res))
    date_res = datetime.now()
    format_date = date_res.strftime("%Y-%m-%d %H:%M:%S")

    

    if response:
        if type(res) == str:
              
                    type_res = "text"
                    success = db.insert_res_msg(res, format_date, id_msg,req_sql)
                    print("Insert success:", success)
        else:
                   
                    type_res = "list"
                    file_path = convert_excel(res,id_msg)
                    print(convert_excel(res,id_msg))
                    success = db.insert_res_msg(file_path, format_date, id_msg,req_sql)
                    print("Insert success:", success)



        if success:
            return JsonResponse({
                "status": "updated",
                "response": res,
                "format_date": format_date,
                "id_msg": id_msg,
                "type_res": type_res
            })
        else:
            return JsonResponse({"error": "DB insert failed"}, status=400)
    else:
        return JsonResponse({"error": "Ollama response empty"}, status=400)



 
