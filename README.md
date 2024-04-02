## LLM Competition Analyzer

### Overview

The LLM Competition Analyzer is a sophisticated Python-based tool designed to evaluate and compare answers from different Large Language Models (LLMs) against a standard reference source, in this case, Wolfram Alpha. The tool utilizes models from GPT-4ALL, fetching answers to a set of questions and comparing them for similarity, thereby assessing the models' accuracy and reliability.

### Features

**LLM Evaluation**: Leverages models from GPT-4ALL to answer questions and evaluates their accuracy.

**Wolfram Alpha Integration**: Uses Wolfram Alpha as a benchmark to compare LLM answers against.

**Similarity Scoring**: Employs a similarity scoring system to quantitatively assess LLM responses.

**Redis Caching**: Implements Redis for efficient caching of Wolfram Alpha responses.

**Comprehensive Logging**: Includes logging for easy monitoring and debugging.

### Prerequisites

Python 3.x

Redis server

Internet connection for API requests

Before running the tool, ensure that you have access to the necessary LLM models on GPT-4ALL. You might need to download or subscribe to these models on the GPT-4ALL platform.
Please refer to GPT-4ALL's documentation or contact their support for guidance on accessing the models:

- **orca-2-7b.Q4_0.gguf**

- **mistral-7b-openorca.Q4_0.gguf**


### Installation

#### Clone the repository:
```
git clone https://github.com/YonathanAllouch/llm_competition.git
```
#### Navigate to the project directory:
```
cd LLM-Competition-Analyzer
```
#### Install required Python packages:
```
pip install -r requirements.txt
```
Create a requirements.txt file if it doesn't exist, listing all the necessary packages such as redis, requests, dotenv, and any specific packages required for GPT-4ALL integration.

#### Set up Redis:
Ensure Redis is installed and running on your system. The default configuration assumes Redis is accessible at localhost:6379.

#### Configure environment variables:
Create a .env file in the project root with the necessary API keys and configurations, such as:

```
WOLFRAM_APP_ID=your_wolfram_app_id_here
```

### Usage

#### Prepare your question set:
Load your questions into a CSV file named General_Knowledge_Questions.csv, ensuring each question is listed under a Question column.

#### Run the tool:
Execute the script with:

```
python LLM_Competition.py
```

#### Review the results:

The tool will log the process and output the results, including the number of questions answered, average ratings for each LLM, and the lowest-rated answers.

### Contributing

Contributions to the LLM Competition Analyzer are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.

### License

This project is open-sourced under the MIT License.


### Demo

