# -*- coding: utf-8 -*-
import config
import telebot
import random
import threading


flag = 0
x = 0
y = 0
score = 0
# 0 - игра не началась
# 1 - игрок ждет вопрос
# 2 - мы ожидаем ответ
# 3 - пауза
# 10 - начать ли заново?
# 11 - ожидать ответа
# 12 - начать заново

TimeOut = False
waitingThread = threading.Thread(target=None)
bot = telebot.TeleBot(config.token)

def SignalTimeIsOut():
	global TimeOut
	TimeOut = True

def WaitForTimeOut(id):
	global TimeOut
	while True:
		if TimeOut == True:
			TimeIsOut(id)

def TimeIsOut(id):
	global thread1
	thread1.join()
	TimeOut = False
	bot.send_message(id, "Время вышло!")
	bot.send_message(id, "Новая задачя:")
	push(id)

def getText(message):
	checkPlayersAnswer(message)

def push(id):
	global x, y, flag, thread1
	x = random.randint(0, 100)
	y = random.randint(0, 100)
	keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	button1 = telebot.types.KeyboardButton(str(x + y))
	r = random.randint(0,200)
	while r == x + y:
		r = random.randint(0,200)
	button2 = telebot.types.KeyboardButton(str(r))

	if random.randint(0,2) == 0:
		keyboard.add(button1)
		keyboard.add(button2)
	else:
		keyboard.add(button2)
		keyboard.add(button1)
	ms = bot.send_message(id, str(x) + " + " + str(y), reply_markup=keyboard)
	bot.register_next_step_handler(ms, getText)
	flag = 2

	thread1 = threading.Timer(4.0, SignalTimeIsOut)
	thread1.start()

'''def deleteScore(id):
	fname = "/Users/mikhail/Documents/Programming/Python/Bots/HenryBot/bot2/scores_" + str(id) + "_.txt"
	def file_len(fname):
		with open(fname) as f:
			for i, l in enumerate(f):
				pass
		return i + 1
	if file_len(fname) > 50:
		file = open(fname, "r")
		min = int(file[0])
		minIndex = 0'''

def saveScore(id):
	global score
	file = open("/Users/mikhail/Documents/Programming/Python/Bots/HenryBot/bot2/data/scores_" + str(id) + "_.txt", "a")
	file.write(str(score) + "\n")
	file.close()

def getHighScores(id):
	file = open("/Users/mikhail/Documents/Programming/Python/Bots/HenryBot/bot2/data/scores_" + str(id) + "_.txt", "r")
	scores = file.readlines()
	file.close()
	n = 0
	for i in scores:
		scores[n] = int(i)
		n += 1
	scores.sort(reverse=True)
	bot.send_message(id, "Рекорды:")
	for n in range(5):
		try:
			bot.send_message(id, str(scores[n]))
		except:
			break

def initiateGame(message):
	global flag
	global score
	score = 0
	bot.send_message(message.chat.id, "Игра началась :)")
	flag = 1
	bot.send_message(message.chat.id, "Счёт: " + str(score))
	waitingThread.start()
	push(message.chat.id)
	return

def checkPlayersAnswer(message):
	global flag
	global score
	global thread1
	try:
		if int(message.text) == x+y:
			bot.send_message(message.chat.id, "Молодец!")
			flag = 1
			score += 1
			bot.send_message(message.chat.id, "Счёт: " + str(score))
			thread1.join()
			push(message.chat.id)
		else:
			bot.send_message(message.chat.id, "Ты проиграл!!!")
			#deleteScore(message.chat.id)
			saveScore(message.chat.id)
			score = 0
			flag = 0
	except:
		bot.send_message(message.chat.id, "Ты проиграл!!!")
		#deleteScore(message.chat.id)
		saveScore(message.chat.id)
		score = 0
		flag = 0

@bot.message_handler(commands=["start", "stop", "pause", "resume", "get_my_scores"])
def react_to_commands(message):
	global flag
	global waitingThread
	if message.text == "/start":
		if flag == 0:
			waitingThread = threading.Thread(target=WaitForTimeOut, args=(message.chat.id,))
			initiateGame(message)
		else:
			flag = 10
			react_to_text(message)
	elif message.text == "/stop":
		flag = 0
		waitingThread.join()
		saveScore(message.chat.id)
		score = 0
	elif message.text == "/pause":
		flag = 3
	elif message.text == "/resume":
		flag = 1
		push(message.chat.id)
	elif message.text == "/get_my_scores":
		getHighScores(message.chat.id)
		#flag = 20
		#react_to_text(message)
	else:
		bot.send_message(message.chat.id, "Неверная команда")

@bot.message_handler(content_types=["text"])
def react_to_text(message):
	global flag
	#bot.send_message(message.chat.id, "Игра началась :)")
	if flag == 2:
		checkPlayersAnswer(message)
	elif flag == 10:
		bot.send_message(message.chat.id, "Вы действительно хотите начать заново? (Y/N)")
		flag = 11
	elif flag == 11:
		if message.text.lower() == 'y':
			saveScore(message.chat.id)
			flag = 1
			initiateGame(message)
		elif message.text.lower() == 'n':
			flag = 2
		else:
			bot.send_message(message.chat.id, 'Введите Y чтобы ответить "да" или введите N чтобы ответить "нет".')
	#elif flag == 20:
	#	bot.send_message(message.chat.id, "Сколько ")

if __name__ == '__main__':
    bot.polling(none_stop=True)
