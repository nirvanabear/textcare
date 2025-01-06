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
from .models import Conversation
from .utils import send_message2, logger




# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

openai.api_key = f"{env('OPENAI_API_KEY')}"


def add_first_line(original, string):
    '''Adds a new line to a text file as the first line.'''
    with open(original,'a+', encoding='utf-8') as f:
        with open("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt",'a', encoding='utf-8') as f2:
            f2.write(string)
            f2.write("\n")
            f.seek(0, 0)
            f2.write(f.read())
    os.remove(original)
    os.rename("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt", original)



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
    
        message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_log.txt"
        message_w_id = "--- " + message
        add_first_line(message_log, message_w_id)
    

        waitlist = "/home/ubuntu/textcare/framework/staticfiles/message_logs/waitlist.txt"
        triage_path = "/home/ubuntu/textcare/framework/staticfiles/message_logs/triage_path.txt"
        triage_state = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_state.txt"

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
    '''es contact number to the chat session'''
    user_input = json.loads(request.body)

    make_str = str(user_input)
    filename = make_str[18:50]
    phone_num = make_str[-12:-2]
    token_v0 = make_str[65:]
    token = token_v0[:-22]

    recaptcha_url = " https://www.google.com/recaptcha/api/siteverify"
    param_dict = {
        'secret': f"{env('RECAPTCHA_SECRET')}",
        'response': token
    }
    recaptcha_resp = requests.get(url=recaptcha_url, params=param_dict)
    recaptcha_data = recaptcha_resp.json()

    key_values = []
    for key, value in recaptcha_data.items():
        key_values.append(key)
        key_values.append(value)
    key_values = str(key_values)
    # recaptcha_str = str(recaptcha_data)
    # recaptcha_dict = json.loads(recaptcha_str)
    

    message_log = "/home/ubuntu/textcare/framework/staticfiles/" + filename
    add_first_line(message_log, "~~~~~~~~~~~~~~~~~~~~")

    context = {
        'make_str': make_str,
        'filename': filename,
        'phone_num': phone_num,
        'token': token,
        # 'recaptcha_str': recaptcha_str,
        # 'key values': key_values,
        'success': recaptcha_data['success'],
        'challenge_ts': recaptcha_data['challenge_ts'],
        'request': request,
    }

    # Use the render() response instead to view the context dict in Developer Tools
    # return render(request, 'set_chat.html', context=context)
    return JsonResponse(recaptcha_data)



def open_chat(request):
    """Chat function for WhatsApp sending"""

    send_message_url = f"{env('SEND_MESSAGE_URL')}"
    end_session_url = f"{env('END_SESSION_URL')}"
    issues_url = f"{env('ISSUES_URL')}"

    context = {
        'send_message_url': send_message_url,
        'end_session_url': end_session_url,
        'issues_url': issues_url,
    }

    return render(request, 'open_chat.html', context=context)





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

    ## TODO ##
    # Limit messages to only number in waitlist.txt?
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



def end_session(request):
    ''' Removes phone number from waitlist.txt to reset TextCare'''
    user_input = json.loads(request.body)

    make_str = str(user_input)
    # filename = make_str[18:50]
    phone_num = make_str[-12:-2]

    # Removes the phone number from the waitlist, which allows
    # the triage session to restart.
    waitlist = "/home/ubuntu/textcare/framework/staticfiles/message_logs/waitlist.txt"
    # add_first_line(message_log, "~~~~~~~~~~~~~~~~~~~~")
    match_list = []
    with open(waitlist, 'r+') as f:
        with open("/home/ubuntu/textcare/framework/staticfiles/message_logs/new2.txt",'a') as f2:

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
    os.rename("/home/ubuntu/textcare/framework/staticfiles/message_logs/new2.txt", waitlist)

    # Resets the triage state.
    triage_state = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + phone_num + "_state.txt"
    with open(triage_state, 'w+') as g:
            g.write('')

    # Resets transcript with TriageGPT.
    transcript = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + phone_num + "_transcript.txt"
    with open(transcript, 'w+') as t:
            t.write('')

    context = {
        'match_list': match_list,
        'num_list': num_list,
        'phone_num': phone_num,
        'user_input': user_input,
    }

    return render(request, 'end_session.html', context=context)


    # with open(original,'a+') as f:
    #     with open("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt",'a') as f2:
    #         f2.write(string)
    #         f2.write("\n")
    #         f.seek(0, 0)
    #         f2.write(f.read())
    # os.remove(original)
    # os.rename("/home/ubuntu/textcare/framework/staticfiles/message_logs/new.txt", original)



# def gpt_triage(number, message, waitlist, triage_path, triage_state):
#     with open(waitlist,'r') as f:
#         for line in f:
#             if line == number:
#                 chat_text = ''
#                 print(chat_text)
#                 return chat_text    



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



