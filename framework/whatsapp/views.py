from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

import os
import environ
from twilio.rest import Client

import requests
import json
import re

import openai
from django.db import transaction

from .models import Conversation, ClientLog, ChatSession, ChatLog, Message
from .utils import send_message2, logger
from chat.models import Room, Channel

from django.utils.timezone import now
from datetime import datetime
import pytz
from django.conf import settings

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

openai.api_key = f"{env('OPENAI_API_KEY')}"

logger = logging.getLogger('django')
dtn = datetime.now().strftime('%Y-%m-%d %H:%M') + " "

def add_first_line(original, string):
    '''Adds a new line to a text file as the first line.'''
    with open(original,'a+', encoding='utf-8') as f:
        with open(str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "new.txt",'a', encoding='utf-8') as f2:
            f2.write(string)
            f2.write("\n")
            f.seek(0, 0)
            f2.write(f.read())
    os.remove(original)
    os.rename(str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "new.txt", original)



def triage(number, message, waitlist, triage_path, triage_state): 
    '''Increments incoming calls through the triage question pathway'''
    message = message.lower()

    # Bypass triage questions and send caller to doctor chat.
    with open(waitlist,'r') as f:
        for line in f:
            if line == number:
                bypass_note = "Call forwarded to chat."
                print(bypass_note)
                return bypass_note

    # Checks triage state document and displays next question.
    conditions_list = []
    if os.path.exists(triage_state):
        with open(triage_state, 'r+') as g:
            with open(triage_path, 'r') as h:
                path_list = h.readlines()
                for line in path_list:
                    line_list = line[:-1].split(",")
                    line_list[1] = int(line_list[1])
                    line_list[2] = int(line_list[2])
                    conditions_list.append(line_list)
                print(conditions_list)
            # Reads current state.
            g.seek(0, 0)
            state = g.readline()
            print('state: ' + state)
            new_index = 0
            # Initial condition.
            if state == '':  
                question = conditions_list[0][0]
                g.seek(0, 0)
                g.write(str(0))
            # Choose 'yes' or 'no'.
            else:
                index = int(state)
                if message == 'y':
                    new_index = conditions_list[index][1]
                else:
                    new_index = conditions_list[index][2]
                question = conditions_list[new_index][0]
                g.seek(0, 0)
                g.write(str(new_index))
            # End condition.
            if new_index == 15:
                g.seek(0, 0)
                g.write(str(0))
                link = f"{env('CHAT_LINK')}"
                question += " Please click on the link to proceed: " + link
                # Adds number to doctor's waitlist.
                with open(waitlist, 'a') as i:
                    i.write(str(number))
    else:
        # Creates the state file if none.
        with open(triage_state, 'w+') as g:
            with open(triage_path, 'r') as h:
                path_list = h.readlines()
                for line in path_list:
                    line_list = line[:-1].split(",")
                    line_list[1] = int(line_list[1])
                    line_list[2] = int(line_list[2])
                    conditions_list.append(line_list)
                print(conditions_list)
            question = conditions_list[0][0]
            g.seek(0, 0)
            g.write(str(0))
    print(question)
    return question



@csrf_exempt
def message(request):
    '''Receives message and passes it to the prewritten
    question and answer version of triage.'''
    user = request.POST.get('From')
    message = request.POST.get('Body')
    print(f'{user} says {message}')
 
    number = user[11:]
    try:
    
        message_log = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + number + "_log.txt"
        message_w_id = "--- " + message
        add_first_line(message_log, message_w_id)
    

        waitlist = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "waitlist.txt"
        triage_path = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "triage_path.txt"
        triage_state = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + number + "_state.txt"

        question = triage(number, message, waitlist, triage_path, triage_state)


        response = MessagingResponse()
        response.message(question)
        return HttpResponse(str(response))

    except:
        with open(triage_state, 'w+') as g:
            g.write(str(0))

        response = MessagingResponse()
        response.message('Triage error. Please try again.')
        return HttpResponse(str(response))



def chat(request):
    """Chat function for WhatsApp sending"""

    message = "template check"
    set_chat_url = f"{env('SET_CHAT_URL')}"

    context = {
        'message': message,
        'set_chat_url': set_chat_url
    }
    return render(request, 'chat.html', context=context)



