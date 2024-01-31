#region imports

import io
import base64
from PIL import Image
import aiohttp
from aiohttp import ClientSession
from aiotg import Bot, Chat
from openai import OpenAI
import os
import datetime
import cv2
import json
import shutil
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
import re
import subprocess
import asyncio
import boto3
import winsound
import requests
import json
from PIL import Image
from io import BytesIO
from google.cloud import vision, texttospeech
import pandas as pd
import re
import emoji
from aiohttp import web
import re
import atexit
import ctypes
from termcolor import colored  


from asyncio.exceptions import TimeoutError     #TRYING

#endregion

# region Parameters

params= {}
def Get_Parameters():
    global params
    global API_KEY 
    global DefaultTempForGPT, DefaultTempImageGPT, DefaultImageSteps, LogTextNameFixLength, OpnAIApiKey, OpnAIOrgKey
    global GenImageReplyText, ImageGeneratorURL, ImageGeneratorAddress, ImageGenSystemRoleText
    global ImageGenUserRoleText, ImageGenUserRoleTextRandom, ImageGenDefault, ImageGenSkipThese
    global automatic1111_path, automatic1111_starter, async_bot_path, GOOGLE_APPLICATION_CREDENTIALS
    global ChatGPTErrorReply, weather_api_key, AWS_Lambda_Webhook_URL, admin_Telegram_ID, image_generator_model_name
    global image_generator_sampler_name

    # Read parameters from JSON
    with open('_main/params.json', 'r') as f:
        paramsNew = json.load(f)
    if params != paramsNew:
        print('** New Parameters Updating **')

        OpnAIApiKey = paramsNew['openai_api_key']
        OpnAIOrgKey = paramsNew['openai_organization']
        AWS_Lambda_Webhook_URL = paramsNew ['AWS_Lambda_Webhook_URL']
        API_KEY = paramsNew['telegram_api_key']
        admin_Telegram_ID = paramsNew['admin_Telegram_ID']
        weather_api_key = paramsNew['weather_api_key']
        DefaultTempForGPT = paramsNew['default_temp_for_gpt']
        DefaultTempImageGPT = paramsNew['default_temp_image_gpt']
        DefaultImageSteps = paramsNew['default_image_steps']
        LogTextNameFixLength = paramsNew['log_text_name_fix_length']
        GenImageReplyText = paramsNew['gen_image_reply_text']
        ImageGeneratorURL = paramsNew['image_generator_url']
        ImageGeneratorAddress = paramsNew['image_generator_address']
        ImageGenSystemRoleText = paramsNew['image_gen_system_role_text']
        ImageGenUserRoleText = paramsNew['image_gen_user_role_text']
        ImageGenUserRoleTextRandom = paramsNew['image_gen_user_role_text_random']
        ImageGenDefault = paramsNew['image_gen_default']
        ImageGenSkipThese = paramsNew['image_gen_skip_these']
        ChatGPTErrorReply = paramsNew['chat_gpt_error_reply']
        automatic1111_path = paramsNew['automatic1111_path']
        automatic1111_starter = paramsNew['automatic1111_starter']
        async_bot_path = paramsNew['async_bot_path']
        image_generator_model_name = paramsNew ['image_generator_model_name']
        image_generator_sampler_name = paramsNew ['image_generator_sampler_name']
        GOOGLE_APPLICATION_CREDENTIALS = paramsNew['GOOGLE_APPLICATION_CREDENTIALS']
Get_Parameters()

client = OpenAI(api_key=OpnAIApiKey)    # update OPENAI new client system


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
bot = Bot(api_token=API_KEY)


#endregion

#region Telegram Handled Inputs

@bot.command(r"^/(weather|hava|havadurum|havadurumu|waether|wether)(?:\s+(.*))?$")
async def tele_weather (chat: Chat, match):
    try:
        BotPrps = await GetBotProps(chat)
        langname = BotPrps[2]
        remainder = match.group(2)  # get the remaining string

        if remainder is not None:
            ReplyText=[]
            ReplyText = get_weather_replies_by_lang(langname)
            #print (f"Match: {remainder}")
            weather,image = await get_weather(langname,remainder)
            image = image.convert("RGBA")

            if weather != "ERROR":
                #print (weather)
                if image:
                    byte_image = BytesIO()
                    image.save(byte_image, format='PNG')
                    byte_image.seek(0)  # Move the cursor back to the beginning of the file
                    await chat.send_photo(byte_image)
                await chat.send_text(weather)
                makelog (chat,weather,True)
            else:
                await chat.send_text(f' {ReplyText["errCon"]} {remainder}')
                makelog (chat,(f' {ReplyText["errCon"]} {remainder}'),True)

        else:
            await chat.send_text(ReplyText["errcity"])
            makelog (chat,ReplyText["errcity"],True)
            
    except:
        await chat.send_text(ReplyText["errUnkn"])
        makelog (chat,ReplyText["errUnkn"],True)

