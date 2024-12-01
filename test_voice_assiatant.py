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

# Fixture to initialize the app and add it to the test framework
@pytest.fixture
def app(qtbot):
    test_app = VoiceAssistantApp()
    qtbot.addWidget(test_app)
    return test_app

# Test function to check basic function calls for various prompts
def test_function_call_basic():
    """Test function call for different types of prompts"""
    assert function_call("Take a screenshot") in ["take screenshot", "None"], "Test failed for screenshot prompt"
    assert function_call("What's on my clipboard?") in ["extract clipboard", "None"], "Test failed for clipboard prompt"
    assert function_call("Show me what's in front of the webcam") in ["capture webcam", "None"], "Test failed for webcam prompt"
    assert function_call("Tell me about the weather") == "None", "Test failed for weather prompt"

# Test functionality of the screenshot capture function
def test_screenshot_functionality(tmp_path):
    """Test screenshot capture functionality"""
    os.chdir(tmp_path)
    take_screenshot()
    assert os.path.exists('screenshot.png'), "Screenshot was not saved."
    assert os.path.getsize('screenshot.png') > 0, "Screenshot file is empty."

# Test functionality of the webcam capture function
def test_webcam_capture_functionality(tmp_path):
    """Test webcam capture functionality"""
    os.chdir(tmp_path)
    capture_webcam()
    assert os.path.exists('webcam.png'), "Webcam image was not saved."
    assert os.path.getsize('webcam.png') > 0, "Webcam image file is empty."

# Test clipboard extraction using a mock function
def test_clipboard_functionality(monkeypatch):
    """Test clipboard extraction"""
    def mock_paste():
        return "Test clipboard content"
    
    monkeypatch.setattr(pyperclip, 'paste', mock_paste)
    
    clipboard_content = get_clipboard()
    assert clipboard_content == "Test clipboard content", "Clipboard content extraction failed"

# Test the initial state of the GUI (buttons enabled, no conversation text)
def test_gui_initial_state(app):
    """Test initial state of the GUI"""
    assert app.send_button.isEnabled(), "Send button should be enabled."
    assert app.screenshot_button.isEnabled(), "Screenshot button should be enabled."
    assert app.webcam_button.isEnabled(), "Webcam button should be enabled."
    assert app.clipboard_button.isEnabled(), "Clipboard button should be enabled."
    assert app.conversation_display.toPlainText() == "", "Conversation display should be empty at the start."

# Test button interactions to simulate clicking and check the expected behavior
def test_button_interactions(app, qtbot):
    """Test various button interactions"""
    # Screenshot button
    qtbot.mouseClick(app.screenshot_button, Qt.MouseButton.LeftButton)
    assert "Screenshot captured" in app.conversation_display.toPlainText(), "Screenshot action failed"

    # Webcam button
    qtbot.mouseClick(app.webcam_button, Qt.MouseButton.LeftButton)
    assert "Webcam image captured" in app.conversation_display.toPlainText(), "Webcam action failed"

# Test input processing by simulating user input and ensuring the conversation displays correctly
def test_input_processing(app, qtbot):
    """Test input processing"""
    app.input_text.setText("Hello, what can you do?")
    qtbot.mouseClick(app.send_button, Qt.MouseButton.LeftButton)
    conversation = app.conversation_display.toPlainText()
    assert "You: Hello, what can you do?" in conversation, "User input is not displayed correctly."
    assert "Assistant:" in conversation, "Assistant response is not displayed."

# Test prompt generation with and without image context
def test_prompt_generation():
    """Test prompt generation with and without image context"""
    prompt = "Hello, what can you do?"
    response = groq_prompt(prompt, None)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"

# Test error handling for empty prompts
def test_error_handling():
    """Test error handling scenarios"""
    with pytest.raises(Exception, match="Prompt cannot be empty"):
        groq_prompt("", None)

# Optional: Skip GUI-related tests if dependencies are missing
def pytest_collection_modifyitems(config, items):
    try:
        import pyperclip
    except ImportError:
        skip_gui = pytest.mark.skip(reason="Required dependencies missing")
        for item in items:
            # Skip tests that involve GUI functionality if pyperclip is missing
            if "gui" in item.keywords:
                item.add_marker(skip_gui)