def set_chat(request):
    '''Adds contact number to the chat session.'''
    user_input = json.loads(request.body)
    logger.debug(type(user_input))

    # Parses everything coming from the javascript
    # fetch() function in chat.html.
    make_str = str(user_input)
    filename = make_str[33:52]
    phone_num = make_str[-12:-2]
    token_v0 = make_str[65:]
    token = token_v0[:-22]

    filename = user_input["file"]
    phone_num = user_input["to"]
    token = user_input["captcha"]

    logger.debug("Request body: " + str(user_input))

    recaptcha_url = " https://www.google.com/recaptcha/api/siteverify"
    param_dict = {
        'secret': f"{env('RECAPTCHA_SECRET')}",
        'response': token
    }
    recaptcha_resp = requests.get(url=recaptcha_url, params=param_dict)
    recaptcha_data = recaptcha_resp.json()

    logger.debug("~~~~~~~ reCaptcha Response: ~~~~~~~")
    key_values = []
    for key, value in recaptcha_data.items():
        key_values.append(key)
        key_values.append(value)
        logger.debug(str(key) + ": " + str(value))
    key_values = str(key_values)

    message_log = str(settings.BASE_DIR) + filename
    logger.debug("message log: " + message_log)
    add_first_line(message_log, "~~~~~~~~~~~~~~~~~~~~")

    context = {
        'make_str': make_str,
        'filename': filename,
        'phone_num': phone_num,
        'token': token,
        'success': recaptcha_data['success'],
        'challenge_ts': recaptcha_data['challenge_ts'],
        'request': request,
    }

    # Use the render() return instead to view the context dict in Developer Tools
    # return render(request, 'set_chat.html', context=context)
    return JsonResponse(recaptcha_data)



def open_chat(request):
    """Chat function for WhatsApp sending"""
    logger.debug(dtn + "open_chat() function called.")

    send_message_url = f"{env('SEND_MESSAGE_URL')}"
    end_session_url = f"{env('END_SESSION_URL')}"
    issues_url = f"{env('ISSUES_URL')}"

    chat_room, created = Room.objects.get_or_create(name='Room1')

    context = {
        'send_message_url': send_message_url,
        'end_session_url': end_session_url,
        'issues_url': issues_url,
    }
    return render(request, 'open_chat.html', context=context)



def send_message(request):
    """Chat function for WhatsApp sending"""

    account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
    auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
    
    client = Client(account_sid, auth_token)
    user_input = json.loads(request.body)

    make_str = str(user_input)
    phone_num = make_str[12:22]
    cut_front = make_str[34:]
    body = cut_front[:-2]

    twilio_phone = f"{env('TWILIO_PHONE')}"

    message = client.messages.create(
        body=f"{body}",
        from_=f"whatsapp:+1{twilio_phone}",
        to=f"whatsapp:+1{phone_num}",
    )
    logger.debug(message.body)

    message_log = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + phone_num + "_log.txt"
    message_w_id = "Doctor: " + body
    add_first_line(message_log, message_w_id)
    logger.debug("Message logged to text file.")

    # Adds message to the chat log.
    try:
        with transaction.atomic():
            client, create_client = ClientLog.objects.get_or_create(
                phone_num=phone_num
            )
            # chat_room, created = Room.objects.get_or_create(name='Room1')
        open_session_set = ChatSession.objects.filter(open_session=True, client=client)
        # Chooses the most recent open session.
        latest = datetime.min.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        session = None
        for item in open_session_set:
            # logger.debug(str(item))
            if item.start_time > latest:
                latest = item.start_time
                session = item
        logger.debug(dtn + f"send_message: session={str(session.session_id)}")

        # Adds new outgoing message to the chat log.
        message_w_id = "Doctor: " + body
        new_message = ChatLog(message=message_w_id, session=session)
        new_message.save()

        # Retrieve all messages from this session.
        session_msgs = ChatLog.objects.filter(session=session)
        log_text = ""
        for chat_msg in session_msgs:
            # logger.debug(chat_msg.message)
            log_text += chat_msg.message

        # Send contents of chat session to websocket window.
        # filtered by session_id and sorted by timestamp
        channel_name = Channel.objects.latest('timestamp').channel_name
        logger.debug(dtn + f"send_message: {channel_name}")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(channel_name, {"type": "chat_message", "message": "Hello from views."})
        # except:
        #     logger.exception("?")

        # logger.debug(dtn + "send_message: no error")
    except:
        response = MessagingResponse()
        response.message(dtn + 'send_message: Database entry error.')
        logger.exception(dtn + 'send_message: Database entry error.')
        return HttpResponse(str(response))




    context = {
        'message': message.body,
        'phone_num': phone_num,
        'make_str': make_str,
        'request': request,
        # 'whatsapp_num': whatsapp_num,
        # 'body': json.loads(request.POST.dict())
    }


    return render(request, 'show_context.html', context=context)



