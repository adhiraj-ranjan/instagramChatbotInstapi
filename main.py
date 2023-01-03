exit(0)
import os
import time
from utils.caffemodel2 import instagramapi as i_api
from PyDictionary import PyDictionary
import wikipedia
from random import randint, choice
import requests
from PIL import Image
from utils.keep_alive import keep_alive
from prsaw import RandomStuffV4
import json
import re
import subprocess
from bs4 import BeautifulSoup

keep_alive()

dict = PyDictionary()

#-----------------Settings---------------
responseTime = 70 # in seconds

#----------------------------------------


rs = RandomStuffV4(api_key=os.environ['apikey'], bot_name='Neuro Tak')
api = i_api(os.environ['USER1'], os.environ['USER1P'])
api.load_session('cookies/insta_chatbot.cookie')
BotUserId = api.userID

api2 = i_api(os.environ['USER2'], os.environ['USER2P'])
api2.load_session('cookies/instabot.image.cookie')
ImageBotUserId = api2.userID

def processImage(img_query, username):
    url = 'https://www.bing.com/images/search?q=' + img_query + '&form=HDRSC2&first=1&tsc=ImageBasicHover'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
           'Connection': 'keep-alive',
           'Referer': 'https://www.bing.com',
           'accept': '*/*',
           'accept-language': 'en-US,en;q=0.9'}


    resonse = requests.get(url, headers=headers)
    soup = BeautifulSoup(resonse.text, 'html.parser')

    images_link = []
    links = soup.find_all('a', {'class': 'iusc'})
    for link in links:
      try:
        image_url = json.loads(link['m'])
        images_link.append(image_url['murl'])
      except:
        return processImage(img_query, username)
    try:
      i_object = requests.get(choice(images_link), headers=headers)
      with open('temps/image.jpg', 'wb') as f:
          f.write(i_object.content)
    except:
      return processImage(img_query, username)
    try:
      Image.open("temps/image.jpg").resize((1080, 1220)).save("temps/resized_Image.jpg")
    except:
      return processImage(img_query, username)
    if api2.upload_photo("temps/resized_Image.jpg",
                         caption=f"Requested by @{username}",
                         tag_users=[username]):
        return True
    else:
        api2.login(show_response=True)
        api2.save_session()
        return False


def getWeather(CITY):
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?q=" + CITY + f"&appid={os.environ['APPID']}"
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        temperature = (str(int(main['temp'] - 270)) + "*C")
        humidity = (str(main['humidity']) + " %")
        pressure = (str(main['pressure']) + " hPa")
        report = data['weather']
        WeatherReport = f'''{CITY:-^22}\n
 Temperature: {temperature}
 Humidity: {humidity}
 Pressure: {pressure}
 Report: {report[0]['description']}'''
        return WeatherReport
    else:
        return "Error in the weather HTTP request, Pls try again after sometime"


count = 0

while True:
    time.sleep(randint(responseTime - 3, responseTime + 3))

    api2.send_text(BotUserId, 'keep_alive')

    api.acceptPendingThreads()

    inbox = api.get_inbox()
    inbox_threads = inbox["inbox"]["threads"]

    for thread in inbox_threads:
        thread_id = thread['thread_id']
        last_thread_item = thread["last_permanent_item"]
        user_id = str(last_thread_item["user_id"])
        if randint(1, 3000) in range(1535, 1540):
            file = open('utils/image_count', 'r')
            image_count = file.read()
            api.changeProfilePicture(f'profilepics/image{image_count}.jpg')
            file.close()
            file = open('utils/image_count', 'w+')
            if int(image_count) + 1 > 28:
                file.write('1')
            else:
                file.write(str(int(image_count) + 1))
            file.close()
            #api.acceptPendingThreads()
            user_id = str(thread['users'][0]['pk'])
        else:
            if user_id == BotUserId:
                continue
        if last_thread_item["item_type"] == "text":
            msgResponse = last_thread_item["text"].lower()
            msg = msgResponse.replace("?", "")
            # check for profile pic request
            if 'profile' in msg and 'of' in msg:
              t_user = msg.split(" ")[-1]
              link = api2.get_profile_pic_link(t_user)
              if link:
                with open('temps/profile_pic.jpg', 'wb') as f:
                  f.write(requests.get(link).content)
              else:
                api.send_text(user_id, 'Invalid username')
                continue
              api.send_image('temps/profile_pic.jpg', thread_id)
              continue
            # weather request
            if "weather of" in msg or "temperature of" in msg:
                city = msg.split(" ")
                api.send_text(user_id, getWeather(city[-1]))
                continue
            # image request
            if "image of" in msg or "picture of" in msg or "photo of" in msg or "pic of" in msg:
                if count == 0:
                    start_timer = time.time()
                time_elapsed = int(time.time() - start_timer)
                if time_elapsed >= 3600:
                    count = 0
                if count < 4:
                    image_to_req = msg.split(" ")[-1]
                    username = thread['inviter']['username']
                    if processImage(image_to_req, username):
                        api.send_text(
                            user_id,
                            "Your image has been uploaded at @instabot.image")
                        count += 1
                        continue
                    else:
                        api.send_text(
                            user_id,
                            "Image not found. Try using a different keyword.")
                        continue
                else:
                    api.send_text(
                        user_id,
                        f"Image request hourly limit reached! You may try after {str((3600 - time_elapsed)//60)} minutes."
                    )
                    continue

            if "what" in msg and "is" in msg and "your" not in msg:
                requestQuery = msg.split(" ")[-1]
                try:
                    querY = wikipedia.summary(requestQuery, sentences=2)
                    api.send_text(user_id, str(querY))
                    continue
                except:
                    querY = dict.meaning(requestQuery)
                    if querY:
                        querY = str(querY).replace('[', '').replace(
                            ']', '').replace('{', '').replace('}', '').replace(
                                '\'', '').replace(',', '\n     ').replace(
                                    'Verb:', '\nVerb:')
                        api.send_text(user_id, str(querY))
                        continue

            # generate response
            try:
                response = rs.get_ai_response(msgResponse)[0]['message']
            except Exception:
                responses = [
                    "Sorry, I didn't understand", "I didn't get that, Try Something else",
                    "Let's talk later, I have some work to finish", "You do not sound Interesting"
                ]
                response = choice(responses)

            # check for Link in message
            if response.startswith('<a'):
                response = re.findall('"([^"]*)"', response)[0]
                api.send_linktext(user_id, response + '\n< Click Here >',
                                 response)
                continue

            api.send_text(user_id, str(response))
        
        elif last_thread_item["item_type"] == "link":
          # keep bot alive
          user_id = str(last_thread_item["user_id"])
          if user_id == ImageBotUserId:
            api.send_text(user_id, 'Response to 127.0.0.1 - SUCCESS')
          else:
            api.send_text(user_id, "no Links allowed kiddo!")

        elif last_thread_item["item_type"] == "media" and last_thread_item['media']['media_type'] == 1:
          img_url = last_thread_item['media']['image_versions2']['candidates'][0]['url']
          with open('temps/bw_image.jpg', 'wb') as f:
            f.write(requests.get(img_url).content)
          subprocess.call('python utils/colorize.py -i temps/bw_image.jpg', shell=True)
          api.send_image('temps/colorized_img.jpg', thread_id)

        else:
            api.send_text(user_id, "Try typing to me, I didn't get these stuffs")