@csrf_exempt
def reply(request):
    # Loop the GPT three times
        # Need a state.txt of the loop
    # Then send to chat
    # Post copy of the GPT triage to the bottom of the chat page
    whatsapp_number = request.POST.get('From').split("whatsapp:")[-1]
    print(f"Sending the ChatGPT response to this number: {whatsapp_number}")
    number = whatsapp_number[2:]
    triage_state = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_state.txt"
    print("triage state file: " + triage_state)
    transcript = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_transcript.txt"
    try:
        # Extract the message from the incoming webhook request.
        body = request.POST.get('Body', '')

        # Adds previous parts of the conversation to the query.
        with open(transcript, 'a+', encoding='utf-8') as t:
            print("successful open")
            t.seek(0, 0)
            tscript_list = t.readlines()
            # if tscript_text.strip() != '':
            # tscript_text += '\n'
            print(tscript_list)
            tscript_text = ''
            for line in tscript_list:
                tscript_text += line
            print(tscript_text)

        body_w_tscript = tscript_text + "Patient: " + body
        messages = [{"role": "user", "content": body_w_tscript}]        

        # Log of messages for the incoming phone number.
        message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_log.txt"
        message_w_id = "--- " + body
        # Adds message to message log for this phone number.
        add_first_line(message_log, message_w_id)

        # Checks waitlist and if found, bypasses GPT for the live chat.
        waitlist = "/home/ubuntu/textcare/framework/staticfiles/message_logs/waitlist.txt"
        with open(waitlist,'r') as f:
            for line in f:
                # .strip() removes \n for match purposes.
                if line.strip() == number:
                    print("Matching line: " + line)
                    chat_text = 'Bypass to the chat function!'
                    print(chat_text)
                    return chat_text
            print("No matches in waitlist.")

        messages.append({"role": "system", "content": "You are a Triage Nurse. The incoming message is a conversation between a Patient and a Triage Nurse who is asking questions to determine the kind of health care the Patient needs. Ask two medical triage questions as the Triage Nurse to continue the conversation and get a better understanding of the situation."})

        # messages.append({"role": "system", "content": "You are a triage nurse. A patient is telling you their symptoms. Give a recommendation for the kind of specialist doctor that should been seen by the patient."})

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5
            )

        # The generated text
        chatgpt_response = response.choices[0].message.content

        print("just after chatgpt response")
        print(chatgpt_response)

        # transcript = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_transcript.txt"
        with open(transcript, 'a+', encoding='utf-8') as t:
            t.write("Patient: " + body + "\n")
            t.write(chatgpt_response + "\n")

        # Checks if triage state for this phone number exists.
        if os.path.exists(triage_state):
            print("exists!")
            with open(triage_state, 'r+') as g:
                # Reads current state.
                print("triage state opened")
                g.seek(0, 0)
                state_str = g.readline().strip()
                if state_str == '':
                    state_str = '0'
                print("state_str: " + state_str)
                state = int(state_str)
                print("state: #" + state_str + "#")
                if state == 0:
                    welcome = "Welcome to TextCare! \n\n" + chatgpt_response
                    chatgpt_response = welcome
                # Adds TriageGPTs output to the chat history.
                if state <= 2:
                    triage_msg = "+++ " + chatgpt_response
                    add_first_line(message_log, triage_msg)
                # If state is greater than 2, adds number to waitlist.
                if state > 2:
                    print("greater than")
                    with open(waitlist, 'a') as i:
                        i.write(str(number))
                        link = f"{env('CHAT_LINK')}"
                        print(link)
                        link_info = "We'll get you to a doctor now. Please click on the link to proceed: " + link
                        chatgpt_response += "\n\n" + link_info
                    last_message = [{"role": "user", "content": body_w_tscript}]
                    last_response = chat_switch(last_message) + "\n\n" + link_info
                    send_message2(whatsapp_number, last_response)
                    return HttpResponse('')
                # If state is less than 2, increments state.
                else:      
                    g.seek(0, 0)
                    state += 1
                    g.write(str(state))
        else:
            print("not exists!")
            # Creates the state file if none. Sets state to 0.
            with open(triage_state, 'w+') as g:
                g.seek(0, 0)
                g.write(str(0))
            # Adds TriageGPT response to the chat log.
            triage_msg = "+++ " + chatgpt_response
            add_first_line(message_log, triage_msg)

        send_message2(whatsapp_number, chatgpt_response)

        return HttpResponse('')

        
        # Store the conversation in the database
        # try:
        #     with transaction.atomic():
        #             conversation = Conversation.objects.create(
        #                 sender=whatsapp_number,
        #                 message=body,
        #                 response=chatgpt_response
        #             )
        #             conversation.save()
        #             logger.info(f"Conversation #{conversation.id} stored in database")
        # except Exception as e:
        #     logger.error(f"Error storing conversation in database: {e}")
        #     return HttpResponse(status=500)

    except:
        with open(triage_state, 'w+') as g:
            g.write('')
        with open(transcript, 'w+') as t:
            t.write('')

        response = MessagingResponse()
        response.message('TriageGPT error. Please try again.')
        return HttpResponse(str(response))