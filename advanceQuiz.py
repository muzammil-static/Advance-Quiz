import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import random
from collections import deque

class QuizManager:
    def __init__(self, questions):
        self.questions = random.sample(questions, len(questions))  # Randomize questions
        self.index = 0
        self.skipped_questions = deque()
        self.attempted_questions = deque()
        self.score = 0
        self.right_answers = 0
        self.wrong_answers = 0
        self.reviewing_skipped = False
        self.current_skipped_question = None

    def current_question(self):
        if self.reviewing_skipped:
            return self.current_skipped_question
        if self.index < len(self.questions):
            return self.questions[self.index]
        return None

    def next_question(self, answer=None):
        if self.reviewing_skipped:
            return self.handle_skipped_answer(answer)

        if self.index < len(self.questions):
            current = self.questions[self.index]
            if answer is not None:
                self.calculate_score(current, answer)
                self.attempted_questions.append(current)  # Enqueue to attempted
            self.index += 1
        return self.current_question()

    def skip_question(self):
        if not self.reviewing_skipped and self.index < len(self.questions):
            self.skipped_questions.appendleft(self.questions[self.index])  # Add skipped question to front of queue
            self.index += 1
        return self.current_question()

    def review_skipped_question(self):
        if self.skipped_questions:
            self.reviewing_skipped = True
            self.current_skipped_question = self.skipped_questions[0]  # Just peek the front of the queue
            return self.current_skipped_question
        return None

    def handle_skipped_answer(self, answer):
        if self.current_skipped_question:
            self.calculate_score(self.current_skipped_question, answer)
            self.attempted_questions.append(self.current_skipped_question)  # Enqueue to attempted
            self.skipped_questions.popleft()  # Dequeue from skipped
            self.current_skipped_question = None
        self.reviewing_skipped = False
        return self.review_skipped_question()

    def calculate_score(self, question, answer):
        if answer.lower() == question['correct']:
            self.score += 5
            self.right_answers += 1
        else:
            self.score -= 1
            self.wrong_answers += 1

    def restart(self):
        self.index = 0
        self.skipped_questions.clear()
        self.attempted_questions.clear()
        self.score = 0
        self.right_answers = 0
        self.wrong_answers = 0
        self.reviewing_skipped = False
        self.current_skipped_question = None
        self.questions = random.sample(self.questions, len(self.questions))  # Reshuffle questions


def start_quiz(quiz_manager, question_label, attempted_listbox, skipped_listbox, yes_button, no_button, skip_button, review_button, restart_button, end_button, score_label):
    def update_question():
        question = quiz_manager.current_question()
        if question:
            question_label.config(text=f"Q: {question['text']}")
        else:
            question_label.config(text="No more questions. Review or End the quiz.")
            yes_button["state"] = "disabled"
            no_button["state"] = "disabled"
            skip_button["state"] = "disabled"

    def handle_answer(answer):
        quiz_manager.next_question(answer)
        update_question()
        refresh_attempted_list()
        refresh_skipped_list()
        score_label.config(text=f"Score: {quiz_manager.score}")

    def handle_skip():
        quiz_manager.skip_question()
        update_question()
        refresh_skipped_list()

    def handle_review():
        question = quiz_manager.review_skipped_question()
        if question:
            question_label.config(text=f"Review: {question['text']}")
            yes_button["state"] = "normal"
            no_button["state"] = "normal"
        else:
            question_label.config(text="No skipped questions to review.")
            yes_button["state"] = "disabled"
            no_button["state"] = "disabled"
        refresh_skipped_list()

    def handle_end():
        # Display final summary
        question_label.config(
            text=f"Quiz Completed!\nTotal Score: {quiz_manager.score}\nRight Answers: {quiz_manager.right_answers}\nWrong Answers: {quiz_manager.wrong_answers}\nSkipped Questions: {len(quiz_manager.skipped_questions)}"
        )
        yes_button["state"] = "disabled"
        no_button["state"] = "disabled"
        skip_button["state"] = "disabled"
        review_button["state"] = "disabled"
        end_button["state"] = "disabled"

    def handle_restart():
        quiz_manager.restart()
        update_question()
        refresh_attempted_list()
        refresh_skipped_list()
        yes_button["state"] = "normal"
        no_button["state"] = "normal"
        skip_button["state"] = "normal"
        review_button["state"] = "disabled"  # Disable the Review Skipped button initially
        end_button["state"] = "normal"
        score_label.config(text=f"Score: {quiz_manager.score}")

    def refresh_attempted_list():
        attempted_listbox.delete(0, tk.END)
        for q in quiz_manager.attempted_questions:
            attempted_listbox.insert(tk.END, q['text'])

    def refresh_skipped_list():
        skipped_listbox.delete(0, tk.END)
        for q in quiz_manager.skipped_questions:
            skipped_listbox.insert(tk.END, q['text'])
        
        # Enable or disable the review button based on whether there are skipped questions
        if quiz_manager.skipped_questions:
            review_button["state"] = "normal"
        else:
            review_button["state"] = "disabled"

    # Initialize the quiz
    handle_restart()

    # Bind button commands
    yes_button.config(command=lambda: handle_answer("yes"))
    no_button.config(command=lambda: handle_answer("no"))
    skip_button.config(command=handle_skip)
    review_button.config(command=handle_review)
    end_button.config(command=handle_end)
    restart_button.config(command=handle_restart)

