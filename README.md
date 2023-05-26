# telegram_bot

A Telegram bot using ChatGPT to answer any question.
The code is working in async mode.

Some features are:
 * Select language of the bot
 * Select a bot character (you can easily add any character you want)
 * Chat / ask qustions
 * You can use ChatGPT-3, ChatGPT-4, da-vinci models or others provided by openAI
 * Chat with voice (and the reply comes also as voice)
 * Send pictures and let the bot tell what is inside
 * Generate pictures (using Automatic1111 on your computer or any cloud platform)
 * You as admin, can also use the bot to remotely control your computer which is running the code

## Before you begin
**Why not take a look at how the bot is working, before installing**

   Follow the below link to open your Telegram to reach the bot running on my computer.
   
   If you don't get answer, my PC might be offline.
   
   https://t.me/FunnyAndDumb_bot

**The code has been tested only on Windows Environment**

## Prerequisites

This section will list the software and knowledge prerequisites for using this bot.

- Python 3.10.6 or later
- pip (Python Package Installer) - You can choose to install pip while installing Python.
- Git
- Basic understanding of Python and Telegram bots


## Installation & Setup


1. **Clone the repository**

   Run the following command in the terminal to clone this repository:
   
   ```bash
   git clone https://github.com/alperinugur/com/alperinugur/telegram_bot.git
   
2. **Navigate to the cloned repository**

    Change the current working directory to your new cloned directory:
   ```bash
   cd YOUR_PROJECT_NAME

3. **Install Python**

   If Python is not installed, download and install it from python.org.

4. **Set up a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux
   .\venv\Scripts\activate   # For Windows

5. **Install dependencies**

   Install the necessary packages using pip:
   ```bash
   pip install -r requirements.txt

6. **Update params.json file with your credentials**

   The file "./main/params.json" holds all of the parameters of your credentials.
   These include:
   * OpenAI API Key
   * OpenAI Organization Key
   * Telegram API Key
   * Amazon AWS Access Key Id       (for voice enabled bot)
   * Amazon AWS Secret Access Key   (for voice enabled bot)
   * Google Application Credentials (for image interrogation)
   
   There are also other settings you can play with. Like ChatGPT default temperature.
   
   Don't forget to update the folder to the folder you have installed (async_bot_path)
   
   If you want to use Automatic1111, also update the parameters there. (like the IP / port of the program, and also the path and shortcut to starting Automatic1111 Stable-Diffusion-Webui

7. **Install Telegram API Certificate**
   
   Go to webpage https://core.telegram.org/bots
   If you are using Chrome:
      Press the Lock key near the web-page
      
      Press the "Connection is Secure"
      
      ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/8e0bab0b-b41b-49b0-bcd3-bc558d55eb20)

      Press the "Certificate is Valid" and go to Details:
      
      ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/1b5f7e1e-2306-41b4-9a89-8f12378fd526)

      You need to export the key (certificate)
      
      ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/a1982392-2bd0-4ae0-a404-7bbf4ddd7988)

      And then, install the certificate:
      
      ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/95aeb2e2-4601-4f35-b5db-aa9134dbb36d)

      Select Current User (for only you on the computer) or Local Machine (for all users)
      
      and place all certificates on the "Trusted Root Certification Authorities":
      
      ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/a1fd308b-ec15-4f64-9251-ff46f4587841)

      Press Finish!
      
8. **Install Original FFMPEG**

   Download the FFPMEG from the original web address:
   
   https://www.ffmpeg.org/download.html
   
   Once downloaded, extract the zip files into a folder (I prefer C:\Program Files\ffmpeg-6.0-essentials_build)
   
   Add the bin directory to your PATH environment form the windows "Edit the System Environment":
   
   ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/0fba9bbe-45b5-4442-9169-0252e88f94f3)

   Select "Environment Variables" on the bottom of the page:
   
   ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/a0de9f30-aadf-487f-b498-bfd3e7331cd7)

   Find Path in the System Variblaes and click Edit:
   
   ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/f2f84d6b-8a28-40fd-a79f-4d125753d82a)

   Press "New" on the right:
   
   ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/fd6d6e6c-863c-4d40-8acd-364c71d66b3a)

   **And insert your path (don't forget the last part /bin)**
   
   ![image](https://github.com/alperinugur/FunnyBot-ChatGPT-Telegram/assets/30839536/f652fb92-307e-4019-8629-327000e20e76)

   Click OK - OK - OK 
   
   
9. **Run the bot**
   Now you can run the bot:
   ```bash
   C:
   CD AI
   CD telegram_bot
   .\venv\Scripts\activate   # For Windows   
   python TeleBot_Async.py
   
  or faster:
   Just run the Batch file named: AsyncBot.bat by double clicking its icon.

10.**ACTIVATING BOT LATER**

   
## OPTIONAL FEATURES
   
   Optional features are optional, but they are the real fun. If you can, I advise to use them!
   
**To use image generation**

   If you want to use image generation (requires NVIDIA graphics card with min 6GB memory),
   please follow the instructions to set-up on your local computer from original page:
   
   https://github.com/AUTOMATIC1111/stable-diffusion-webui
   

**To use image interrogation**

   This code uses Microsoft Vision to interrogate images. 
   If you want to use this, you have to create an account to use Microsoft Vision.
   
   The authentication JSON file created there will have a name like 'mybots-325452-ad7e3ab28d2a.json'
   Save this file in the _main subfolder, and change the placement in the _main/params file.

   If you are familiar with Google Cloud services, use the following link to create a Service Account:7
   
   https://console.cloud.google.com/iam-admin/serviceaccounts/details/
   
  
