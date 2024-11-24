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


@csrf_exempt
def message(request):
    user = request.POST.get('From')
    message = request.POST.get('Body')
    print(f'{user} says {message}')

    response = MessagingResponse()
    response.message('Congratulations, George!!!')
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


@csrf_exempt
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



    # output = ''
    # for key, value in user_input.items():
    #     output += key, ":", value, ", "

    message = client.messages.create(
        body=f"{user_input}",
        from_="whatsapp:+1***REMOVED***",
        to="whatsapp:+1***REMOVED***",
    )
    print(message.body)

    context = {
        'message': message.body,
        'request': request,
        'body': json.loads(request.POST.dict())
    }


    return render(request, 'show_context.html', context=context)
