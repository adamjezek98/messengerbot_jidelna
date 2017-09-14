import requests
import botconfig
import json
access_token = botconfig.access_token

def get_message_text_template(user_id, text):
    return {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": text
        }
    }
def get_message_button_template(user_id, text, buttons):
    a =  {
        "recipient": {
            "id": user_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": []
                }
            }
        }
    }
    for button in buttons:
        a["message"]["attachment"]["payload"]["buttons"].append({
                            "type": "postback",
                            "title": button[0],
                            "payload": button[1]
                        })
    return a

def send(body):
    params = {"access_token":access_token}
    headers = {"Content-Type": "application/json"}
    print("=====SENDING=======")
    print(body, params, headers)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=json.dumps(body))
    print("=====RESPONSE======")
    print(r.status_code)
    print(r.text)

def send_message(user_id, text):
    data = get_message_text_template(user_id,text)

    send(data)