@bot.command(r"^\/?help$")                # /help komutu verilirse
async def Help_EN(chat: Chat, match):
    sendHelpScreen(chat)

@bot.command(r"^/(yardim|yardım)$")              # /yardim komutu verilirse
async def Help_TR(chat: Chat, match):
    sendHelpScreen(chat,True)

@bot.command(r"^/start")                     # /start verilirse
async def Start_EN(chat: Chat, match):
    sendHelpScreen(chat)

@bot.command(r"^/lock")                     # /lock the pc verilirse
async def LockPC(chat: Chat, match):
    user_id = chat.sender["id"]
    if checkAuth(chat,match):
        makelog (chat,f"{user_id} - LOCK PC command from admin. Processing.",True)
        ctypes.windll.user32.LockWorkStation()

@bot.command(r"^/shutdown")                     # /shutdown the pc verilirse
async def LockPC(chat: Chat, match):
    user_id = chat.sender["id"]
    if checkAuth(chat,match):
        makelog (chat,f"{user_id} - SHUTDOWN command from admin. Processing.",True)
        os.system("shutdown /s /t 1")

@bot.command(r"^/(restart|reboot)$")                     # /lock the pc verilirse
async def LockPC(chat: Chat, match):
    user_id = chat.sender["id"]
    if checkAuth(chat,match):
        makelog (chat,f"{user_id} - Restart command from admin. Processing.",True)
        os.system("shutdown /f /r /t 1")

@bot.command(r"^/image(?:\s+(.*))?$")       # /image komutu verilirse
async def gen_image(chat: Chat, match):
    #return chat.reply(match.group(1))
    prompt=match.group(1)
    NumStep = DefaultImageSteps
    if prompt is None:
        GenPrompt = await GetGenerativePrompt (chat)
    else:
        st_pattern = re.compile(r"—st(\d+)")
        st_match = st_pattern.search(prompt)
        if st_match:
            NumStep =  int(st_match.group(1)) if int(st_match.group(1))<60 else 59
            
            GenPrompt = st_pattern.sub("", prompt).strip()
        else:
            GenPrompt = prompt
        
        if GenPrompt is None or GenPrompt == "" or GenPrompt == " ":
            GenPrompt = await GetGenerativePrompt (chat)
                
    async with ClientSession() as session:
        makelog(chat,f'Image Generating: {GenPrompt} Steps:{NumStep}',True)
        chat.send_text (f"\n {GenImageReplyText} \n {GenPrompt} \n\n- Steps:  {NumStep}")
        await genimage(GenPrompt, NumStep, session, chat)

@bot.command(r"^/camera")                    # /camera komutu verilirse
async def camera_pic(chat: Chat, match):
    if await checkAuth(chat,match):
        playsound("_main/camera-shutter-click-01.wav")
        await get_cam_photo(chat)
        makelog (chat,"Cam Photo Shared")

@bot.command(r"^/new")                       # /new komutu verilirse
async def clearChat(chat: Chat, match):
    await ClearChatContents(chat)
    makelog (chat,"Chat Cleared")

