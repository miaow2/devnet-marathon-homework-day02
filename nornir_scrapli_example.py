import getpass 
import os
import re
import scrapli
import sys

from nornir import InitNornir
from nornir.core import exceptions
from nornir.core.filter import F
from nornir_scrapli.tasks import send_command


def reset_connection(host):
    try:
        host.close_connections()
    except ValueError:
        pass


def check_mac(mac):
    if re.search(r'[a-f0-9]{4}\.[a-f0-9]{4}\.[a-f0-9]{4}', mac):
        return True


def find_mac(task, mac, show_mac_raw):
    is_found = False
    # парсим вывод при помощи Genie
    show_mac = show_mac_raw.scrapli_response.genie_parse_output()
    # проходимся по структурированным данным и проверяем, что искомый МАС находится за access портом
    for vlan in show_mac['mac_table']['vlans']:
        if mac in show_mac['mac_table']['vlans'][vlan]['mac_addresses'].keys():
            interface = list(show_mac['mac_table']['vlans'][vlan]['mac_addresses'][mac]['interfaces'].keys())[0]
            try:
                show_int_raw = task.run(task=send_command, command=f'show interfaces {interface} switchport')
                show_int = show_int_raw.scrapli_response.genie_parse_output()
            except exceptions.NornirSubTaskError:
                break
            if show_int:
                if 'access' in show_int[interface]['switchport_mode'].lower():
                    is_found = True
                    print(f"MAC address {mac} was found on interface {interface} on switch {task.host}")
    task.host['is_found'] = is_found


def check_auth(task, mac):
    try:
        # запрашиваем МАС таблицу и заодно проверяет аутенфикацию
        show_mac_raw = task.run(task=send_command, command='show mac address-table')
        task.run(task=find_mac, mac=mac, show_mac_raw=show_mac_raw)
    except exceptions.NornirSubTaskError as e:
        if isinstance(e.result.exception, scrapli.exceptions.ScrapliAuthenticationFailed):
            print('*' * 70)
            print(f'Authentication failed to host {task.host}')
            print('*' * 70)
            reset_connection(task.host)


def main(mac):
    # определяем путь до скрипта для упрощения навигации
    script_path = os.path.split(os.path.realpath(__file__))[0]
    # иницилизируем норнир
    with InitNornir(config_file=f"{script_path}/config.yaml") as nr:
        username = input("Username: ")
        password = getpass.getpass(prompt='Password: ') 
        nr.inventory.defaults.username = username
        nr.inventory.defaults.password = password
        switches = nr.filter(F(name__contains="SW"))
        switches.run(task=check_auth, mac=mac)
        # если МАС не был найден, то выводится об этом сообщение
        is_found = False
        for host in switches.inventory.dict()['hosts']:
            if switches.inventory.dict()['hosts'][host]['data']['is_found']:
                is_found = True
        if not is_found:
            print(f"MAC address {mac} not found")


if __name__ == '__main__':
    # проверяем формат МАС на правильность
    attempts = 4
    while attempts != 0:
        mac = input("Enter MAC address in format hhhh.hhhh.hhhh: ")
        mac = mac.lower()
        if check_mac(mac):
            break
        else:
            attempts -= 1
            if attempts == 0:
                print('You spent all attempts')
                sys.exit(1)
            print(f'Entered wrong MAC address, you have {attempts} attempts left')
    main(mac)