def end_session(request):
    ''' Removes phone number from waitlist.txt to reset TextCare'''
    user_input = json.loads(request.body)

    make_str = str(user_input)
    # filename = make_str[18:50]
    phone_num = make_str[-12:-2]

    # Removes the phone number from the waitlist, which allows
    # the triage session to restart.
    waitlist = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "waitlist.txt"
    # add_first_line(message_log, "~~~~~~~~~~~~~~~~~~~~")
    match_list = []
    with open(waitlist, 'r+') as f:
        with open(str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "new2.txt",'a') as f2:

            f.seek(0, 0)
            num_list = f.readlines()
            for i in range(len(num_list)):
                # if str(num_list[i])[:-1] == phone_num:
                if re.match(phone_num, num_list[i]):
                    match_list.append(i)
            for j in range(len(match_list)-1, -1, -1):
                del num_list[match_list[j]]
            f.seek(0, 0)
            for each in num_list:
                f2.write(each)
    os.remove(waitlist)
    os.rename(str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "new2.txt", waitlist)

    # Resets the triage state.
    triage_state = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + phone_num + "_state.txt"
    with open(triage_state, 'w+') as g:
            g.write('')
            

    # Resets triage state in database.
    try:
        with transaction.atomic():
            client, create_client = ClientLog.objects.get_or_create(
                phone_num=phone_num
            )
        client.state = 20
        client.save()
        
        # Chooses the most recent open session.
        open_session_set = ChatSession.objects.filter(open_session=True, client=client)
        latest = datetime.min.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        session = None
        # print("Min time: ")
        # print(latest)
        for item in open_session_set:
            if item.start_time > latest:
                latest = item.start_time
                session = item
        # Ends the session.
        session.open_session = False
        session.save()
        print("Closing chat session: ")
        print(session)
    except:
        response = MessagingResponse()
        response.message('end_session: Client database entry error.')
        print('end_session: Client database entry error.')
        return HttpResponse(str(response))
 


    # Resets transcript with TriageGPT.
    transcript = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + phone_num + "_transcript.txt"
    with open(transcript, 'w+') as t:
            t.write('')

    context = {
        'match_list': match_list,
        'num_list': num_list,
        'phone_num': phone_num,
        'user_input': user_input,
    }
    return render(request, 'end_session.html', context=context)  



def chat_switch(last_message):
    last_message.append({"role": "system", "content": "You are a triage nurse. Read the conversation between a Triage Nurse and a Patient and give a recommendation for the kind of specialist doctor that should treat the patient."})

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=last_message,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
        )

    # The generated text
    chatgpt_response = response.choices[0].message.content
    return chatgpt_response



########################################

    # Loop the GPT three times
        # Need a state.txt of the loop
    # Then send to chat
    # Post copy of the GPT triage to the bottom of the chat page