@bot.command(r"^/bot(?:\s+(\d+))?")          # /bot komutu verilirse
async def select_bot(chat: Chat, match):
    if (match == '/bot'):
        attribs = None
    else:
        attribs = match.group(1)   
    thisvalid=False
    if attribs is not None:
        try:
            rcvd = int(attribs)
            if rcvd in range (1,11):
                await ClearChatContents(chat)
                newbot,newchat,name,lang,mtemp = thisusersBot(chat,str(rcvd))
                makelog (chat,f"NEW BOT SELECTED: {newbot} - {name} - {lang}")
                thisvalid = True
        except:
            thisvalid = False
    if not thisvalid:
        print('Specify a bot please.')
        therep = "\n"
        with open(f'_main/systemroles_ext.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for role in data['systemRoles']:
            therep += f"BOT {str(role['id'])} : {role['name']} -- {role['language']}\n"
        try:
            abc = []
            abc = thisusersBot(chat)
            curbot = f"Current bot: {abc[0]} - {abc[2]} - {abc[3]}\n"
        except:
            curbot= ""
        chat.send_text (f"Please Select from below modes\n {therep} \nExample: /bot 6 \n\n{curbot}")

@bot.command(r"^/(.+)")                      # / ile başlayan anlamsız komutlara cevap
async def unknown(chat:Chat,match):
    await chat.reply ("No such command.")
    with open('_main/helptext.txt', 'r') as file:
        helptext = file.read()
    await chat.send_text(helptext)
    makelog(chat,f'Unknown Command Tried: {match}',True)

@bot.command(r"(?s)(.+)")                   # Normal Chat Mode'u
async def text_input(chat: Chat, match):
    prompt = match.group(1)
    prompt = re.sub(r'\n+', '\\n', prompt)  # remove extra newlines
    answer = await chatGPT(chat, prompt)
    if answer:
        await chat.send_text(answer)

@bot.handle("photo")                        # fotoğraf yüklenirse
async def tele_photo(chat:Chat,photo):
    try:
        time = datetime.datetime.now().strftime("%y-%m-%d_%H_%M_%S")

        file_id = photo[-1]["file_id"]
        file_info = await bot.api_call("getFile", file_id=file_id)
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{API_KEY}/{file_path}"

        saved_file_name = f'{getdir(chat,"pictures")}/Pic_{time}.jpg'

        #download the picture from the fileurl
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                with open(saved_file_name, "wb") as f:
                    while True:
                        chunk = await resp.content.read(1024)  # read 1024 bytes
                        if not chunk:
                            # we are done reading the file
                            break
                        f.write(chunk)

        whatisinimage = Interrogate_Image(saved_file_name)[0:1000]

        imageContains= await chatGPTimageResult(chat, whatisinimage)
        chat.send_text(text=imageContains)
        makelog(chat,f'Image Contains: \n\n{imageContains}',True)
        makelog(chat,f'Users Picture Saved: Pic_{time}.jpg',True)
    except:
        chat.send_text(text = 'Thanks for the picture!')

    #chat.send_text(text=f"Picture? Why??")

@bot.handle("sticker")                      # Handle the stickers
async def sticker_handle(chat:Chat,sticker):
    time = datetime.datetime.now().strftime("%y-%m-%d_%H_%M_%S")
    user_name = getUserName(chat)
    user_id = chat.sender["id"]
    myemoji = (sticker["emoji"])
    myemojidesc = (describe_emoji (myemoji))
    chat.send_text (myemoji)
    makelog(chat,f"Emoji: {myemoji} {myemojidesc}", False)
    getusermessages (chat,"user", f"{myemoji} {myemojidesc}" )
    makelog(chat,f"Emoji: {myemoji} {myemojidesc}",True)
    getusermessages (chat,"assistant",f"{myemoji} {myemojidesc}" )

@bot.handle("voice")                        # VOICE COMMANDS
async def voice_handler(chat: Chat, voice):
    file_id = voice["file_id"]
    duration = voice["duration"]
    file_info = await bot.api_call("getFile", file_id=file_id)
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{API_KEY}/{file_path}"

    if duration < 1:
        await chat.send_text(f"Ne dedin? Sorry, what was that??")
    else:
        theText = await teleVoiceFileToTxt (chat,file_url)
        #await chat.send_text(f"YouSaid: {theText}")
        try:
            characters_to_escape = r"_*[]()~`>#&+{}=_|.!"
            escaped_text = "".join(f"\\{char}" if char in characters_to_escape else char for char in theText)
            await chat.send_text(f'You: _{escaped_text}_', parse_mode="MarkdownV2")
        except:
            await chat.send_text(f'You: {theText}')

        answer = await chatGPT(chat,theText)

        await chat.send_text(answer)

        try:
            replyfile = await reply_with_voice (chat, answer)

            if replyfile is not None:
                with open(replyfile, "rb") as file:
                    print('replying')
                    await chat.send_audio(file)
                file.close()
                os.remove(replyfile)
        except Exception as e:
            print (e)
#endregion

#region Helper routines

def describe_emoji(e):
    return (emoji.demojize(e).strip(":").replace('_', ' '))

def sendHelpScreen(chat:Chat,Turkce = False):
    fname = "_main/helptext.txt"
    if Turkce:
        fname = "_main/yardimtext.txt"
    with open(fname, 'r',encoding='utf-8') as file:
        helptext = file.read()
    chat.send_text(helptext)

async def reply_with_voice (chat: Chat,inputtxt):

    BotPrps = await GetBotProps(chat)
    langname = BotPrps[2]
    gender= BotPrps[4]
    googleVoiceName = BotPrps[9]

    mylan= "en-US"
    if langname == 'Turkish':
        mylan = "tr-TR"
    elif langname == 'Hindi':
        mylan= "hi-IN"
    else:
        mylan = "en-US"


    VoiceGet = await google_synth_speech (Language = mylan,Gender = gender, text_to_talk= inputtxt, GoogleVName= googleVoiceName) 
    # The response's audio_content is binary.


    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    thefolder= getdir(chat,'temp')
    thefile = thefolder + "/" +timestamp + '.mp3'

    with open(thefile, "wb") as out:
        # Write the response to the output file.
        out.write(VoiceGet.audio_content)
        # print('Audio content written to file "output.mp3"')
    return (thefile)

async def google_synth_speech(Language ="en-US", Gender ="neutral", text_to_talk = "Hello there.." , GoogleVName="en-US-Standard-B"):

    client = texttospeech.TextToSpeechClient()

    mpitch = "default"

    # Set the SSML text input to be synthesized

    # Mapping input string gender to the proper Enum value
    if Gender.lower() == "male":
        ssml_gender = texttospeech.SsmlVoiceGender.MALE
    elif Gender.lower() == "female":
        ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
    else:
        ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL
        mpitch = "high"
    
    synthesis_input = texttospeech.SynthesisInput(ssml=f'<speak><prosody rate="medium" pitch="{mpitch}">{text_to_talk}</prosody></speak>')

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=Language.lower(),
        name=GoogleVName,
        ssml_gender=ssml_gender)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config)

    return (response)

