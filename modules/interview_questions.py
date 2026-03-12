class InterviewQuestionGenerator:
    """Generates interview questions based on skills and role."""
    
    def __init__(self):
        self.question_bank = {
            "machine learning": [
                "Explain the bias-variance tradeoff.",
                "How do you handle imbalanced datasets?",
                "What is cross-validation and why is it important?"
            ],
            "deep learning": [
                "What is the vanishing gradient problem and how do you solve it?",
                "Explain the difference between Convolutional and Recurrent Neural Networks."
            ],
            "tensorflow": [
                "What is a tf.Tensor and how is it different from a NumPy array?",
                "How would you deploy a TensorFlow model to production?"
            ],
            "python": [
                "What are the differences between lists and tuples?",
                "Explain decorators and generators in Python."
            ],
            "docker": [
                "What is the difference between an Image and a Container?",
                "Explain the use of docker-compose."
            ],
            "sql": [
                "What are the different types of JOINs?",
                "How do you optimize a slow-running SQL query?"
            ]
        }
        
    def generate(self, resume_skills: list, role: str, company: str = "") -> list:
        """
        Generate a list of probable interview questions.
        """
        questions = []
        if company:
            questions.append(f"Scenario: Why are you interested in joining {company} as a {role.title()}?")
        else:
            questions.append(f"Scenario: Describe your experience and how it aligns with the {role.title()} role.")
            
        # Add a couple of questions based on matching or known skills
        count = 0
        for skill in set(resume_skills):
            s_lower = skill.lower()
            if s_lower in self.question_bank:
                questions.extend(self.question_bank[s_lower][:2])  # Take up to 2 questions per matching skill
                count += 1
            if count >= 3:
                break # Limit total number of technical questions
                
        if len(questions) < 3:
             questions.append("Coding: Write a function to reverse a linked list.")
             questions.append("Conceptual: Describe a challenging technical problem you solved recently.")
             
        return questions
