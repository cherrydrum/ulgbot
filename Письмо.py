# -*- coding: utf-8 -*-
import requests
import ast

#CONFIG
try:
	config = open('settings.conf', 'r').read()
	config = {a.split('=')[0]: a.split(' = ')[1] for a in config.split('\n') if a != ''} 
except:
	print('[!!!] Не удалось загрузить файл конфигурации!')
	exit()

version = config['version']
token = config['community']

ls = []

def send(usergroup, message):
	userids = str(ids.get(usergroup))
	userids = userids.replace('[', '')
	userids = userids.replace(']', '')	
	userids = userids.replace(' ', '')
	print('Рассылка для {}'.format(usergroup))
	if type(message) == str:
		message = unicode(message, 'utf-8')
	r = requests.get(u'https://api.vk.com/method/messages.send?user_ids={}&message={}&v=3.0&lang=0&access_token={}'.format(userids, message, token))

print u'ulg_bot v{} \n'.format(version)
print '[INI] Загрузка базы...'

file = open('userbase','r')
ids = file.read()
ids = ast.literal_eval(ids)
file.close()

msg_file = open('message','r')
msg = msg_file.read()
msg_file.close()

print u'[РАССЫЛКА]'
for key, value in ids.items(): #Отправка каждому получателю.
		send(key, msg)
		
