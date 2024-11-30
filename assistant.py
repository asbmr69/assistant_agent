import os
from groq import Groq
from PIL import ImageGrab, Image
import cv2
import pyperclip
import google.generativeai as genai

groq_client = Groq(api_key = 'your api key')
genai.configure(api_key = 'your api key')
web_cam = cv2.VideoCapture(0)

sys_message = (
    'You are a multi-modal AI voice assistant. Your user may or may not have attached a photo for context'
    '(either  a screenshot or a webcam photo). Any photo has alerady been processed into a highly detailed text prompt that will be attatched to their transcribed voice prompt.'
    'Generate the most useful and factual response possible, carefully considering all previous generated text in your response before'
    'adding new tokens to the response. Do not expect or request images, just use the context if added.'
    'Use all the context of this conversation so your response is relevent to the conversation. Make your responses clear and avoiding any verbosity'
)
convo = [{'role': 'system', 'content': sys_message}]
generation_config = {
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1,
    'max_output_tokens': 2048,
}
safety_settings = [{
    'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
    'threshold': 'BLOCK_NONE'
},
    {
    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
    'threshold': 'BLOCK_NONE'
},
    {
    'category': 'HARM_CATEGORY_HARASSMENT',
    'threshold': 'BLOCK_NONE'
},
    {
    'category': 'HARM_CATEGORY_HATE_SPEECH',
    'threshold': 'BLOCK_NONE'
},
]

model = genai.GenerativeModel('gemini-1.5-flash-latest',
    generation_config=generation_config,
    safety_settings=safety_settings)    


def groq_prompt(prompt, img_context):
    if img_context:
        prompt = f'USER PROMPT: {prompt}\n\n    IMAGE CONTEXT: {img_context}'
    convo.append({'role': 'user', 'content': prompt})

    chat_completion = groq_client.chat.completions.create(messages=convo,model='llama3-70b-8192')
    response = chat_completion.choices[0].message
    convo.append(response)

    return response.content

def function_call(prompt):
    sys_message = ('You are an AI function calling model. You will determine whether extracting the users clipboard content,'
    'taking a screenshot, capturing the webcam or calling no functions is best for a voice assistant to repond '
    'to take the users prompt. The webcam can be assumed to be a normal laptop webcam facing user. '
    'You will respond with only one selection from this list: ["extract clipboard", "take screenshot", "capture webcam", "None"] \n'
    'Do not respond with anything but most logical selection from that list with no explanation. Format the function call name exactly as I listed.'
    )
    function_convo = [{'role': 'system', 'content': sys_message}, 
                      {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo,model="llama3-70b-8192")
    response = chat_completion.choices[0].message
    return response.content

def take_screenshot():
    path = 'screenshot.png'
    screenshot = ImageGrab.grab()
    rgb_screenshot = screenshot.convert('RGB')
    rgb_screenshot.save(path, quality=15)

def capture_webcam():
    if not web_cam.isOpened():
        print('Error: Could not open webcam')
        exit()
    
    path = 'webcam.png'
    ret, frame = web_cam.read()
    cv2.imwrite(path, frame)
def get_clipboard():
    clipboard_content = pyperclip.paste()
    if isinstance(clipboard_content, str):
        return clipboard_content
    else:
        print('Error: Clipboard content is not a string')
        return None

def vision_prompt(prompt, photo_path):
    img = Image.open(photo_path)
    prompt = (
        'You are the vision analysis AI that provides semantic meaning from images to provide context'
        'to send to another AI that will create a response to the user. Do not respond as the AI assistant' 
        'to the user. Insted take the user prompt input and try to extract all meaning from the photo' 
        f'assistant who will respond to the user. \nUSER PROMPT: {prompt}' 
          )
    response = model.generate_content([prompt, img])
    return response.text
#prompt = input('USER: ')
while True:
    prompt = input('USER: ')
    call = function_call(prompt)
    if 'take screenshot' in call:
        print('Taking screenshot...')
        take_screenshot()
        visual_context = vision_prompt(prompt, photo_path='screenshot.png')
    elif 'capture webcam' in call:
        print('Capturing webcam...')
        capture_webcam()
        visual_context = vision_prompt(prompt, photo_path='webcam.png')
    elif 'extract clipboard' in call:
        print('Extracting clipboard...')
        clipboard_content = get_clipboard()
        prompt = f'{prompt}\n\n CLIPBOARD CONTENT: {clipboard_content}'
        visual_context = None
    else:
        visual_context = None
    response = groq_prompt(prompt=prompt, img_context=visual_context)
    print(response)
