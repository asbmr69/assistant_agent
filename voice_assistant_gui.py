import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QLabel)
from PyQt6.QtCore import Qt

# Import the existing application logic
from assistant import (
    function_call, 
    groq_prompt, 
    take_screenshot, 
    capture_webcam, 
    get_clipboard, 
    vision_prompt
)

class VoiceAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Voice Assistant')
        self.setGeometry(100, 100, 600, 500)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Conversation display
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        main_layout.addWidget(self.conversation_display)
        
        # Input layout
        input_layout = QHBoxLayout()
        
        # Input text box
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(100)
        input_layout.addWidget(self.input_text)
        
        # Send button
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.process_input)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Screenshot button
        self.screenshot_button = QPushButton('Screenshot')
        self.screenshot_button.clicked.connect(self.take_screenshot)
        button_layout.addWidget(self.screenshot_button)
        
        # Webcam button
        self.webcam_button = QPushButton('Webcam')
        self.webcam_button.clicked.connect(self.capture_webcam)
        button_layout.addWidget(self.webcam_button)
        
        # Clipboard button
        self.clipboard_button = QPushButton('Clipboard')
        self.clipboard_button.clicked.connect(self.extract_clipboard)
        button_layout.addWidget(self.clipboard_button)
        
        main_layout.addLayout(button_layout)
        
        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def process_input(self):
        # Get the input text
        prompt = self.input_text.toPlainText().strip()
        if not prompt:
            return
        
        # Clear input text box
        self.input_text.clear()
        
        # Display user input
        self.conversation_display.append(f"You: {prompt}")
        
        # Process the input
        call = function_call(prompt)
        
        visual_context = None
        if 'take screenshot' in call:
            self.conversation_display.append("Taking screenshot...")
            take_screenshot()
            visual_context = vision_prompt(prompt, photo_path='screenshot.png')
        elif 'capture webcam' in call:
            self.conversation_display.append("Capturing webcam...")
            capture_webcam()
            visual_context = vision_prompt(prompt, photo_path='webcam.png')
        elif 'extract clipboard' in call:
            self.conversation_display.append("Extracting clipboard...")
            clipboard_content = get_clipboard()
            prompt = f'{prompt}\n\n CLIPBOARD CONTENT: {clipboard_content}'
        
        # Get response from AI
        response = groq_prompt(prompt=prompt, img_context=visual_context)
        
        # Display response
        self.conversation_display.append(f"Assistant: {response}\n")
        
    def take_screenshot(self):
        take_screenshot()
        self.conversation_display.append("Screenshot captured: screenshot.png")
        
    def capture_webcam(self):
        capture_webcam()
        self.conversation_display.append("Webcam image captured: webcam.png")
        
    def extract_clipboard(self):
        clipboard_content = get_clipboard()
        self.conversation_display.append(f"Clipboard content: {clipboard_content}")

def main():
    app = QApplication(sys.argv)
    ex = VoiceAssistantApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()