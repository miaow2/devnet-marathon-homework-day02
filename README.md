# Домашная работа второй день DevNet Marathon

[Ссылка](https://cisco.app.box.com/s/wxml1yyels5abzdvk7hhqmw6v4dzc5vd) на домашнее задание

Связка [Nornir](https://github.com/nornir-automation/nornir) + [Scrapli](https://github.com/carlmontanari/nornir_scrapli) ([SSH2-Python](https://github.com/ParallelSSH/ssh2-python)) + [Genie](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/)

В `inventory/devices.yaml` находятся предпологаемые IP адреса девайсов из схемы из ДЗ

Запускается файлом `nornir_scrapli_example.py`

Скрипт спрашивает МАС (проверяется на соответствие вида hhhh.hhhh.hhhh), логин, пароль.