def main():
    # Example Questions
    questions = [
        {"text": "Can a queue be implemented using a linked list?", "correct": "yes"},
        {"text": "Is it possible to perform a binary search on an unsorted array?", "correct": "no"},
        {"text": "Can a doubly linked list be traversed in both directions?", "correct": "yes"},
        {"text": "Is a stack a FIFO (First In First Out) data structure?", "correct": "no"},
        {"text": "Is the time complexity of accessing an element in an array O(1)?", "correct": "yes"},
        {"text": "Can you implement a priority queue using a binary heap?", "correct": "yes"},
        {"text": "Can a tree have more than one root node?", "correct": "no"},
        {"text": "Does bubble sort have a time complexity of O(n log n)?", "correct": "no"},
    ]

    # Initialize Quiz Manager
    quiz_manager = QuizManager(questions)

    # Setup GUI
    root = tk.Tk()
    root.title("Advanced Quiz System")
    root.geometry("800x400")
    root.config(bg="#f8f8f8")

    # Load and set the background image
    try:
        bg_image = Image.open("Final11img.png")  # Replace with your image path
        bg_image = bg_image.resize((800, 400))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo, bg="#f8f8f8")  # Match the background color
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        bg_label.lower()  # Send to the back of all widgets
    except FileNotFoundError:
        print("Background image not found. Proceeding with background color only.")

    # Quiz Question Section
    question_frame = tk.Frame(root, bg="#ECECEC", relief=tk.RAISED, borderwidth=2)
    question_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

    question_label = tk.Label(question_frame, text="", font=("Arial", 16, "bold"), bg="#ECECEC", fg="#116466", wraplength=700, justify="center")
    question_label.pack(pady=20)

    # Attempted Questions Section
    attempted_frame = tk.Frame(root, bg="#ECECEC", relief=tk.RAISED, borderwidth=2)
    attempted_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    attempted_label = tk.Label(attempted_frame, text="Attempted Questions (Queue)", font=("Arial", 14, "italic"), bg="#ECECEC", fg="#0B315E")
    attempted_label.pack(pady=10)

    attempted_listbox = tk.Listbox(attempted_frame, height=15, font=("Arial", 12), bg="#FFFFFC", fg="#0B315E")
    attempted_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Skipped Questions Section
    skipped_frame = tk.Frame(root, bg="#ECECEC", relief=tk.RAISED, borderwidth=2)
    skipped_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    skipped_label = tk.Label(skipped_frame, text="Skipped Questions (Queue)", font=("Arial", 14, "italic"), bg="#ECECEC", fg="#8E3B46")
    skipped_label.pack(pady=10)

    skipped_listbox = tk.Listbox(skipped_frame, height=15, font=("Arial", 12), bg="#FFFFFC", fg="#8E3B46")
    skipped_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Control Buttons
    bottom_frame = tk.Frame(root, bg="#f8f8f8")  # Parent frame for buttons and score
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=30)

    control_frame = tk.Frame(bottom_frame, bg="#f8f8f8")  # Buttons container
    control_frame.pack(side=tk.TOP, pady=10)

    yes_button = tk.Button(control_frame, text="Yes", bg="#04AA6D", fg="#ffffff", font=("Arial", 12))  # Green
    yes_button.pack(side=tk.LEFT, padx=5, pady=5)

    no_button = tk.Button(control_frame, text="No", bg="#f44336", fg="#ffffff", font=("Arial", 12))   # Red
    no_button.pack(side=tk.LEFT, padx=5, pady=5)

    skip_button = tk.Button(control_frame, text="Skip Question", bg="#FFD700", fg="#000000", font=("Arial", 12))  # Orange
    skip_button.pack(side=tk.LEFT, padx=5, pady=5)

    review_button = tk.Button(control_frame, text="Review Skipped", bg="#0B315E", fg="#ffffff", font=("Arial", 12))  # Light Blue
    review_button.pack(side=tk.LEFT, padx=5, pady=5)

    end_button = tk.Button(control_frame, text="End Quiz", bg="#008080", fg="#ffffff", font=("Arial", 12))   # Purple
    end_button.pack(side=tk.LEFT, padx=5, pady=5)

    restart_button = tk.Button(control_frame, text="Restart Quiz", bg="#CB4154", fg="#FFFFFF", font=("Arial", 12))  # Yellow
    restart_button.pack(side=tk.LEFT, padx=5, pady=5)

    score_label = tk.Label(root, text="Score: 0", font=("Arial", 18, "bold"), bg="#000000", fg="#ffffff")
    score_label.pack(side=tk.BOTTOM, pady=5)

    # Start the Quiz
    start_quiz(quiz_manager, question_label, attempted_listbox, skipped_listbox,
               yes_button, no_button, skip_button, review_button, restart_button, end_button, score_label)

    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    main()
