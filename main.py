from api import *
from time_work import *
from database import *
from config import *

# pip 3
import datetime
import random
import json as Json
import multitasking
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


# access_token I call user_token

class answers:
    def __init__(self):
        pass

    def set_user_token(self):
        return f'For use {project_name} you must make your own account token\n' \
               '1. Go to link: https://oauth.vk.com/oauth/authorize?client_id=8035251&scope=photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,email,notifications,stats,ads,offline,docs,pages,stats,notifications&response_type=token&__q_hash=69940e59922728d45b3bca4d29ab1dc9\n' \
               '2. Copy and send address bar content'

    def token_has_been_saved(self):
        return 'Token saved successfully\nNow send please your group_id\n\n1. Go to your group\n' \
               '2. Manage -> Main Inf -> Community id\n' \
               f'Send only numbers, like {random.randrange(100000000, 999999999)}'

    def group_id_has_been_saved(self):
        return 'Group_id and user token saved\nSend your schedule or if you wont to use standard send point - .\n' \
               'Schedule format, for example [[hour, minute], [time second post], ...]'

    def error(self):
        return f'Your token-url or group id is wrong\nplease try again'

    def schudle_saved(self):
        return 'All information is collected\nNow if you send images to bot, they are put in postponed posts'

    def schedule_error(self):
        return 'Wrong schedule has wrong format\nYou can use standard schedule'

    def schedule_send(self, schedule: str):
        # [[2, 30], [7, 40], [10, 0], [14, 0], [17, 22], [20, 15]]
        time = [f"""{i[0]}: {i[1]}""" for i in schedule]
        result = ''
        for i in range(len(time)):
            result += f'Post number {i + 1} will be published at {time[i]}\n'
        return result


class user_vk:
    def __init__(self, event, type):
        self.event = event
        self.type = type
        self.user_token = False

        if type is VkBotEventType.MESSAGE_NEW:
            self.event_object = event.object
            self.event_message = event.object['message']
            self.event_message_date = event.object['message']['date']
            self.event_message_from_id = event.object['message']['from_id']
            self.event_message_attachments = event.object['message']['attachments']
            self.event_message_text = event.object['message']['text']
            # self.event_message_ = event.object['message']['']

    def set_json(self, json):
        self.user_id = json['user_id']
        self.user_token = json['user_token']
        self.group_id = json['group_id']
        self.schedule = json['schedule']


