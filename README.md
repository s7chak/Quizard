# Quizard

## Description

Quizard is an interactive interface with OpenAI's Language Model (LLM) designed to generate quizzes based on any document the user provides. It leverages the concept of Retrieval Augmented Generation (RAG) to prompt the LLM for user-specified questions.

### Key Features:

- Generate quizzes from uploaded documents (links, PDFs, Word documents).
- Utilizes the power of OpenAI's LLM with sophisticated prompts.
- User-friendly UI for file/link upload and quiz generation.
- Export quizzes as Word documents.
- Fast quiz generation, taking only a few minutes depending on the uploaded resources.

## Installation

### Requirements:

- Python 3.10
- Numpy
- Pandas
- Matplotlib
- Scipy
- Plotly
- Dash 2.10.2
- Dash Bootstrap Components 1.4.1
- Dash Extensions
- Dash Iconify s0.1.2
- XGBoost
- Statsmodels 0.14.0
- Scikit-learn 1.2.2
- Yfinance
- Yahoo_fin
- Selenium
- Dash Daq
- Kaleido
- Pillow
- Dash
- Dash Bootstrap Components
- Python-docx
- Chromadb
- Unstructured
- Tiktoken

### Installation Steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/s7chak/quizard.git
   ```

2. Navigate to the project directory:

   ```bash
   cd quizard
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Quizard app:

   ```bash
   python app.py
   ```

2. Open your web browser and visit [http://localhost:8050](http://localhost:8050).

3. Use the UI to upload documents (links, PDFs, Word documents).

4. Configure the quiz settings and initiate quiz generation.

5. Download the generated quiz as a Word document.

## Notes

- Ensure that the required dependencies are installed before running the app.
- Adjust the port number (default is 8050) based on your preferences.
- The prompt used to generate this quiz:

```
Design a quiz using the context provided with {} multiple-choice questions. 
Please make sure to include 4 answer options (a, b, c, d) for each question. 
The difficulty levels should be distributed as follows:
- {} questions of low difficulty
- {} questions of medium difficulty
- {} questions of high or hard difficulty

Quiz Title: [Your Quiz Title]

Question 1: [Your Question Here]
a. [Option a]
b. [Option b]
c. [Option c]
d. [Option d]
Correct Answer: [Correct Option]

Question 2: [Your Question Here]
a. [Option a]
b. [Option b]
c. [Option c]
d. [Option d]
Correct Answer: [Correct Option]

...


Please follow this exact format since I will be parsing your quiz programmatically.

```





## License

This project is licensed under the [MIT License](LICENSE).
