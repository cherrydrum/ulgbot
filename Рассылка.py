# -*- coding: utf-8 -*-
# ULGBOT. Очень старался, но вышло как всегда :D
import requests
import json
import ast
import docx
import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#Глобальные словари, нужные для оформления вывода.
emoji_dic = {u'А':u'🎵', u'Б':u'💡', u'В':u'🌿', u'Т': '💾'}
months = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря'] 
classes = [u'8А', u'8Б', u'8В', u'8Т', u'9А', u'9Б', u'9В', u'9Т', u'10А', u'10Б', u'10В', u'10Т', u'11А', u'11Б', u'11В', u'11Т']

#Читаем конфиг.
try:
	config = open('settings.conf', 'r').read()
	config = {a.split('=')[0]: a.split(' = ')[1] for a in config.split('\n') if a != ''} 
except:
	print('[!!!] Не удалось загрузить файл конфигурации!')
	exit()

post_token = config['user']
token = config['community']
version = config['version']
word_file_path = config['word_file_path']

print u'ulg_bot v{} \n'.format(version)
print 'Загрузка базы...'

#Читаем базу.
try:
	file = open('userbase','r')
	ids = file.read()
	ids = ast.literal_eval(ids)
except:
	print('[!!!] Не удалось загрузить базу!')
	exit()

def vk(method, params, token, ver):
	r = requests.get(u'https://api.vk.com/method/{}?{}&v={}&lang=0&access_token={}'.format(method, params, ver, token))
	out = r.text 
	json_out = json.loads(out)
	json_out = (json_out.get('response'))
	return json_out
def get_doc(path):
	try:
		print u'\n[*] Открываю документ с расписанием...'
		document = docx.Document(path)
		basedic = {}
		print u'[*] Обрабатываю таблицу...'
		for k in range(2):
			table = document.tables[k]
			a = table.columns
			for i, row in enumerate(a):
				key = a[i].cells[0].text
				lessons = [] 
				for j in range(5):
					lesson = {}
					b = a[i].cells[j+1].text
					if len(b.split('\n')) == 2:
						lesson['sbj'] = b.split('\n')[1]
						lesson['order'] = a[0].cells[j+1].text
						lesson['cab'] = b.split('\n')[0]
					else:
						lesson['sbj'] = b
						lesson['order'] = a[0].cells[j+1].text
					lesson.setdefault('cab', '-/-')
					lessons.append(lesson)
				basedic[key] = lessons

			basedic.pop('')
		print u'[*] Готово!\n'
		return(basedic)
	except:
		print('[!!!] Упс, ошибка во время работы с файлом расписания!')
		exit()
def genertatemessage(curclass, dic): #Получить пары 1 из классов
	print u'[*] Генерирую и отправляю расписание для {}'.format(curclass)

	emoji = ''
	for key, value in emoji_dic.items():
		if curclass.find(key) != -1:
			emoji = emoji_dic.get(key)
	if type(emoji) == str:
		emoji = unicode(emoji, 'utf-8')

	now = datetime.datetime.now()
	date = u'{} {}'.format(now.day, months[now.month - 1])
	answer = u'🕒 [{}]\n{} {} класс\nФЕЙКОВОЕ'.format(date, emoji, curclass)
	lessons = dic.get(unicode(curclass))
	for lesson in lessons:
		if lesson.get('cab') == '-/-':
			answer = answer + u'\n{order}: {sbj}'.format(**lesson)
		elif lesson.get('sbj') == '':
			answer = answer + u'\n{order}: ---'.format(**lesson)
		else:
			answer = answer + u'\n{order}: {sbj} (Каб. {cab})'.format(**lesson)
	return(answer)
def base_add(uid, bid, reply):
	bid = bid.encode('utf-8')
	base = ids.get(bid)
	if base.count(uid) == 0:
		print '[A] Добавляю {} в {}...'.format(uid, bid)
		base.append(uid)
		basedict = {bid:base}
		ids.update(basedict)
		send_one(uid, '⚡ Ваш ID был добавлен в базу расслыки {}.'.format(bid), reply)
	else:
		print '[D] Пользователь уже подписан на рассылку.'
		send_one(uid, '⛔ Вы уже подписаны на рассылку {}.'.format(bid), reply)
def base_remove(uid, bid, reply):
	bid = bid.encode('utf-8')
	base = ids.get(bid)
	if base.count(uid) >= 1:
		print '[A] Удаляю {} из {}...'.format(uid, bid)
		base.remove(uid)
		basedict = {bid:base}
		ids.update(basedict)
		send_one(uid, '⚡ Ваш ID был удален из базы расслыки {}.'.format(bid), reply)
	else:
		print '[D] Такого пользователя в базе нет.'
		send_one(uid, '⛔ Вы не были подписаны на расслыку {}.'.format(bid), reply)
def send(usergroup, message):
	userids = str(ids.get(usergroup))
	userids = userids.replace('[', '')
	userids = userids.replace(']', '')	
	userids = userids.replace(' ', '')
	if type(message) == str:
		message = unicode(message, 'utf-8')
	r = requests.get(u'https://api.vk.com/method/messages.send?user_ids={}&message={}&v=3.0&lang=0&access_token={}'.format(userids, message, token))
def send_one(uid, message, reply):
	if type(message) == str:
		message = unicode(message, 'utf-8')
	r = requests.get(u'https://api.vk.com/method/messages.send?user_id={}&message={}&forward_messages={}&v=3.0&lang=0&access_token={}'.format(uid, message, reply, token))
