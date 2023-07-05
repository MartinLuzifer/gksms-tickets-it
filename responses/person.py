import os
import json
import requests
import xmltodict
from requests.auth import HTTPBasicAuth


def get_username_list():

    with requests.session() as session:

        username_list = []
        f_name_list = []
        l_name_list = []

        session.auth = HTTPBasicAuth('admin', '12gfWUIR#$')
        response = session.get(
            url='http://172.16.13.5:4443/webservices/export-v2.php?'
                'format=xml&'
                'login_mode=basic&'
                'date_format=Y-m-d+H%3Ai%3As&'
                'expression=SELECT%20Person'
                '',
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/113.0.0.0 Safari/537.36'
            }
        )

        with open('person.xml', 'w') as file:
            file.write(response.text)

        with open("person.xml") as xml_file:
            data_dict = xmltodict.parse(xml_file.read())

        with open("person.json", "w") as json_file:
            json_file.write(json.dumps(data_dict))

        with open('person.json') as person:
            person = json.load(person)
            for person_list in person['Set']['Person']:
                username_list.append(
                    f"{person_list['first_name']} "
                    f"{person_list['name']}"
                )
                f_name_list.append(
                    f"{person_list['first_name']}"
                )
                l_name_list.append(
                    f"{person_list['name']}"
                )
    if os.name == 'posix':
        os.system('rm ./person.xml')
        os.system('rm ./person.json')
    return username_list, f_name_list, l_name_list
