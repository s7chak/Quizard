import hashlib
import json
import os

import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from config import Config


class LanguageModel:
    def __init__(self):
        openai.api_key = '<OPENAI_API_KEY>'
        os.environ["OPENAI_API_KEY"] = openai.api_key
        self.qa = None

    def doc_feed(self, file):
        embeddings = OpenAIEmbeddings()
        loader = DirectoryLoader("", glob=file)
        txt_docs = loader.load_and_split()
        docsearch = Chroma.from_documents(txt_docs, embeddings)
        # llm = InferenceOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
        self.qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())

    def doc_query(self, question):
        if self.qa:
            ans = self.qa.run(question)
        else:
            ans = "Not yet."
        return ans

    def query_with_prompt_file(self, prompt_file_path, count, difficulties=()):
        with open(prompt_file_path, 'r') as prompt_file:
            prompt_data = json.load(prompt_file)
            quiz_prompt = prompt_data.get("quiz_prompt", "")
            quiz_prompt = quiz_prompt.format(count, difficulties[0], difficulties[1], difficulties[2])


        response = self.doc_query(quiz_prompt)

        return response

    def train_llm(self, txt_dir):
        for txt_file in os.listdir(txt_dir):
            if '.txt' in txt_file:
                txt_file_path = os.path.join(txt_dir, txt_file)
                self.doc_feed(txt_file_path)

    def save_quiz_as_json(self, quiz_json, file_path):
        with open(file_path, 'w') as quiz_file:
            json.dump(quiz_json, quiz_file, indent=4)

    def save_response_as_json(self, response, file_path):
        with open(file_path, 'w') as response_file:
            json.dump(response, response_file, indent=4)

    def parse_quiz_response(self, response):
        quiz_lines = response.strip().split('\n')
        quiz_dict = {
            'title': quiz_lines[0].strip().split(': ')[1],
            'questions': []
        }

        for i in range(1, len(quiz_lines)):
            if not ('question' in quiz_lines[i].lower() and len(quiz_lines[i].strip().split(':'))>1):
                continue
            question_number = quiz_lines[i].strip().split(': ')[0]
            question_text = quiz_lines[i].strip().split(': ')[1]
            answer_options = [x.strip() for x in [quiz_lines[i + 1],quiz_lines[i + 2],quiz_lines[i + 3],quiz_lines[i + 4]]]
            correct_answer = quiz_lines[i + 5]
            i+=5
            if question_number:
                question_dict = {
                    'number': question_number,
                    'text': question_text,
                    'options': answer_options,
                    'correct_answer': correct_answer
                }

                quiz_dict['questions'].append(question_dict)

        return quiz_dict

class Util():

    def save_dataframe(self, df:pd.DataFrame, path, name):
        df.to_csv(path+name)

    def get_average(self,d, cat, val):
        return pd.DataFrame(round(d.groupby(cat)[val].mean(), 2))

    def get_average_multi(self,d, cats, val):
        return pd.DataFrame(round(d.groupby(cats)[val].mean(), 2))

    def get_last_multi(self,d, cats, val):
        return pd.DataFrame(round(d.groupby(cats)[val].tail(1).reset_index(), 2))

    def get_sum(self,d, cat, val):
        return pd.DataFrame(round(d.groupby(cat)[val].sum(), 2))

    def get_sum_multi(self,d, cats, val):
        return pd.DataFrame(round(d.groupby(cats)[val].sum(), 2))

    def read_data(self):
        pass

    def clean_article(self, article_text):
        cleaned_text = ' '.join(article_text.split())
        return cleaned_text

    def save_link_content(self, link):
        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            article = soup.find('article')

            if article:
                filename = hashlib.md5(link.encode()).hexdigest() + ".txt"
                file_path = os.path.join(Config.wd_path, filename)
                if not os.path.exists(Config.wd_path):
                    os.mkdir(Config.wd_path)
                article_text = article.get_text()
                cleaned_text = self.clean_article(article_text)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(cleaned_text)

                print(f"Saved content from {link} to {file_path}")
            else:
                print(f"No article found on {link}")

        except Exception as e:
            return print("Error processing {link}: {str(e)}")