def get_new_users():
	print '\n[*] Проверяю новые сообщения...' 
	jso = vk('messages.getConversations', 'filter=unread&count=200', token, '3.0')
	for i in range(len(jso) - 2):
		cur = str(i + 1)
		usr_req = jso.get(cur) #Ввод переменных чтоб не тягать элементы словаря.
		usr_req = usr_req.get('last_message')
		usr_reqid = usr_req.get('from_id')
		buf = vk('messages.getHistory', 'user_id={}'.format(usr_reqid), token, '3.0')
		buf.pop(0)
		buf.reverse()
		for k in range(len(buf)):
			dic = buf[k]
			read = str(dic.get('read_state'))
			if read == '0' and dic.get('from_id') == usr_reqid:
				print u'[*] Запрос от {}: {}'.format(usr_reqid, dic.get('body'))
				agregate_message((dic.get('body')).upper(), usr_reqid, dic.get('mid'))

	print '[*] Проверка завершена.'	
def agregate_message(message, uid, reply):
	message = message.upper()
	try: 
		if message == u'РАСПРЕДЕЛЕНИЕ':
			send_one(uid, ids, reply) #Нужно для выгрузки существующей базы адресантов, для последующего использования в других проектах.
		else:
			base_id = message.split(' ')[1]
			if message.split(' ')[0] == u'ПОДПИШИ': 
				base_add(uid, base_id, reply)
			elif message.split(' ')[0] == u'ОТПИШИ':
				base_remove(uid, base_id, reply)
			else:
				send_one(uid, u'😰 Извините, запрос не распознан. \nПожалуйста, повторите попытку.', reply)
				print '[!] Ошибка от {}, команда не распознана.'.format(uid)		

	except IndexError:
			send_one(uid, u'😰 Извините, запрос не распознан. \nПожалуйста, повторите попытку.', reply)
			print '[!] Ошибка от {}, IndexError.'.format(uid)





get_new_users() #Обработка новых запросов.

print '\n[A] Запись изменений в базу...'
file = open('userbase','w')
file.write(str(ids))
file.close()

print u'Прежде чем мы начнем...\nВы хотите отправить что-то важное каждому подписчику?\nЭто может быть объявление или важное напоминание.\nОставьте пустым, чтобы продолжить.'
ans = raw_input('Ответ: ').decode('utf-8')
a = get_doc(word_file_path) #Получаю данные из таблицы Word

print u'[РАССЫЛКА]'
for key, value in ids.items(): #Отправка каждому получателю.
	i = key.decode('utf-8')
	send(key, (genertatemessage(i, a)))
	if ans != '':
		send(key, (u'📕 Внимание, {}'.format(ans)))


#Кусок кода, ответственный за постинг.
#Сначала получим саму картинку.
a = get_doc(word_file_path)
'[*] Генерирую картинку...'
img = Image.open("in.jpg")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("font.ttf", 14)

now = datetime.datetime.now()
date = u'{} {}'.format(now.day, months[now.month - 1])
draw.text((40, 30),u'Расписание уроков на {}.'.format(date),(41,41,41),font=ImageFont.truetype("header.ttf", 45))

x = 40 #Настройки разметки, куча костылей, да-да.
y = 95
sample = 95
counter = 0
for c in classes:
	draw.text((x, y),c ,(41,41,41),font=ImageFont.truetype("header.ttf", 25))
	y += 40
	for i in a.get(c):
		if i.get('order') == u'СК':
			draw.text((x, y),u'СК: {sbj}'.format(**i),(41,41,41),font=ImageFont.truetype("font.ttf", 11))
		elif i.get('order') == u'0':
			draw.text((x, y),u'0: {sbj}'.format(**i),(41,41,41),font=ImageFont.truetype("font.ttf", 11)) 
		else:
			if len(i.get('sbj')) > 14:
				draw.text((x, y),u'{sbj}'.format(**i),(41,41,41),font=ImageFont.truetype("font.ttf", 8))
			else:
				draw.text((x, y),u'{sbj}'.format(**i),(41,41,41),font=font)
			y += 15
			draw.text((x, y),u'Каб. {cab}'.format(**i),(41,41,41),font=ImageFont.truetype("font.ttf", 10))
		y += 20
	x += 120
	counter += 1
	if counter == 8:
		sample = 300
		x = 40
	y = sample
print '[*] Сохраняю...'
img.save('out.jpg')

#Теперь отправляем.
print '[*] Отправляю...'
p_img = open('out.jpg', 'rb')
try:
	#Абсолютное мракобесие. Без ста грамм не разбираться.
	url = vk('photos.getWallUploadServer', '174539192', post_token, '3.0') 
	url = url.get('upload_url')
	img_post = requests.post(url, files={'file1': p_img})
	img_post = json.loads(img_post.text)
	photo_json = img_post.get('photo')
	img_save = requests.get('https://api.vk.com/method/photos.saveWallPhoto?photo={}&server={}&hash={}&v=5.92&lang=0&access_token={}'.format(photo_json, int(img_post.get('server')), img_post.get('hash'), post_token))
	img_save = json.loads(img_save.text).get('response')[0]
	link = 'photo{}_{}'.format(img_save.get('owner_id'), img_save.get('id'))
	img_post = requests.get('https://api.vk.com/method/wall.post?owner_id=-174539192&from_group=1&attachments={}&v=5.92&lang=0&access_token={}'.format(link, post_token))
except:
	print('[!!!] Не удалось отправить расписание на стену! Пинайте Колю!') #Только несильно.
	exit()