async def ClearChatContents (chat: Chat):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nul1, mdir = getdir(chat,'convs'), getdir(chat)
    try:
        if os.path.exists(f"{mdir}/conversation.json"):
            shutil.move(f"{mdir}/conversation.json", f"{mdir}/convs/conv_"+timestamp+".json")
    except:
        if os.path.exists(f"{mdir}/conversation.json"):
            os.remove(f"{mdir}/conversation.json")
    finally:
        chat.send_text("Ok. I forget what we talked before.")

async def checkAuth(chat,match):
    user_name = getUserName(chat)
    user_id = chat.sender["id"]
    if user_id == admin_Telegram_ID:
        return True
    else:
        print (user_name)
        print (user_id)
        await chat.reply("You are not authorized for this.")
        makelog (chat, "Unauthorized request. DENIED." ,True)
        return False

def makelog (chat, log_text, isbot = True):
    user_name = getUserName(chat)
    user_id = chat.sender["id"]
    mydir = getdir(chat)

    mitext = f'{fixed_size_string(user_name,14)} : {log_text}'

    if isbot:
        retbot = thisusersBot(chat)
        mitext= f'{fixed_size_string(retbot[2],14)} : {log_text}'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    comptext = timestamp + " // " + mitext 

    with open(f'./{mydir}/log.txt', 'a',encoding='utf-8') as file:
        file.write(f"{comptext}\n")
        print(comptext)

    file.close()

async def genimage(prompt, NumOfSteps, session, chat):
    payload = {
        "prompt": f"{prompt}",
        "steps": NumOfSteps,
        "sampler_index": image_generator_sampler_name
    }
    
    option_payload = {
        "sd_model_checkpoint": image_generator_model_name
    }
    try:
        async with session.post(url= f'{ImageGeneratorURL}/sdapi/v1/options', json=option_payload) as responseChangeCkpt:
            if responseChangeCkpt.status ==200:
                print("Generating image using Realistic Vision v6 model")
            else:
                print(f"\nresponseChangeCkpt")
                print (responseChangeCkpt.status)
    except Exception as e:
        print("Something went wrong: ",e)
        
    try:
        async with session.post(url= ImageGeneratorAddress, json=payload) as response:
            r = await response.json()
            k = 0
            for i in r['images']:
                k += 1
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                genim_filename = getdir(chat,'generated/img_') + timestamp + "_"+str(k)+".jpg"
                #genim_filename = f"img__{k}.jpg"
                image.save(genim_filename)
                with open(genim_filename, "rb") as file:
                    #await chat.reply(f"Here is your generated image: {prompt}")
                    #await chat.reply(f"Buyrun: {prompt}")
                    await chat.send_photo(file,caption=prompt)
                print(f'Generated {prompt}..')
                makelog (chat,f"Image Generated: {prompt} and saved as {genim_filename}")

                getusermessages (chat,'user',f'Can you generate for me a picture: {prompt}')
                getusermessages (chat,'assistant',f'Here is your picture. I am sending it to you.')
        
                # getusermessages (chat,'assistant',f'I have prepared a picture for you. Here I am sharing. {prompt}')
    except:
            generated = False
            startretry = 3
            chat.reply(text=f"Image Generator Offline. Trying to start up.")
            makelog(chat,"Image Generator Offline. Trying to start up.",True)
            os.chdir(automatic1111_path)
            myfile = automatic1111_starter
            subprocess.Popen(f'cmd.exe /c start {myfile}', shell=True)
            #subprocess.Popen(myfile, shell=True)
            os.chdir(async_bot_path)
            while startretry>0:
                startretry = startretry -1
                # print (startretry)
                if await is_generator_online(session):
                    await chat.reply(text="Image Generator is now online. Trying again..")
                    await genimage(prompt, NumOfSteps, session, chat)
                    generated = True
                    break
                else:
                    await asyncio.sleep(15)  # Wait for 5 seconds before checking again
                    
            if not generated:
                await chat.reply(text="Sorry. Could not start Image Generator..")
                makelog(chat,"Could not start Image Generator..",True)

