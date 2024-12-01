import tkinter as tk
from tkinter import messagebox
from assistant import start_thread_for_assistant  # Import the threaded assistant call

# Function to process the prompt and update the GUI with the result
def process_and_display_response(prompt):
    def display_response(response):
        # Add a gap between conversations for better readability
        response_text.insert(tk.END, "\n\n")  # Gap between every conversation
        response_text.insert(tk.END, f"Assistant: {response}\n", 'assistant')
        response_text.yview(tk.END)  # Scroll to the bottom
        stop_loading_indicator()  # Stop loading indicator once response is displayed

    # Show loading indicator
    start_loading_indicator()
    
    # Call the assistant's function in a new thread to prevent blocking
    start_thread_for_assistant(prompt, display_response)

# Function to show the loading indicator
def start_loading_indicator():
    loading_label.pack(pady=10)
    prompt_entry.config(state=tk.DISABLED)  # Disable the input field to avoid multiple submissions

# Function to stop the loading indicator
def stop_loading_indicator():
    loading_label.pack_forget()  # Hide the loading label
    prompt_entry.config(state=tk.NORMAL)  # Enable the input field again

# Function to handle the Enter key to trigger the submit action
def on_submit(event=None):
    user_prompt = prompt_entry.get()
    if user_prompt:
        # Display the user's prompt in the conversation area
        response_text.insert(tk.END, f"\nYou: {user_prompt}\n", 'user')
        process_and_display_response(user_prompt)
        prompt_entry.delete(0, tk.END)  # Clear the input field after submission
    else:
        messagebox.showwarning("Input Error", "Please enter a prompt.")

# GUI Setup
root = tk.Tk()
root.title("Voice Assistant")
root.geometry("800x600")  # Increase the size of the window for better fit
root.resizable(True, True)  # Allow resizing of the window
root.config(bg="black")  # Set black background color

# Conversation window
conversation_frame = tk.Frame(root, bg="black")
conversation_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Scrollbar for the conversation window
scrollbar = tk.Scrollbar(conversation_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

response_text = tk.Text(conversation_frame, height=25, width=80, font=('Helvetica', 12), wrap=tk.WORD, yscrollcommand=scrollbar.set, bg="black", fg="white")
response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=response_text.yview)

# Adding tags for color coding
response_text.tag_config('user', foreground='blue')  # Color for user input
response_text.tag_config('assistant', foreground='green')  # Color for assistant response

# Loading indicator (label)
loading_label = tk.Label(root, text="Processing... Please wait.", font=('Helvetica', 12, 'italic'), fg='blue', bg="black")

# User input field
prompt_label = tk.Label(root, text="Enter your prompt:", font=('Helvetica', 12), bg="black", fg="white")
prompt_label.pack(pady=10)

# Enlarging the input field
prompt_entry = tk.Entry(root, width=60, font=('Helvetica', 16), bg="black", fg="white", insertbackground="white")
prompt_entry.pack(pady=10)
prompt_entry.bind("<Return>", on_submit)  # Bind Enter key to submit action

# Run the GUI
root.mainloop()
