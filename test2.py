from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

prompt =  ChatPromptTemplate.from_messages(
    [
        (
            'system',
            'ты преподаватель {language}.'
            'объясняй материал для уровня {level}.'
            'Всегда приводи пример кода.'
        ),
        (
            'human',
            'Объясни тему: {topic}'
        )
    ]
)

model = ChatOllama(
    model="llama3.2:latest",
    temperature=0
)

chain = prompt | model

response = (
    {
        'language': "Python",
        'level': "Ниже среднего",
        'topic': "Строка"
    }
)

for i in chain.stream(response):
    print(i.text, end='')