async def GetGenerativePrompt (chat):
    conversation = []
    systemimage = [({"role": "system", "content": ImageGenSystemRoleText})]
    try:
        with open(f'{getdir(chat,".")}/conversation.json', 'r') as f:
            conversation = json.load(f)[-9:]
            #combine4 = systemimage + conversation
        content_str = ImageGenUserRoleText
        for ms in conversation:
            content_str += "- " + ms["content"] + "\n"
        userstr = [({"role": "user", "content": content_str})]
        combine4 = systemimage + userstr
    except:
        content_str = ImageGenUserRoleTextRandom
        userstr = [({"role": "user", "content": content_str})]
        combine4 = systemimage + userstr

    
    #print ("Generation String:")
    #print(combine4)
    makelog (chat,f"Generation String:\n{combine4}",True)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=combine4,
            max_tokens=1000,
            temperature = DefaultTempImageGPT
        )
        ChatGPT_reply = response.choices[0].message.content
    except:
        ChatGPT_reply = ImageGenDefault

    ChatGPT_reply = skipPres(ChatGPT_reply)
    ChatGPT_reply = skipPres(ChatGPT_reply)
    ChatGPT_reply = skipPres(ChatGPT_reply)


    makelog (chat,f'ChatGPT Image Prompt Generated: {ChatGPT_reply}')

    return(ChatGPT_reply)

def skipPres(TheReply):
    for prefix in ImageGenSkipThese:
        if TheReply.startswith(prefix):
            TheReply = TheReply[len(prefix):].lstrip()
    return TheReply

def getdir (chat,dirname='.'):
    user_name = getUserName(chat)
    user_id = chat.sender["id"]
    if dirname:
        mydir = os.path.join(".", "_main/users", f"{user_id}-{user_name}", dirname)
    else:
        mydir = os.path.join(".", "_main/users", f"{user_id}-{user_name}")
    if not os.path.exists(mydir):
        os.makedirs(mydir)
    return mydir

async def get_cam_photo(chat):
    user_name = getUserName(chat)
    user_id = chat.sender["id"]
    cap = cv2.VideoCapture(0)
    # Capture a single frame
    ret, frame = cap.read()
    # Save the frame to a file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    capim_filename = f"{getdir(chat,'capture')}/cap_{timestamp}.jpg"

    cv2.imwrite(f'{capim_filename}', frame)
    #print (capim_filename)
    with open(capim_filename, 'rb') as f:
        await chat.send_photo (f)
    # Release the camera
    # cap.release()
    # Close all OpenCV windows
    # cv2.destroyAllWindows()

    #makelog ....

async def teleVoiceFileToTxt(chat,file_url):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mdir = getdir(chat,'voices')
    local_filename = f"{mdir}/{timestamp}.oga"
    await download_file(file_url, local_filename)
    oga_audio = AudioSegment.from_ogg(local_filename)
    mp3_filename = f"{local_filename[:-3]}.mp3"
    oga_audio.export(mp3_filename, format="mp3")
    os.remove(local_filename)

    makelog(chat,f"Voice recording saved {timestamp}.mp3",False)

    Botlanguage="en-US"
    Botlanguage="tr-TR"

    try:
        #n1,n2,n3,Botlanguage,n5,n6,n7,n8,ntemp , ntemp6= await GetBotProps(chat)
        BotPrps = await GetBotProps(chat)
        Botlanguage = BotPrps[3]
        #print (f"Bot Lang A1: {Botlanguage}")
    except:
        Botlanguage = "tr-TR"
        #print (f"Bot Lang: {Botlanguage}")

    audio_file = open(mp3_filename, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file = audio_file).text
    return(transcript)