### Database version ###
@csrf_exempt
def reply(request):
    # Handles incoming texts and coordinates communication with ChatGPT or live agent via a chat console.
    whatsapp_number = request.POST.get('From').split("whatsapp:")[-1]
    number = whatsapp_number[2:]

    logger.debug("Function start.")      

    print("###########################")
    # Checks ClientLog for entry using the incoming phone number.
    # Creates a new client entry if none exists.
    try:
        with transaction.atomic():
            client, create_client = ClientLog.objects.get_or_create(
                phone_num=number
            )
            # 
            chat_room, created = Room.objects.get_or_create(name='Room1')
    except:
        response = MessagingResponse()
        response.message('Client database entry error.')
        print('Client database entry error.')
        return HttpResponse(str(response))

    # Checks for existing open sessions to join. 
    try:
        if client.state > 20:
            open_session_set = ChatSession.objects.filter(open_session=True)
            if len(open_session_set) == 0:
                client.state = 20
                client.save()
            # Chooses the most recent open session.
            latest = datetime.min.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            session = None
            print("Min time: ")
            print(latest)
            for item in open_session_set:
                if item.start_time > latest:
                    latest = item.start_time
                    session = item
        # Creates a new open session in none exist.
        elif client.state == 20:
            session = ChatSession(
                client=client,
                start_time=now()
            )
            session.save()
    except:
        response = MessagingResponse()
        response.message('Client status error.')
        print('Client status error.')
        return HttpResponse(str(response))

    logger.debug("Database entry and status checked.") 

    ## Database ##
    # If state is 20, create a new session and increment state.
    # If 20 < state < 23, continue chatbot session.
    # If > 22, send end message and increment.
    # If > 23, bypass chatbot for live chat.
    # Live chat view can reset for new session.

    try:
        # Extract the message from the incoming webhook request.
        body = request.POST.get('Body', '')

        # Adds new incoming message to the chat log.
        message_w_id = "Patient: " + body
        new_message = ChatLog(message=message_w_id, session=session)
        new_message.save()
        


        # Logs messages to text file for the incoming phone number.
        message_log = str(settings.BASE_DIR) + "/whatsapp/message_logs/" + "T" + number + "_log.txt"    ## Deprecated ## 
        # message_w_id = "--- " + body
        # Adds message to message log for this phone number.
        add_first_line(message_log, message_w_id)
        logger.debug("After message logged")
        
        # Checks client state and bypasses GPT for live chat if needed.
        if client.state > 23:
            bypass_info = f"Patient state is {client.state}. Bypass to the chat function!"
            logger.debug(bypass_info)
            # Join channel layer, send database contents.
            # render(request, 'chat.html', context=context)
            return HttpResponse('')
            # return render(request, "whatsapp/home.html", context=context)

        # Filter for all messages that match the session id.
        # Add all previous messages to the TriageGPT conversation.
        tscript_text = ''
        session_messages = ChatLog.objects.filter(session_id=session.session_id)
        for each in session_messages:
            tscript_text += each.message
            tscript_text += '\n'
        # Transcript history to be provided to TriageGPT.
        messages = [{"role": "user", "content": tscript_text}]  

        logger.debug("Setup for TriageGPT completed.")      

        # TriageGPT:
        # Prompt engineering to initialize a triage nurse bot.
        messages.append({"role": "system", "content": "You are a Triage Nurse. The incoming message is a conversation between a Patient and a Triage Nurse who is asking questions to determine the kind of health care the Patient needs. Ask two medical triage questions as the Triage Nurse to continue the conversation and get a better understanding of the situation."})

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5
            )

        logger.debug("TriageGPT call complete.")      

        # The generated text from TriageGPT
        chatgpt_response = response.choices[0].message.content

        # Inserts welcome message for new session.
        if client.state == 20:
            chatgpt_response = "Welcome to TextCare! \n\n" + "Triage Nurse: " + chatgpt_response

        # Adds TriageGPT response to ChatLog.
        gpt_response = ChatLog(message=chatgpt_response, session=session)
        gpt_response.save()

        # Concluding message for patient going to live chat after three GPT prompts.
        if client.state > 22:
            # Link connects to the live chat functionality.
            link = f"{env('CHAT_LINK')}"
            link_info = "We'll get you to a doctor now. Please click on the link to proceed: " + link
            chatgpt_response += "\n\n" + link_info
            last_message = [{"role": "user", "content": tscript_text}]
            last_response = chat_switch(last_message) + "\n\n" + link_info
            # Increments state and sends response.
            client.state += 1
            client.save()            
            send_message2(whatsapp_number, last_response)
            return HttpResponse('')
        else:
            # Increments state and sends response.
            client.state += 1
            client.save()
            send_message2(whatsapp_number, chatgpt_response)
            return HttpResponse('')

    except:
        response = MessagingResponse()
        response.message('TriageGPT error. Please try again. :,(')
        return HttpResponse(str(response))
       


def index(request):
    logger.debug("Log message changed.")
    root_path = str(settings.BASE_DIR)
    logger.debug("Django root path: " + str(root_path))
    context = {
        'root_path': root_path,
    }
    return render(request, "whatsapp/home.html", context=context)
