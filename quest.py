 
import re
file_path = 'mongo_db.txt'



with open(file_path, 'r') as file:
    text = file.read()
        # Assuming '|' separates the question and answer

pattern = r'(\d+\.\s.*?\?)\s*(-\s.*?)(?=\d+\.|$)'
matches = re.findall(pattern, text, re.DOTALL)

for i, (question,answer) in enumerate(matches,1):
    print(f'Question {i}: {question.strip()}')
    print(f'Answer {i}: {answer.strip()}')
    print('-'*30)