@multitasking.task
def multi_task_vk():
    global get_info_vk
    flags = {}
    # dict format is like
    # {user_id: [{flag_name: 'name of flag', other variable...}, other flags...], other users...}

    print(f'vk bot work {datetime.datetime.now()}')
    vk = bot_vk(
        bot_token=bot_token,
        bot_group_id=bot_group_id
    )

    for event in vk.bot_longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            # -
            # -
            user = user_vk(event, event.type)
            user_token = vk_user_inf(user_id=user.event_message_from_id)

            answer = answers()
            data = Time()
            if user.event_message_from_id in flags or not user_token:
                # if we have some flag or don't have json file
                if f"{user.event_message_from_id}" in flags.keys():
                    for flag in flags[f'{user.event_message_from_id}']:
                        # here process user flags
                        if flag['flag_name'] == 'user_token' and not flag['user_token']:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['user_token'] = user.event_message_text
                            vk.send_message(user.event_message_from_id, answer.token_has_been_saved())

                        elif flag['flag_name'] == 'user_token' and not flag['group_id']:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['group_id'] = user.event_message_text
                            check = user_token_and_group_id_test(flag['user_token'], user.event_message_text)
                            if check:
                                vk.send_message(user.event_message_from_id, answer.group_id_has_been_saved())

                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        flags[f'{user.event_message_from_id}'][i][
                                            'user_token'] = check['user_token']
                            else:
                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        none_flag = {'flag_name': 'user_token', 'user_token': False,
                                                     'group_id': False, 'schedule': False}
                                        flags[f'{user.event_message_from_id}'][i] = none_flag
                                vk.send_message(user.event_message_from_id, answer.error())

                        elif flag['flag_name'] == 'user_token' and flag['schedule'] == False:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['schedule'] = user.event_message_text
                                    us, gr = flags[f'{user.event_message_from_id}'][i]['user_token'],\
                                             flags[f'{user.event_message_from_id}'][i]['group_id']

                            check = schedule_test(user.event_message_text)
                            if check:
                                json = {"user_id": user.event_message_from_id,
                                        "user_token": us,
                                        "group_id": gr,
                                        'schedule': check}
                                vk_save_user_token(user.event_message_from_id, json)
                                vk.send_message(user.event_message_from_id, answer.schudle_saved())
                                vk.send_message(user.event_message_from_id, answer.schedule_send(check))
                            else:
                                # if info user is wrong
                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        none_flag = {'flag_name': 'user_token', 'user_token': False,
                                                     'group_id': False, 'schedule': False}
                                        flags[f'{user.event_message_from_id}'][i] = none_flag
                                vk.send_message(user.event_message_from_id, answer.schedule_error())
                elif not user_token:
                    # if don't have token and you don't have flag
                    vk.send_message(user_id=user.event_message_from_id, message=f"{answer.set_user_token()}")
                    none_flag = {'flag_name': 'user_token', 'user_token': False, 'group_id': False, 'schedule': False}
                    flags[f'{user.event_message_from_id}'] = [none_flag]
            else:
                # if token file exist

                user_json = vk_user_inf(user.event_message_from_id)
                """Here write checker for json file"""
                user.set_json(user_json)
                vk_request = vk_requests(user.user_token)

                # check photo in message
                if user.event_message_attachments:
                    # here process photo(s) in message
                    photos = [i for i in user.event_message_attachments if i['type'] == 'photo']
                    post_images = []
                    for photo in photos:
                        sizes = photo['photo']['sizes']
                        for i in range(len(sizes) - 1):
                            for j in range(len(sizes) - i - 1):
                                if (sizes[j]['height'] * sizes[j]['width']) > (
                                        sizes[j + 1]['height'] * sizes[j + 1]['width']):
                                    sizes[j], sizes[j + 1] = sizes[j + 1], sizes[j]
                        # sort list by size, last image is the highest quality
                        post_images.append(download_photo('vk', user.event_message_from_id, sizes[-1]))

                    # get last post time in unixtime format
                    posts = vk_request.get_group_posts(user.group_id, count=1000,
                                                       postponed=True, last_post=True, only_time=True)
                    data.unix_time = int(posts)
                    data.datatime_convert()
                    # get the next scheduled time
                    t = vk_request.post_timetable([int(f'{data.time.hour}'), int(f'{data.time.minute}')], user.schedule)
                    if t[0]:
                        data.delta_time(delta_days=1)
                    data.replace_time(hour=t[1][0], minute=t[1][1])
                    data.unix_time_convert()
                    # make post
                    make_post = vk_request.new_post(
                        user.group_id, data.unix_time, image=post_images, text=f'{user.event_message_text}')
                    vk.send_message(user_id=user.event_message_from_id,
                                    message=f"Post redy\n{make_post}')\nTime: {data.time}\nAttachments: {post_images}")
                # here all other messages


def download_photo(serv, user_id, size):
    url = size['url']

    db = Database(f'database/{serv}', 'database.db')
    num = db.next_image_number(db.photo_database(user_id))
    photo = db.download_photo(user_id, url, f'image%{num}.png')
    return photo


def vk_save_user_token(user_id, json):
    vk_database = Database('database/vk', 'database.db')
    vk_database.new_directory(f'{user_id}')
    vk_database.sql_user_token_table(json["user_id"], json['user_token'])
    return (vk_database.save_json(user_id, json, 'token.json'))


def vk_user_inf(user_id):
    vk_database = Database('database/vk', 'database.db')
    vk_database.new_directory(f'{user_id}')
    token_json = vk_database.get_file(f'{user_id}', 'token.json')
    if not token_json:
        return False
    else:
        return vk_database.read_json(user_id, token_json)


def user_token_and_group_id_test(url: str, group_id: int):
    if 'com' in url or 'access_token' in url:
        url = url.split('#')
        variables = url[-1].split('&')
        variables = {f"{j[0]}": j[1] for j in [i.split('=') for i in variables]}
        token = variables["access_token"]
    else:
        token = url
    try:
        # using here normal construction with vk.API(vk.Session(access_token), v=version, lang='ru', timeout=10
        # ).secure.checkToken(token=access_token, access_token=service_token)
        vk_api.VkApi(token=token).get_api().wall.get(**{"owner_id": f'-{group_id}', "count": f'100'})
        return {'user_token': token, 'group_id': group_id}
    except:
        return False


def schedule_test(schedule: str):
    if schedule == '.':
        return schedule_table
    else:
        try:
            result = Json.loads(schedule)
            if type(result) is list and all([True for i in result if type(i) is list and len(i) == 2])\
                    and all([True for i in result if i[0] is list and i[1] is list]):
                return result
        except:
            return False


if __name__ == '__main__':
    reset = True
    while True:
        if reset:
            try:
                reset = False
                multi_task_vk()
            except:
                reset = True

"""
Must make later
1) upload and download json in vk bot
2) change schedule
"""
