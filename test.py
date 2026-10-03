from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
model = ChatOllama(
    model='llama3.2',
    temperature=0
)

messages =[
    SystemMessage(
        content=(
            'Ты опытный senior python-разработчик с 10 летним опытом работы'
            'ты должен отвечать на вопросы кратко и с примерами'
        )
    ),
    HumanMessage(
        content=(
            'Что такое Langchain'
        )
    )
]


response = model.invoke(messages)
print(response.content)