async def download_file(url, local_filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(local_filename, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)


class MockMatch:
    def __init__(self, group2):
        self.group2 = group2

    def group(self, index):
        if index == 2:
            return self.group2
        return None


async def chatGPT(chat: Chat, prompt):
    winsound.Beep(1440, 25)
    Get_Parameters()
    user_name = getUserName(chat)

    user_id = chat.sender["id"]
    geridon = user_name + "-" + prompt
    botmode, usermessages, botTemp = getusermessages (chat,"user",prompt)
    combined = botmode + usermessages

    makelog (chat,prompt,False)
    # print (f"\r\n\r\nTOPLAM GIDEN :{combined}\r\n\r\n")


    function_selector_fn = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name, e.g. Istanbul. Default to Istanbul if not defined. Make sure it is a city name or default to Istanbul",
                            }
                        },  
                        "required": ["location"]
                    }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate an image",
                "parameters": {
                        "type": "object",
                        "properties": {
                            "image_prompt": {
                                "type": "string",
                                "description": "The prompt for generating an image.",
                            }
                        },  
                        "required": []
                }
            }
        }
    ]


    try:
        # response = openai.ChatCompletion.create(
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=combined,
            tools = function_selector_fn,
            max_tokens=1500,
            temperature = botTemp
        )
        print(str(combined),"\n\n")
        print (response,"\n")
        assistant_message = response.choices[0].message.tool_calls
        if assistant_message:
            print (assistant_message)
            fnargs = json.loads(assistant_message[0].function.arguments)
            fn_Name=  assistant_message[0].function.name
            if fn_Name == "get_current_weather":
                ppp = fnargs["location"]
                await tele_weather ( chat ,  MockMatch(ppp))
                return ()
            elif fn_Name == "generate_image":
                if fnargs["image_prompt"]:
                    ppp = fnargs["image_prompt"]
                else:
                    ppp = ""
                await gen_image (chat, MockMatch(ppp))
                return ()
        else:
            ChatGPT_reply = response.choices[0].message.content
            ln1,ln2,ln3 = response.usage.prompt_tokens,response.usage.completion_tokens,response.usage.total_tokens
            tokeninfo = f" - [Tokens: {ln1}-{ln2}-{ln3}]"
            #tokeninfo = ""
            makelog (chat,ChatGPT_reply + tokeninfo,True)
            getusermessages(chat,"assistant",ChatGPT_reply)
            return (f"{ChatGPT_reply}")
    except Exception as e:
        print (f"Exception:\n{e}\n")

        if str(e).startswith("This model's maximum context"):
            #delete some 
            DeleteLongest (chat)
            print ('DELETED')
            return ('Try again please.. Too much input for ChatGPT\nLütfen tekrar deneyin. Fazla yüklendik..')

        makelog (chat,"ChatGPT raised Error",True)
        DeleteLast(chat)
        return (ChatGPTErrorReply)

async def chatGPTimageResult(chat:Chat, prompt):
    Get_Parameters()
    user_name = getUserName(chat)

    myTable = VisionToTable(prompt)
    print (f"\n\nMY TABLE:\n\n{myTable}")
    imageReqLine = [{
        "role": "system", 
        "content": "You are a predictor which analysis text contents about a picture and sends back the best possible results. You give prompt answers and you do not mention about the table given to you. You just type in what you understand from the input material"
        }]
    if botsLanguage(chat) == "Turkish":
        reptr = "Please provide the answer fully in Turkish"
    else: reptr=""

    newline =  imageReqLine+[{"role": "user", "content": f"Here is the probabilities about a picture as a table:\n\n{myTable}\n\nPlease type down what is in the picture considering this table. Do not mention the table, just give prompt answer. {reptr} "}]

    print (newline)

    try:
        # response = openai.ChatCompletion.create(
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=newline,
            max_tokens=1500,
            temperature = 0.1
        )
        ChatGPT_reply = response.choices[0].message.content

        ln1,ln2,ln3 = response.usage.prompt_tokens,response.usage.completion_tokens,response.usage.total_tokens

        tokeninfo = f" - [Tokens: {ln1}-{ln2}-{ln3}]"
        #tokeninfo = ""
        makelog (chat,ChatGPT_reply + tokeninfo,True)
        getusermessages(chat,"assistant",ChatGPT_reply)
        return (f"{ChatGPT_reply}")
    except Exception as e:
        print (f"Exception:\n{e}\n")

        if str(e).startswith("This model's maximum context"):
            #delete some 
            DeleteLongest (chat)
            print ('DELETED')
            return ('Try again please.. Too much input for ChatGPT\nLütfen tekrar deneyin. Fazla yüklendik..')

        makelog (chat,"ChatGPT raised Error",True)
        DeleteLast(chat)
        return (ChatGPTErrorReply)

def DeleteLast(chat):
    try:
        with open(f'{getdir(chat,".")}/conversation.json', 'r') as f:
            conversation = json.load(f)[:-1]
            with open(f'{getdir(chat,".")}/conversation.json', 'w') as f:
                json.dump(conversation, f)
    except:
        os.remove(f'{getdir(chat,".")}/conversation.json')
        print('Chat Deleted')

def DeleteLongest(chat):
    try:
        with open(f'{getdir(chat,".")}/conversation.json', 'r') as f:
            conversation = json.load(f)[-9:]

        longest_text = ''
        longest_length = 0
        longest_index = -1

        for i, entry in enumerate(conversation):
            content = entry['content']
            if len(content) > longest_length:
                longest_text = content
                longest_length = len(content)
                longest_index = i

        if longest_index >= 0:
            if conversation[longest_index]['role'] == 'user':
                del conversation[longest_index]
                try:
                    del conversation[longest_index]
                except:
                    a1=1
            else:
                del conversation[longest_index-1]
                del conversation[longest_index-1]

            with open(f'{getdir(chat,".")}/conversation.json', 'w') as f:
                json.dump(conversation, f)

    except:
        os.remove(f'{getdir(chat,".")}/conversation.json')
        print('Chat Deleted')

