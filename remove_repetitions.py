import requests
config = dotenv_values(".env")

YOU_TRACK_TOKEN = config.get("YOU_TRACK_TOKEN")

main_url = config.get("main_url")
headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(YOU_TRACK_TOKEN),
        "Content-Type": "application/json"
    }
list_summary = requests.get(main_url, headers=headers).json()

no_repeat_list = []
repeat_list = []
for i in range(len(list_summary)):
    if list_summary[i]['summary'] not in no_repeat_list:
        no_repeat_list.append(list_summary[i]['summary'])
    else:
        repeat_list.append(list_summary[i]['id'])

for n, name in enumerate(repeat_list, start = 1):
    del_url = config.get("del_url")
    delete_url = f'{del_url}/api/issues/{name}'
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(YOU_TRACK_TOKEN),
        "Content-Type": "application/json"
    }
    requests.delete(delete_url, headers=headers)
    print(f'{n} / {len(repeat_list)}')
