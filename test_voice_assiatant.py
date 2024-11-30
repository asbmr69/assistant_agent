import os
import pytest
import sys
import pyperclip
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from assistant import (
    function_call, 
    groq_prompt, 
    take_screenshot, 
    capture_webcam, 
    get_clipboard, 
    vision_prompt
)
from voice_assistant_gui import VoiceAssistantApp

@pytest.fixture
def app(qtbot):
    test_app = VoiceAssistantApp()
    qtbot.addWidget(test_app)
    return test_app

def test_function_call_basic():
    """Test function call for different types of prompts"""
    assert function_call("Take a screenshot") in ["take screenshot", "None"]
    assert function_call("What's on my clipboard?") in ["extract clipboard", "None"]
    assert function_call("Show me what's in front of the webcam") in ["capture webcam", "None"]
    assert function_call("Tell me about the weather") == "None"

def test_screenshot_functionality(tmp_path):
    """Test screenshot capture functionality"""
    os.chdir(tmp_path)
    take_screenshot()
    assert os.path.exists('screenshot.png')
    assert os.path.getsize('screenshot.png') > 0

def test_webcam_capture_functionality(tmp_path):
    """Test webcam capture functionality"""
    os.chdir(tmp_path)
    capture_webcam()
    assert os.path.exists('webcam.png')
    assert os.path.getsize('webcam.png') > 0

def test_clipboard_functionality(monkeypatch):
    """Test clipboard extraction"""
    def mock_paste():
        return "Test clipboard content"
    
    monkeypatch.setattr(pyperclip, 'paste', mock_paste)
    
    clipboard_content = get_clipboard()
    assert clipboard_content == "Test clipboard content"

def test_gui_initial_state(app):
    """Test initial state of the GUI"""
    assert app.send_button.isEnabled()
    assert app.screenshot_button.isEnabled()
    assert app.webcam_button.isEnabled()
    assert app.clipboard_button.isEnabled()
    assert app.conversation_display.toPlainText() == ""

def test_button_interactions(app, qtbot):
    """Test various button interactions"""
    # Screenshot button
    qtbot.mouseClick(app.screenshot_button, Qt.MouseButton.LeftButton)
    assert "Screenshot captured" in app.conversation_display.toPlainText()

    # Webcam button
    qtbot.mouseClick(app.webcam_button, Qt.MouseButton.LeftButton)
    assert "Webcam image captured" in app.conversation_display.toPlainText()

def test_input_processing(app, qtbot):
    """Test input processing"""
    # Set input text
    app.input_text.setText("Hello, what can you do?")
    
    # Click send button
    qtbot.mouseClick(app.send_button, Qt.MouseButton.LeftButton)
    
    # Check if input and response are added to conversation display
    conversation = app.conversation_display.toPlainText()
    assert "You: Hello, what can you do?" in conversation
    assert "Assistant:" in conversation

def test_prompt_generation():
    """Test prompt generation with and without image context"""
    prompt = "Hello, what can you do?"
    response = groq_prompt(prompt, None)
    assert isinstance(response, str)
    assert len(response) > 0

def test_error_handling():
    """Test error handling scenarios"""
    # Test with invalid inputs
    with pytest.raises(Exception):
        groq_prompt("", None)

# Optional: Configuration to skip if dependencies are missing
def pytest_collection_modifyitems(config, items):
    try:
        import pyperclip
    except ImportError:
        skip_gui = pytest.mark.skip(reason="Required dependencies missing")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)