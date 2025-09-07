import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ================= DATABASE SETUP =================
def setup_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root"
    )
    myc = mydb.cursor()

    # Create database and table
    myc.execute("DROP DATABASE IF EXISTS qna")  # ensures fresh start
    myc.execute("CREATE DATABASE qna")
    myc.execute("USE qna")

    myc.execute("""
        CREATE TABLE quiz (
            qno INT AUTO_INCREMENT PRIMARY KEY,
            topic VARCHAR(100),
            subtopic VARCHAR(100),
            question VARCHAR(255),
            option_a VARCHAR(100),
            option_b VARCHAR(100),
            option_c VARCHAR(100),
            option_d VARCHAR(100),
            correct_answer CHAR(1)
        )
    """)

    # Insert questions
    quiz_data = [
        # Physics
        ("Physics", "Mechanics", "What is the SI unit of force?",
         "A. Newton", "B. Joule", "C. Watt", "D. Pascal", "A"),
        ("Physics", "Optics", "Which mirror is used in car rear-view mirrors?",
         "A. Concave", "B. Convex", "C. Plane", "D. Cylindrical", "B"),
        ("Physics", "Electricity", "What is the unit of electric current?",
         "A. Coulomb", "B. Ohm", "C. Ampere", "D. Watt", "C"),

        # Mathematics
        ("Mathematics", "Algebra", "What is (a+b)² ?",
         "A. a²+b²", "B. a²+b²+2ab", "C. a²−b²", "D. 2a²+2b²", "B"),
        ("Mathematics", "Geometry", "How many degrees are there in a right angle?",
         "A. 45", "B. 90", "C. 180", "D. 360", "B"),
        ("Mathematics", "Trigonometry", "What is sin(90°)?",
         "A. 0", "B. 1", "C. -1", "D. √2/2", "B"),

        # Gen AI
        ("Gen AI", "Basics", "What does 'AI' stand for?",
         "A. Automated Input", "B. Artificial Intelligence", "C. Advanced Integration", "D. Automated Internet", "B"),
        ("Gen AI", "ML", "Which of the following is a supervised learning algorithm?",
         "A. K-Means Clustering", "B. Linear Regression", "C. PCA", "D. DBSCAN", "B"),
        ("Gen AI", "Applications", "Which AI model is used for text generation?",
         "A. CNN", "B. RNN", "C. GAN", "D. GPT", "D"),
        ("Gen AI", "Ethics", "Which is a key risk of AI?",
         "A. Faster computation", "B. Job automation", "C. Increased accuracy", "D. Data privacy issues", "D"),
    ]

    myc.executemany("""
        INSERT INTO quiz (topic, subtopic, question, option_a, option_b, option_c, option_d, correct_answer)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, quiz_data)

    mydb.commit()
    myc.close()
    mydb.close()


# ================= QUIZ APP (TKINTER) =================
class QuizApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Quiz App")
        self.root.geometry("750x550")
        self.root.config(bg="#eaf4fc")

        # Connect to DB
        self.mydb = mysql.connector.connect(
            host="localhost", user="root", passwd="root", database="qna"
        )
        self.myc = self.mydb.cursor(dictionary=True)
        self.myc.execute("SELECT * FROM quiz")
        self.questions = self.myc.fetchall()

        # Score tracking
        self.index = 0
        self.score_subject = {}
        self.attempt_subject = {}
        self.score_subtopic = {}
        self.attempt_subtopic = {}

        # Title Banner
        title = tk.Label(root, text="📘 Knowledge Quiz",
                         font=("Arial", 24, "bold"), bg="#4a90e2", fg="white", pady=10)
        title.pack(fill="x")

        # Question Frame
        self.card = tk.Frame(root, bg="white", bd=2, relief="groove")
        self.card.place(relx=0.5, rely=0.45, anchor="center", width=700, height=300)

        self.q_label = tk.Label(self.card, text="", font=("Arial", 16, "bold"),
                                wraplength=650, bg="white", justify="left")
        self.q_label.pack(pady=20)

        self.var = tk.StringVar()

        self.opt_a = tk.Radiobutton(self.card, text="", variable=self.var, value="A",
                                    font=("Arial", 14), anchor="w", bg="white")
        self.opt_a.pack(fill="x", padx=50)

        self.opt_b = tk.Radiobutton(self.card, text="", variable=self.var, value="B",
                                    font=("Arial", 14), anchor="w", bg="white")
        self.opt_b.pack(fill="x", padx=50)

        self.opt_c = tk.Radiobutton(self.card, text="", variable=self.var, value="C",
                                    font=("Arial", 14), anchor="w", bg="white")
        self.opt_c.pack(fill="x", padx=50)

        self.opt_d = tk.Radiobutton(self.card, text="", variable=self.var, value="D",
                                    font=("Arial", 14), anchor="w", bg="white")
        self.opt_d.pack(fill="x", padx=50)

        # Next Button
        self.next_btn = tk.Button(root, text="Next ➡", command=self.next_question,
                                  font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", relief="raised")
        self.next_btn.place(relx=0.5, rely=0.88, anchor="center", width=200, height=40)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress.place(relx=0.5, rely=0.97, anchor="center")
        self.progress["maximum"] = len(self.questions)

        self.load_question()

    def load_question(self):
        if self.index < len(self.questions):
            q = self.questions[self.index]
            self.q_label.config(text=f"Q{q['qno']}. {q['question']}")
            self.opt_a.config(text=q["option_a"])
            self.opt_b.config(text=q["option_b"])
            self.opt_c.config(text=q["option_c"])
            self.opt_d.config(text=q["option_d"])
            self.var.set("")
            self.progress["value"] = self.index
        else:
            self.show_results()

    def next_question(self):
        if self.var.get() == "":
            messagebox.showwarning("⚠ Warning", "Please select an option!")
            return

        q = self.questions[self.index]
        topic, subtopic = q["topic"], q["subtopic"]

        # Init counters
        self.score_subject.setdefault(topic, 0)
        self.attempt_subject.setdefault(topic, 0)
        self.score_subtopic.setdefault((topic, subtopic), 0)
        self.attempt_subtopic.setdefault((topic, subtopic), 0)

        # Check answer
        if self.var.get() == q["correct_answer"]:
            self.score_subject[topic] += 1
            self.score_subtopic[(topic, subtopic)] += 1

        self.attempt_subject[topic] += 1
        self.attempt_subtopic[(topic, subtopic)] += 1

        self.index += 1
        self.load_question()

    def show_results(self):
        result_win = tk.Toplevel(self.root)
        result_win.title("Results")
        result_win.geometry("600x500")
        result_win.config(bg="#f9f9f9")

        tk.Label(result_win, text="📊 Quiz Results", font=("Arial", 20, "bold"),
                 bg="#4a90e2", fg="white", pady=10).pack(fill="x")

        text_box = tk.Text(result_win, font=("Arial", 14), bg="white", wrap="word")
        text_box.pack(fill="both", expand=True, padx=20, pady=20)

        weakest_subject, lowest_acc = None, 101
        for topic in self.score_subject:
            acc = (self.score_subject[topic] / self.attempt_subject[topic]) * 100
            text_box.insert(tk.END, f"\n📘 {topic}: {self.score_subject[topic]}/{self.attempt_subject[topic]} ({acc:.1f}%)\n")

            for (t, sub) in self.score_subtopic:
                if t == topic:
                    sub_acc = (self.score_subtopic[(t, sub)] / self.attempt_subtopic[(t, sub)]) * 100
                    text_box.insert(tk.END, f"   - {sub}: {self.score_subtopic[(t, sub)]}/{self.attempt_subtopic[(t, sub)]} ({sub_acc:.1f}%)\n")

            if acc < lowest_acc:
                lowest_acc = acc
                weakest_subject = topic

        text_box.insert(tk.END, f"\n📉 Weakest Subject: {weakest_subject} ({lowest_acc:.1f}% accuracy)\n")

        tk.Button(result_win, text="Close", command=self.root.destroy,
                  font=("Arial", 14), bg="#e74c3c", fg="white").pack(pady=10)


# ================= MAIN PROGRAM =================
if _name_ == "_main_":
    setup_database()  # Fresh DB setup

    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

    # Drop DB after quiz ends
    mydb = mysql.connector.connect(
        host="localhost", user="root", passwd="root"
    )
    myc = mydb.cursor()
    myc.execute("DROP DATABASE IF EXISTS qna")
    mydb.close()
    print("🗑 Database dropped. Ready for next run.")