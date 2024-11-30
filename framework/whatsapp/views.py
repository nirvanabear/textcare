from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

import os
import environ
from twilio.rest import Client

import requests
import json



# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


def add_first_line(original, string):
    # file = open(original, 'w')
    # file.close()
    with open(original,'a+') as f:
        with open("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt",'a') as f2:
            f2.write(string)
            f2.write("\n")
            f.seek(0, 0)
            f2.write(f.read())
    os.remove(original)
    os.rename("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt", original)


@csrf_exempt
def message(request):
    user = request.POST.get('From')
    message = request.POST.get('Body')
    print(f'{user} says {message}')

    # with open("/home/ubuntu/textcare/framework/staticfiles/new.txt", "w") as file:
    #     file.write("Your text goes here")
    #     file.close()
    filename_user = user[11:]
    try:
        message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + filename_user + "_log.txt"
        # message_log = "/home/ubuntu/textcare/framework/staticfiles/messages.txt"
        # new_log = "/home/ubuntu/textcare/framework/staticfiles/new.txt"
        message_w_id = "--- " + message
        add_first_line(message_log, message_w_id)
    
    # # add_first_line(message_log, message_w_id)

    # with open(message_log,'r') as f:
    #     with open(new_log,'w') as f2: 
    #         f2.write(message_w_id)
    #         f2.write(f.read())
    # # os.remove(message_log)
    # os.rename('new.txt', message_log)

        response = MessagingResponse()
        # response.message('Message received.')
        return HttpResponse(str(response))

    except:
        response = MessagingResponse()
        response.message(message_log)
        return HttpResponse(str(response))

# @csrf_exempt
# age(self):
#     return HttpResponse('Hello!')


##################

def chat(request):
    """Chat function for WhatsApp sending"""

    # account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
    # auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
    # client = Client(account_sid, auth_token)

    # context = {'message': message.body}

    message = "template check"

    context = {'message': message}

    return render(request, 'chat.html', context=context)


def set_chat(request):
    '''Passes contact number to the chat session'''
    user_input = json.loads(request.body)

    make_str = str(user_input)
    filename = make_str[18:50]
    phone_num = make_str[-12:-2]

    message_log = "/home/ubuntu/textcare/framework/staticfiles/" + filename
    add_first_line(message_log, "~~~~~~~~~~~~~~~~~~~~")

    context = {
        'make_str': make_str,
        'filename': filename,
        'phone_num': phone_num,
        'request': request,
        # 'body': json.loads(request.POST.dict())
    }

    # return render(request, 'set_chat.html' context=context)
    return render(request, 'set_chat.html', context=context)



# @csrf_exempt
def previous_send_message(request):
#     """Chat function for WhatsApp sending"""

#     account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
#     auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
#     client = Client(account_sid, auth_token)

#     # user_input = request.POST.get('Headers')
#     # user_input = json.dumps(request.POST.dict())
#     user_input = json.loads(request.body)
#     # user_input = request
#     # user_input = "WHY?"

#     make_str = str(user_input)
#     cut_front = make_str[10:]
#     message_edit = cut_front[:-2]
#     phone_num = make_str[-23:-2]

#     # output = ''
#     # for key, value in user_input.items():
#     #     output += key, ":", value, ", "


#     message_log = "/home/ubuntu/textcare/framework/staticfiles/messages.txt"
#     message_w_id = "*** " + message_edit
#     add_first_line(message_log, message_w_id)

#     context = {
#         'message': message.body,
#         'message_edit': message_edit,
#         'phone_num': phone_num,
#         'make_str': make_str,
#         'request': request,
#         'body': json.loads(request.POST.dict())
#     }


    # return render(request, 'show_context.html', context=context)
    return render(request, 'show_context.html')


###############


##################

def open_chat(request):
    """Chat function for WhatsApp sending"""

    # account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
    # auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
    # client = Client(account_sid, auth_token)


    # context = {'message': message.body}

    # user_input = json.loads(request.body)

    # make_str = str(user_input)
    # filename = make_str[18:37]
    # phone_num = make_str[-12:-2]


    # message = "template check"

    # context = {'make_str': make_str}

    return render(request, 'open_chat.html')





# @csrf_exempt
def send_message(request):
    """Chat function for WhatsApp sending"""

    account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
    auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
    client = Client(account_sid, auth_token)

    # user_input = request.POST.get('Headers')
    # user_input = json.dumps(request.POST.dict())
    user_input = json.loads(request.body)
    # user_input = request
    # user_input = "WHY?"

    make_str = str(user_input)
    phone_num = make_str[12:22]
    cut_front = make_str[34:]
    body = cut_front[:-2]

    # output = ''
    # for key, value in user_input.items():
    #     output += key, ":", value, ", "
    # whatsapp_num = f"whatsapp:+1{phone_num}"
    twilio_phone = f"{env('TWILIO_PHONE')}"

    message = client.messages.create(
        body=f"{body}",
        from_=f"whatsapp:+1{twilio_phone}",
        to=f"whatsapp:+1{phone_num}",
    )
    print(message.body)

    message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + phone_num + "_log.txt"
    message_w_id = "*** " + body
    add_first_line(message_log, message_w_id)

    context = {
        'message': message.body,
        'phone_num': phone_num,
        'make_str': make_str,
        'request': request,
        # 'whatsapp_num': whatsapp_num,
        # 'body': json.loads(request.POST.dict())
    }


    return render(request, 'show_context.html', context=context)