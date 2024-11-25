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
    with open(original,'r') as f:
        with open("/home/ubuntu/textcare/framework/staticfiles/new.txt",'w') as f2: 
            f2.write(string)
            f2.write("\n")
            f2.write(f.read())
    os.remove(original)
    os.rename("/home/ubuntu/textcare/framework/staticfiles/new.txt", original)


@csrf_exempt
def message(request):
    user = request.POST.get('From')
    message = request.POST.get('Body')
    print(f'{user} says {message}')

    # with open("/home/ubuntu/textcare/framework/staticfiles/new.txt", "w") as file:
    #     file.write("Your text goes here")
    #     file.close()

    message_log = "/home/ubuntu/textcare/framework/staticfiles/messages.txt"
    new_log = "/home/ubuntu/textcare/framework/staticfiles/new.txt"
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
    response.message('Message received.')
    return HttpResponse(str(response))

# @csrf_exempt
# def message(self):
#     return HttpResponse('Hello!')


##################

def chat(request):
    """Chat function for WhatsApp sending"""

    # account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
    # auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
    # client = Client(account_sid, auth_token)

    # message = client.messages.create(
    #     body="Sup, dog!",
    #     from_="whatsapp:+1***REMOVED***",
    #     to="whatsapp:+1***REMOVED***",
    # )
    # print(message.body)

    # context = {'message': message.body}

    message = "template check"

    context = {'message': message}

    return render(request, 'chat.html', context=context)





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
    cut_front = make_str[10:]
    message_edit = cut_front[:-2]

    # output = ''
    # for key, value in user_input.items():
    #     output += key, ":", value, ", "

    message = client.messages.create(
        body=f"{message_edit}",
        from_="whatsapp:+1***REMOVED***",
        to="whatsapp:+1***REMOVED***",
    )
    print(message.body)

    message_log = "/home/ubuntu/textcare/framework/staticfiles/messages.txt"
    message_w_id = "*** " + message_edit
    add_first_line(message_log, message_w_id)

    context = {
        'message': message.body,
        'message_edit': message_edit,
        'request': request,
        'body': json.loads(request.POST.dict())
    }


    return render(request, 'show_context.html', context=context)