def getUserName(chat):
    try:
        user_name = chat.sender["username"]
    except Exception as e:
        #print (f'Exception {e}')
        user_name = "NoUserName"
    return (user_name)

def fixed_size_string(s, size=LogTextNameFixLength):
    if len(s) > size:
        return s[:size]  # Truncate the string to the desired size
    elif len(s) < size:
        return s + " " * (size - len(s))  # Pad the string with spaces
    else:
        return s

def getusermessages (chat: Chat,role,new_message):
    botmode = []
    conversation = []
    newline = [{"role": role, "content": new_message}]
    try:
        with open(f'{getdir(chat,".")}/conversation.json', 'r') as f:
            conversation = json.load(f)[-9:]
            conversation.append (newline[0])
        f.close()
    except:
        conversation = newline

    finally:
        with open(f'{getdir(chat,".")}/conversation.json', 'w') as f:
            json.dump(conversation, f)
        f.close()
    botnum,botmode,x,y,z = thisusersBot(chat)
    
    combined = botmode + conversation
    #print (f"Combined Returned: {combined}")    
    return(botmode,conversation,z)

def botsLanguage(update):
    mylang = "English"
    try:
        a,b,c,d,e = thisusersBot(update)
        mylang = d
    except:
        mylang = "English"
    return (mylang)

