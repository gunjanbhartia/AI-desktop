import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import wikipedia
import pyjokes
import requests
import smtplib
import time
import asyncio

# Initialize speech recognition
listener = sr.Recognizer()

# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Replace with the provided OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = 'your_openweathermap_api_key'

# Replace with the provided weather forecast URL
WEATHER_FORECAST_URL = 'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={de61ffac5b63b61b533e6bb7a696f158}'

# Replace with your email and password for sending emails
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_email_password'

# Initialize a dictionary to store reminders
reminders = {}

# Add website URLs
WEBSITE_URLS = {
    'youtube': 'https://www.youtube.com',
    'flipkart': 'https://www.flipkart.com',
    'nalcoindia': 'https://www.nalcoindia.com',
}

# Define user profiles (you can expand this with more profiles)
USER_PROFILES = {
    'user1': {
        'email': 'user1@gmail.com',
        'name': 'User 1',
    },
    'user2': {
        'email': 'user2@gmail.com',
        'name': 'User 2',
    },
}

# Add more natural language understanding capabilities and commands
NLU_COMMANDS = {
    'greet': ['hello', 'hi', 'hey'],
    'goodbye': ['goodbye', 'bye', 'see you'],
    'introduce': ['tell me about yourself', 'who are you'],
    'help': ['help', 'what can you do', 'assist me'],
    'thank': ['thank you', 'thanks'],
    'open': ['open'],
    'search': ['search for'],
    'play_music': ['play music', 'play a song'],
}

async def talk(text):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: engine.say(text))
    await loop.run_in_executor(None, engine.runAndWait)

# Function to recognize user profile from voice
async def recognize_user_profile():
    try:
        with sr.Microphone() as source:
            print('Please say your name...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            name = listener.recognize_google(voice).lower()
            for profile, profile_data in USER_PROFILES.items():
                if name == profile_data['name'].lower():
                    return profile
            return None
    except sr.UnknownValueError:
        return None

# Add more commands based on natural language understanding
async def handle_nlu_command(command, user_profile):
    if command in NLU_COMMANDS['greet']:
        await talk(f'Hello, {USER_PROFILES[user_profile]["name"]}!')
    elif command in NLU_COMMANDS['goodbye']:
        await talk('Goodbye!')
        return 'goodbye'
    elif command in NLU_COMMANDS['introduce']:
        await talk('I am your virtual assistant. I can help you with various tasks.')
    elif command in NLU_COMMANDS['help']:
        await talk('You can ask me about the weather, open websites, search the internet, and more. Just tell me what you need.')
    elif command in NLU_COMMANDS['thank']:
        await talk('You are welcome!')
    elif command.startswith(NLU_COMMANDS['open'][0]):
        website = command[len(NLU_COMMANDS['open'][0]):].strip()
        if website in WEBSITE_URLS:
            webbrowser.open(WEBSITE_URLS[website])
        else:
            await talk('I cannot open that website.')
    elif command.startswith(NLU_COMMANDS['search'][0]):
        query = command[len(NLU_COMMANDS['search'][0]):].strip()
        webbrowser.open(f'https://www.google.com/search?q={query}')
    elif command.startswith(NLU_COMMANDS['play_music'][0]):
        await talk('Playing some music for you.')
        # Implement music streaming functionality here.
    return None

async def take_command():
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            command = listener.recognize_google(voice).lower()
            print('You said:', command)
            return command
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
    except sr.RequestError as e:
        print(f"Sorry, there was an error with the request: {e}")

async def run_alexa():
    while True:
        user_profile = await recognize_user_profile()
        if user_profile is None:
            await talk("Sorry, I didn't recognize your profile.")
            break

        await talk(f'Hello, {USER_PROFILES[user_profile]["name"]}! How can I assist you today?')
        while True:
            command = await take_command()
            print(command)

            # Handle NLU commands
            response = await handle_nlu_command(command, user_profile)
            if response == 'goodbye':
                break
            elif response is not None:
                continue

            if 'weather' in command:
                city = command.replace('weather', '').strip()
                await run_weather_command(city)
            elif 'forecast' in command:
                await talk("Please provide the latitude and longitude coordinates for the forecast.")
                try:
                    coordinates = await take_command()
                    await run_forecast_command(coordinates)
                except Exception as e:
                    print(f"Error parsing coordinates: {str(e)}")
                    await talk("Sorry, I couldn't understand the coordinates.")
            elif 'calculate' in command:
                expression = command.replace('calculate', '').strip()
                await calculate(expression)
            elif 'play' in command:
                song = command.replace('play', '')
                await talk('Playing ' + song)
                # Implement music streaming functionality here.
            elif 'time' in command:
                time_now = datetime.datetime.now().strftime('%I:%M %p')
                await talk('Current time is ' + time_now)
            elif 'who the heck is' in command:
                person = command.replace('who the heck is', '')
                info = wikipedia.summary(person, 1)
                print(info)
                await talk(info)
            elif 'date' in command:
                await talk('Sorry, I have a headache')
            elif 'are you single' in command:
                await talk('I am in a relationship with wifi')
            elif 'joke' in command:
                joke = pyjokes.get_joke()
                print(joke)
                await talk(joke)
            elif 'send email' in command:
                await talk("Please provide the recipient's email address.")
                recipient_email = await take_command()
                await talk("What is the subject of the email?")
                email_subject = await take_command()
                await talk("Please dictate the email message.")
                email_message = await take_command()
                await run_email_command(recipient_email, email_subject, email_message)
            elif 'set reminder' in command:
                await talk("Please specify the reminder message.")
                reminder_message = await take_command()
                await talk("In how many minutes should I remind you?")
                try:
                    time_in_minutes = int(await take_command())
                    await set_reminder(reminder_message, time_in_minutes)
                except ValueError:
                    await talk("Sorry, I couldn't understand the time.")
            elif 'check reminders' in command:
                await check_reminders()
            elif 'nalco india' in command:
                await talk("Here is the website for NALCO INDIA.")
                await open_website(WEBSITE_URLS['nalcoindia'])
            elif 'news' in command:
                await talk("Sure, here are some headlines.")
                await open_website('https://news.google.com/')
            elif 'sports news' in command:
                await talk("Sure, here are the latest sports headlines.")
                await open_website('https://www.espn.com/')
            elif 'technology news' in command:
                await talk("Here are the top technology news stories.")
                await open_website('https://www.techcrunch.com/')
            elif 'stock market' in command:
                await talk("Here is the latest stock market information.")
                await open_website('https://www.cnbc.com/stock-market/')
            elif 'tell me a joke' in command:
                joke = pyjokes.get_joke()
                await talk(joke)
            elif 'stop' in command:
                await talk("Goodbye!")
                break
            else:
                await talk('Please say the command again.')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_alexa())
