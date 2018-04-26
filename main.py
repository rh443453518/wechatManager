#coding:utf8
import itchat
from itchat.content import *
from ocr import *
from db import *

itchat.auto_login()
print "Initializing..."
'''
CONFIGURATION
'''
TARGET_LIST = ["Maskerism", "Liuyang", "Jokee"] # just for spam use
INIT_SCORE = 1 # initial score for user

#CHATROOM_NAME = 'shuati'
#CHATROOM_NAME_CH = u"刷题"
CHATROOM_NAME = 'ceshi'
CHATROOM_NAME_CH = u"测试"

DB_NAME = "wechatDB"
'''
SET UP
'''
#wechat
FRIENDS = itchat.get_friends(update=True)[1:]
FRIEND_NAME_TO_KEY = {friend.PYQuanPin: friend.UserName for friend in FRIENDS}
FRIEND_KEY_TO_NAME = {c:i for i,c in FRIEND_NAME_TO_KEY.items()}

CHATROOMS = itchat.get_chatrooms()
chatroom = itchat.search_chatrooms(CHATROOM_NAME_CH)[0]
CHATROOM_KEY = chatroom.UserName
chatroom = itchat.update_chatroom(CHATROOM_KEY, detailedMember = True)
MEMBERS = chatroom['MemberList']
MEMBER_KEY_TO_NAME = {m['UserName']: m['PYQuanPin'] for m in MEMBERS}
MEMBER_SCORE = {m['PYQuanPin']: INIT_SCORE for m in MEMBERS}

#running
scoreDB = ScoreDB(DB_NAME)
scoreDB.checkOut(FRIEND_NAME_TO_KEY.keys())

'''
running
'''
def send_friend(message, name):
	target = [friendName for friendName in FRIEND_NAME_TO_KEY.keys() if name in friendName]
	if len(target) > 1:
		print "ambiguous friend name "
		return
	elif len(target) == 0:
		print "name not found in friends"
		return
	itchat.send(message, FRIEND_NAME_TO_KEY[target[0]])
	print "message:",message, "sent to ", name

def send_chatroom(message, room_id):
	itchat.send(message, room_id)
	print "message:",message, "sent to ", room_id

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
	try:
		senderName = FRIEND_KEY_TO_NAME[msg.FromUserName]
	except:
		return
	#info = "%s:%s"%(msg["Type"], msg["Text"])
	#itchat.send(info, msg.FromUserName)

@itchat.msg_register([PICTURE], isGroupChat = True)
def download_files(msg):
	chatroomName = msg.User.PYQuanPin
	if chatroomName != CHATROOM_NAME:
		return
	senderKey = msg["FromUserName"]
	senderName = MEMBER_KEY_TO_NAME[senderKey]
	if senderKey[:2] == "@@":
		print "strange user name"
	print "a picture from %s @ %s"%(senderName, CHATROOM_NAME)
	savePath = "cache/"+senderName+".jpg"
	msg["Text"](savePath)
	# check uploaded image contains today's problem
	s = get_problem_title(savePath)
	print "ocr result: ", s
	target_title = "merge intervals"
	distance = get_edit_distance(s, target_title)
	if distance < 5:
		send_chatroom(u"打卡成功", CHATROOM_KEY)
	MEMBER_SCORE[senderName] += 1
	scoreDB.addPoint(senderName, 1)
#时间响应，定时对scoreDB 进行udpate

def dailyUpdate():
	raise NotImplementedError

#从群里删人
def deleteFromChatroom():
	raise NotImplementedError

#将新加入群的人添加到db
def onAddMember():
	raise NotImplementedError
itchat.run()
