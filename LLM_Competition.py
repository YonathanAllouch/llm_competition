import logging
import time
import redis
import os
import requests
import csv
from dotenv import load_dotenv
from gpt4all import GPT4All
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Initialize the clients
app_id = os.getenv('WOLFRAM_APP_ID') 

# Define models
llm1 = "orca-2-7b.Q4_0.gguf"
llm2 = "mistral-7b-openorca.Q4_0.gguf" # Also used for similarity scoring

# Initialize the GPT4All models once
print("Initializing LLM models...")
llm_models = {
    llm1: GPT4All(llm1),
    llm2: GPT4All(llm2),
}

# Connect to Redis
print("Connecting to Redis...")
try:       
    r = redis.Redis(host='localhost', port=6379, db=0)
    print("Connected to Redis successfully.")
except Exception as e:
    logging.error(f"Error connecting to Redis: {e}")
    print(f"Error connecting to Redis: {e}")
    r = None

# Load the questions from a CSV file
print("Loading questions from CSV...")
questions = []
with open('/Users/yonathanallouch/Downloads/General_Knowledge_Questions.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        questions.append(row['Question'])
print(f"Loaded {len(questions)} questions.")

# Function to get the Wolfram Alpha answer
def get_wolfram_answer(question):
    if r is None:
        logging.error("Redis connection is not available.")
        return None

    # Check if the answer is in the cache
    cached_answer = r.get(question)
    if cached_answer is not None:
        # If the answer is in the cache, return it
        return cached_answer.decode('utf-8')

    # If the answer is not in the cache, fetch it from the API
    encoded_question = requests.utils.quote(question)
    url = f"https://api.wolframalpha.com/v1/result?i={encoded_question}&appid={app_id}"
    response = requests.get(url)

    if response.status_code == 200:
        # Store the answer in the cache before returning it
        r.setex(question, 14400, response.text)  # Cache for 4 hours
        return response.text
    else:
        return None

# Function to get the LLM answer
def get_llm_answer(question, model):
    question_prompt = "### Human:" + "\n" + question + "\n" + "### Assistant:"
    return llm_models[model].generate(question_prompt)


# Function to get the similarity score from a llm answer and a wolfram answer
def get_similarity_score(wolfram_answer , llm_answer):
    
    prompt = (
    "###Instruction:\n"
    "Rate the similarity of these two answers on a scale from 0 to 1.0, where 0 is completely different and 1.0 is identical. PROVIDE ONLY THE NUMERICAL ANSWER.\n"
    "###Example 1:\n"+"Answer 1: 'Paris'\n"+"Answer 2: 'Paris'\n"+"Your rating is: 1.0\n"
    "###Example 2:\n"+"Answer 1: 'William Shakespeare'\n"+"Answer 2: 'Charles Dickens'\n"+"Your rating is: 0\n"
    "###Example 3:\n"+"Answer 1: 'H2O'\n"+"Answer 2: 'Water is composed of two hydrogen atoms bonded to a single oxygen atom, commonly represented as H2O.'\n"+"Your rating is: 1.0\n"
    "###Example 4:\n"+"Answer 1: 'Mercury, Venus, Earth'\n"+"Answer 2: 'Mercury, Venus'\n"+"Your rating is: 0.66\n"
    "###Actual Answers:\n"
    f"Answer 1: '{wolfram_answer}'\n"
    f"Answer 2: '{llm_answer}'\n"
    "Your rating is:\n"
    "###Response:\n"
)
    response = llm_models[llm2].generate(prompt)
   
    try:
        return float(response.strip())
    except ValueError:
        print(f"Error: {response}")
        return 0

# Initialize tracking variables
number_of_questions_answered = 0
total_rating_llm1, count_llm1 = 0, 0
total_rating_llm2, count_llm2 = 0, 0
lowest_rating_llm1, lowest_question_llm1, lowest_answer_llm1 = 1.0, None, None
lowest_rating_llm2, lowest_question_llm2, lowest_answer_llm2 = 1.0, None, None

# Main data structure for storing results
results = []

start_time = time.time()
print("Processing questions...")
for question in questions:
    try: 
        print(f"Processing question: {question}")
        # Fetch Wolfram Alpha answer
        wolfram_answer = get_wolfram_answer(question)
        if wolfram_answer:
            print(f"Wolfram Alpha provided an answer: {wolfram_answer}")
            print()
            number_of_questions_answered += 1
        else:
            print(f"No answer from Wolfram Alpha for: {question}")
            print()
            continue    

        # Fetch LLM answers and calculate similarity
        for model in [llm1, llm2]:
            llm_answer = get_llm_answer(question, model)
            print(f"Received answer from {model}: {llm_answer}")
            print()
            rating = get_similarity_score(wolfram_answer, llm_answer)
            print(f"Similarity score for {model} is {rating}")
            print()
            results.append({
                'Question': question,
                'Model': model,
                'Answer': llm_answer,
                'Correctness': rating * 10  # Scale to 0-10
            })

            # Update statistics
            if model == llm1:
                total_rating_llm1 += rating
                count_llm1 += 1
                if rating < lowest_rating_llm1:
                    lowest_rating_llm1, lowest_question_llm1, lowest_answer_llm1 = rating, question, llm_answer
            else:
                total_rating_llm2 += rating
                count_llm2 += 1
                if rating < lowest_rating_llm2:
                    lowest_rating_llm2, lowest_question_llm2, lowest_answer_llm2 = rating, question, llm_answer

    except Exception as e:
        logging.error(f"Error processing question: {question}, Error: {e}")
        print(f"Error processing question: {question}, Error: {e}")


# Calculate average ratings and print results
avg_rating_llm1 = total_rating_llm1 / count_llm1 if count_llm1 else 0
avg_rating_llm2 = total_rating_llm2 / count_llm2 if count_llm2 else 0
print()
print()
print("Results:")
print(f"Number of questions answered: {number_of_questions_answered}")
print(f"Average answer rating of LLM1: {avg_rating_llm1:.2f}")
print(f"Average answer rating of LLM2: {avg_rating_llm2:.2f}")
print(f"Lowest rating question and answer of LLM1: {lowest_question_llm1}\n{lowest_answer_llm1}")
print(f"Lowest rating question and answer of LLM2: {lowest_question_llm2}\n{lowest_answer_llm2}")

end_time = time.time()
print(f"Total time taken: {int(end_time - start_time) / 60:.2f} minutes")
