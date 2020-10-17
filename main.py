import bot_class
import json

if __name__ == '__main__':
    try:
        # Fetching user's info from config file
        with open('config.ini', 'r') as user_info:
            user_details = user_info.readlines()
            for info in user_details:
                if 'email' in info:
                    e_mail = info[6:]
                    e_mail = e_mail.rstrip('\n')
                elif 'password' in info:
                    password = info[9:]
                    password = password.rstrip('\n')
                    break
    except FileNotFoundError:
        print("Could not find config.ini!")
    cookies = {}
    try:
        # Load the session cookies
        with open('session.json', 'r') as f:
            cookies = json.load(f)
    except FileNotFoundError:
        # If it fails, never mind, we'll just login again
        pass

    client = bot_class.MessageBot(e_mail, password, session_cookies=cookies)
    # Save the session again
    with open('session.json', 'w') as f:
        json.dump(client.getSession(), f)
    client.listen()


