import os
from groq import Groq
from PIL import ImageGrab, Image
import cv2
import pyperclip
import google.generativeai as genai
import threading  # Import threading module

groq_client = Groq(api_key='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')
genai.configure(api_key='AIzaSyCsfxwn8e-qmRSkSHe5V6p2XXgGYLMLIB8')
web_cam = cv2.VideoCapture(0)

sys_message = (
    'You are a multi-modal AI voice assistant. Your user may or may not have attached a photo for context'
    '(either a screenshot or a webcam photo). Any photo has already been processed into a highly detailed text prompt that will be attached to their transcribed voice prompt.'
    'Generate the most useful and factual response possible, carefully considering all previous generated text in your response before'
    'adding new tokens to the response. Do not expect or request images, just use the context if added.'
    'Use all the context of this conversation so your response is relevant to the conversation. Make your responses clear and avoid any verbosity.'
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

# def process_prompt(prompt):
#     """Process the user's prompt and determine whether an action (e.g., screenshot, webcam capture) is needed."""
#     call = function_call(prompt)
#     visual_context = None

#     if 'take screenshot' in call:
#         print('Taking screenshot...')
#         take_screenshot()
#         visual_context = vision_prompt(prompt, photo_path='screenshot.png')
#     elif 'capture webcam' in call:
#         print('Capturing webcam...')
#         capture_webcam()
#         visual_context = vision_prompt(prompt, photo_path='webcam.png')
#     elif 'extract clipboard' in call:
#         print('Extracting clipboard...')
#         clipboard_content = get_clipboard()
#         prompt = f'{prompt}\n\n CLIPBOARD CONTENT: {clipboard_content}'
#     response = groq_prompt(prompt=prompt, img_context=visual_context)
#     return response

def process_prompt(prompt, callback):
    """Process the user's prompt and determine whether an action (e.g., screenshot, webcam capture) is needed."""
    call = function_call(prompt)
    visual_context = None
    assistant_response = ""

    if 'take screenshot' in call:
        print('Taking screenshot...')
        take_screenshot()
        visual_context = vision_prompt(prompt, photo_path='screenshot.png')
    elif 'capture webcam' in call:
        print('Capturing webcam...')
        capture_webcam()
        visual_context = vision_prompt(prompt, photo_path='webcam.png')
    elif 'extract clipboard' in call:
        clipboard_content = get_clipboard()
        assistant_response = f"Clipboard Content: {clipboard_content}"  # Add clipboard content to response
        print(f"Clipboard Content: {clipboard_content}")
        prompt = f'{prompt}\n\nCLIPBOARD CONTENT: {clipboard_content}'  # Appending the clipboard content to the prompt
    
    # Call Groq API with the updated prompt (including clipboard content if applicable)
    if not assistant_response:
        assistant_response = groq_prompt(prompt=prompt, img_context=visual_context)

    # Update the GUI with the assistant's response
    callback(assistant_response)

def run_assistant(prompt, callback):
    """Threaded function to process prompt."""
    process_prompt(prompt, callback)

def start_thread_for_assistant(prompt, callback):
    assistant_thread = threading.Thread(target=run_assistant, args=(prompt, callback))
    assistant_thread.start()


def function_call(prompt):
    sys_message = ('You are an AI function calling model. You will determine whether extracting the user\'s clipboard content, '
                   'taking a screenshot, capturing the webcam or calling no functions is best for a voice assistant to respond '
                   'to take the user\'s prompt. The webcam can be assumed to be a normal laptop webcam facing the user. '
                   'You will respond with only one selection from this list: ["extract clipboard", "take screenshot", "capture webcam", "None"] \n'
                   'Do not respond with anything but the most logical selection from that list with no explanation. Format the function call name exactly as I listed.')
    function_convo = [{'role': 'system', 'content': sys_message},
                      {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model="llama3-70b-8192")
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
        'to the user. Instead, take the user prompt input and try to extract all meaning from the photo' 
        f'assistant who will respond to the user. \nUSER PROMPT: {prompt}' 
    )
    response = model.generate_content([prompt, img])
    return response.text

# Function to be called in the GUI for processing
def run_assistant(prompt, callback):
    """Threaded function to process prompt."""
    response = process_prompt(prompt)
    callback(response)

# Example of using threading to call assistant logic in background (for GUI use)
def start_thread_for_assistant(prompt, callback):
    assistant_thread = threading.Thread(target=run_assistant, args=(prompt, callback))
    assistant_thread.start()

# Add the definition of groq_prompt function
def groq_prompt(prompt, img_context):
    if img_context:
        prompt = f'USER PROMPT: {prompt}\n\n    IMAGE CONTEXT: {img_context}'
    convo.append({'role': 'user', 'content': prompt})

    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message
    convo.append(response)

    return response.content

