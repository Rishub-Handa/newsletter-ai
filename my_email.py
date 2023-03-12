from bs4 import BeautifulSoup
import re

class MyEmail:

    def __init__(self, email): 
        self.email = email
        self.sender = re.findall('^(.*)<', email.headers['From'])[0].strip()
        self.soup = BeautifulSoup(email.text_html[0], 'html.parser')

        self.headings_list = [f"{e.name}:{e.text.strip()}" for e in self.soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])]
        self.headings_text = "\n".join(self.headings_list)
        self.email_text = re.sub(r'\n+', '\n', str(self.soup.text))

    # TODO: Langchain prompt to get top headlines
    def get_top_headlines(self): 
        pass

    def set_headlines(self, headlines): 
        self.headlines = headlines