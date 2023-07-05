from pprint import pprint

import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from config.itop_cred import *


def get_active_tickets(f_name, l_name) -> list:
    with requests.session() as session:
        session.auth = HTTPBasicAuth(ITOP_LOGIN, ITOP_PASSWD)
        session.headers = ITOP_HEADER

        expression = f'SELECT UserRequest ' \
                     f'FROM UserRequest ' \
                     f'WHERE caller_id_friendlyname LIKE "{f_name} {l_name}" '

        r = session.get(
            url=f'{ITOP_URL}/webservices/export-v2.php?'
                f'format=xml&'
                f'login_mode=basic&'
                f'date_format=Y-m-d+H%3Ai%3As&'
                f'expression={expression}'
        )

    response = xmltodict.parse(r.text)

    try:
        user_requests = response['Set']['UserRequest']
        tickets = []

        for ticket in user_requests:

            tickets.append(f"Имя и Фамилия: {ticket.get('caller_id_friendlyname')} \n"
                           f"Номер тикета: {ticket.get('ref')} \n"
                           f"Статус: {ticket.get('status')} \n"
                           f"Описание: {ticket.get('description').replace('<p>', '').replace('</p>', '')} ")

    except TypeError:
        tickets = [
            'С сервиса не было получено ответа.\n'
            'Вероятно ваши имя и фамилия, указаные в телеграм, отличаются от имени и фамилии, указанные на сервисе\n\n'
            'Поменяйте имя и фамилию в телеграм и переавторизуйтесь в боте']

    return tickets


if __name__ == '__main__':
    # Запустить скрипт, чтобы проверить работоспособность
    t = get_active_tickets('Ефим', 'Дударев')
    pprint(t)
