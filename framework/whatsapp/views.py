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



'''
check patient log, send to chat if there's a match
open triage path, 
'''

patient_log = 'patient_log.txt'

# message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + filename_user + "_log.txt"
# triage_state = filename_user + "_state.txt"

def triage(number, message, waitlist, triage_path, triage_state): 
    ### test ###
    num = "###" + number + "###"
    words = "###" + message + "###"
    message = message.lower()

    with open(waitlist,'r') as f:
        for line in f:
            if line == number:
                chat_text = ''
                print(chat_text)
                return chat_text

    conditions_list = []
    ### test ###
    exist = "?"
    if os.path.exists(triage_state):
        ### test ###
        exist = "exists"
        with open(triage_state, 'r+') as g:
            with open(triage_path, 'r') as h:
                path_list = h.readlines()
                for line in path_list:
                    line_list = line[:-1].split(",")
                    line_list[1] = int(line_list[1])
                    line_list[2] = int(line_list[2])
                    conditions_list.append(line_list)
                print(conditions_list)
            g.seek(0, 0)
            state = g.readline()
            print('state: ' + state)
            new_index = 0
            if state == '':
                question = conditions_list[0][0]
                g.seek(0, 0)
                g.write(str(0))
            else:
                index = int(state)
                if message == 'y':
                    new_index = conditions_list[index][1]
                    print("new_index: " + str(new_index))
                else:
                    new_index = conditions_list[index][2]
                    print("new_index: " + str(new_index))
                question = conditions_list[new_index][0]
                g.seek(0, 0)
                g.write(str(new_index))
            if new_index == 15:
                g.seek(0, 0)
                g.write(str(0))
                link = "example.com/whatsapp/chat"
                # link = f"{env('CHAT_LINK')}"
                question += " Please click on the link to proceed: " + link
                # Adds number to doctor's waitlist.
                with open(waitlist, 'a') as i:
                    i.write(str(number))
    else:
        exist = "not_exists"
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
    # question = num + words + exist
    print(question)
    return question



@csrf_exempt
def message(request):
    user = request.POST.get('From')
    message = request.POST.get('Body')
    print(f'{user} says {message}')

    # with open("/home/ubuntu/textcare/framework/staticfiles/new.txt", "w") as file:
    #     file.write("Your text goes here")
    #     file.close()
    number = user[11:]
    try:

        message_log = "/home/ubuntu/textcare/framework/staticfiles/message_logs/T" + number + "_log.txt"
        # message_log = "/home/ubuntu/textcare/framework/staticfiles/messages.txt"
        # new_log = "/home/ubuntu/textcare/framework/staticfiles/new.txt"
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
            g.write('')

        response = MessagingResponse()
        response.message('Triage error. Please try again.')
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