def thisusersBot(update,newbot = None):
    if newbot is not None:
        with open(f"{getdir(update,'')}/bot.txt", 'w',encoding='utf-8') as file:
            file.write(newbot)
            botnum = newbot
            with open(f'_main/systemroles_ext.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            for role in data['systemRoles']:
                if str(role['id']) == botnum:
                    update.send_text(f"New mode {newbot} : {role['name']} -{role['language']} ")
                    startSent = [{"role": "system", "content": role['description']}, {"role": "user", "content": role['fsmessage']}, {"role": "user", "content": role['fsreply']}] 
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    mdir = getdir(update)
                    try:
                        shutil.move(f"{mdir}/conversation.json", f"{mdir}/convs/conv_"+timestamp+".json")
                    finally:
                        return botnum, startSent , role['name'],role['language'],role['Temp']

    else:
        botfile = f"{getdir(update,'')}/bot.txt"
        try:
            with open(botfile, 'r',encoding='utf-8') as file:
                for bots in file:
                    botnum  = bots.strip()
        except:
            with open(botfile, 'w',encoding='utf-8') as file:
                file.write('6')
                botnum = '6'
                # make a list of the bots
                print('Specify a bot please.')
                therep = "\n"
                with open(f'_main/systemroles_ext.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                for role in data['systemRoles']:
                    therep += f"BOT {str(role['id'])} : {role['name']} -- {role['language']}\n"
                sendHelpScreen(update)
                update.send_text (f"Please Select from below modes\n {therep} \n\nUsage: /bot 6")

        finally:
            with open(f'_main/systemroles_ext.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            for role in data['systemRoles']:
                if str(role['id']) == botnum:
                    #update.message.reply_text(text=f"*[Bot]:* New mode {botnum} : {role['description']}", parse_mode=telegram.ParseMode.MARKDOWN)
                    startSent = [{"role": "system", "content": role['description']}, {"role": "user", "content": role['fsmessage']}, {"role": "user", "content": role['fsreply']}] 
                    return botnum, startSent, role['name'],role['language'],role['Temp']
        update.send_text(f"*ERROR* New mode: 0 -  You are a helpful assistant")
        return "0",{"You are a helpful assistant."},"AI","English",0

async def GetBotProps(chat: Chat):
    botfile = f"{getdir(chat,'')}/bot.txt"
    try:
        with open(botfile, 'r',encoding='utf-8') as file:
            for bots in file:
                botnum  = bots.strip()
    except:
        with open(botfile, 'w',encoding='utf-8') as file:
            file.write('6')
            botnum = '6'
    finally:
        with open(f'_main/systemroles_ext.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for role in data['systemRoles']:
            if str(role['id']) == botnum:
                return botnum,role['name'],role['language'],role['lancode'],role['gender'],role['description'],role['fsmessage'],role['fsreply'],role['Temp'],role['googlevoice']
    chat.send_text(f"*ERROR* New mode: 0 -  You are a helpful assistant")
    return "0","NONE","English","en-US","male","You are a helpful assistant","Hi","Hello",0, "en-US-Standard-B"

async def is_generator_online(session):
    try:
        async with session.get(url=ImageGeneratorURL) as response:
            if response.status == 200:
                return True
            else:
                return False
    except:
        return False

async def get_weather(lang,city):
    api_key = weather_api_key
    base_url = "http://api.weatherapi.com/v1/current.json"


    ReplyText = get_weather_replies_by_lang(lang)

    # Create the parameters for the request
    params = {
        'key': api_key,
        'q': city
    }

    # Make the request
    response = requests.get(base_url, params=params)

    # Parse the response
    if response.status_code == 200:
        data = response.json()
        weathertemp = data['current']['temp_c']
        weathercity = data['location']['name'] + ", " + data['location']['country']
        weatherstat =  data['current']['condition']['text']
        weatherwind =  data['current']['wind_kph']
        weatherfeel =  data['current']['feelslike_c']


        tempval = f"{ReplyText['curw']} {weathercity} \n\n"
        tempval = tempval + f"{ReplyText['temp']} {weathertemp}°C\n"
        tempval = tempval + (f"{ReplyText['feel']} {weatherfeel}°C\n")
        tempval = tempval + (f"{ReplyText['stat']} {weatherstat}\n")
        tempval = tempval + (f"{ReplyText['wind']} {weatherwind}{ReplyText['unit']} \n")
        try:
            icon_url = data['current']['condition']['icon']
            icon_response =  requests.get('https:'+icon_url)
            # Open the image and display it
            image = Image.open(BytesIO(icon_response.content))
            # image.show()
        except:
            image=None
        return (tempval,image)
    else:
        print(f"Weather Get Error: {response.status_code}")
        return ("ERROR",None)

def get_weather_replies_by_lang(lang):
    with open(f'_main/weather_replies.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for langset in data['weather']:
        if langset['language'] == lang:
            return{
                'errCon': langset['errCon'],
                'errcity': langset['errcity'],
                'errUnkn': langset['errUnkn'],
                'curw':langset['curw'],
                'temp':langset['temp'],
                'feel': langset['feel'],
                'stat':langset['stat'],
                'wind':langset['wind'],
                'unit':langset['unit']
            }
        

    return {
		"errCon": "Error getting weather info for",
		"errcity": "Error getting weather info. Please specify city",
		"errUnkn": "Error getting weather info (B)",
		"curw": "Current weather status in ",
		"temp": "Temperature: ",
		"feel": "Feels like : ",
		"stat": "Status     : ",
		"wind": "Wind       : ",
		"unit": " kmph"
    }

def Interrogate_Image(image_file_path):

    client = vision.ImageAnnotatorClient()

    with io.open(image_file_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.annotate_image({
    'image': image,
    'features': [{'type_': vision.Feature.Type.LABEL_DETECTION}]
    })
    return (str(response))

def VisionToTable(content):
    blocks = content.split('label_annotations')

    # Parse each block and append it to a list
    data = []
    mystr="LABELS:description,score,topicality\n"
    for block in blocks:
        if block.strip() != '':
            mystr= mystr+parse_block2(block)

    # Convert the list of dictionaries into a DataFrame
    #print (f"Deneme Str: {mystr}")
    return(mystr)

def parse_block2(block):
    """
    Parses a block of text and returns a dictionary containing the data.
    """
    lines = block.split('\n')

    denemestr="DATA:"

    for line in lines:
        line = line.strip()
        match = re.match(r'description: "(.*)"', line)
        if match:
            denemestr = denemestr+ match.group(1) + ","
        else:
            match = re.match(r'score: (\d+\.\d+)', line)
            if match:
                # Convert to float and format with two decimal places
                denemestr = denemestr+ format(float(match.group(1)), '.2f') + ","
            else:
                match = re.match(r'topicality: (\d+\.\d+)', line)
                if match:
                    denemestr = denemestr+ format(float(match.group(1)), '.2f') + "\n"
        
    #print (f"Deneme Str: {denemestr}")
    return denemestr

def send_Startup_message(user_id, message="Hello!"):
    chat = Chat(bot, user_id)
    chat.send_text(message)

#endregion

#region Response Online Status to Amazon

async def delhook():
    try:
        response = requests.post(
            f'https://api.telegram.org/bot{API_KEY}/deleteWebhook')
        print(response)
        if response.status_code == 200:
            myres= 'HOOK DELETED'
        else:
            myres = 'Something Wrong' + str(response)
    except:
        myres = '** HOOK NOT DELETED. MANUALLY DELETE FROM TELEGRAM. **'
    return(myres)

async def handle(request):
    await delhook()                     
    return web.Response(text="OK")

async def start_server():
    print (await delhook())
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9988)  # 
    await site.start()

def sethook():
    response = requests.post(
        f'https://api.telegram.org/bot{API_KEY}/setWebhook',
        params={'url': AWS_Lambda_Webhook_URL}
    )       
    print (response.content)

def cleanup():
    # Your cleanup code or any other function you want to run
    print("Adding WebHook to Telegram...")
    try:
        sethook()
    except Exception as e:
        print (e)

app = web.Application()
app.router.add_get('/', handle)

#endregion


# atexit.register(cleanup)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_server())
    send_Startup_message(admin_Telegram_ID,"BOT STARTED")
    print ("READY.")
    loop.run_until_complete(bot.run())
