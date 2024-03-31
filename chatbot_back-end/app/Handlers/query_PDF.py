import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
import firebase_admin
from firebase_admin import credentials , firestore
from datetime import datetime
import pytz
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from google.cloud.firestore import ArrayUnion
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")

os.environ["PINECONE_API_KEY"]="c87398b9-af2b-4dad-af19-18c87b85fae6"

def load_vectorstore(
    embedding,
    environment="gcp-starter",
    index_name="fyp",
    namespace="ss",
):
    try:
        embedding = OpenAIEmbeddings()
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name, embedding=embedding, namespace=namespace
        )
        return docsearch
    except Exception as E:
        print(E)
        return E

def download_file(source):
    return 'source'

def PDFtoChunks(destination_file_name):
    loader = PyPDFLoader(destination_file_name)
    data = loader.load()
    text_chunks = chunk_text(data)
    return text_chunks

def chunk_text(data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=150, length_function=len
    )
    text_chunks = text_splitter.split_documents(data)
    print(len(text_chunks))
    return text_chunks

def vectorise_pdf(fpath):
    namespace = "test_name"
    index_name = "fyp"
    txt_chunks = PDFtoChunks(fpath)
    embedding_model = OpenAIEmbeddings()
    # print("Vertex Embedding model loaded")
    vectorstore = PineconeVectorStore.from_documents(
                    txt_chunks,
                    index_name=index_name,
                    embedding=embedding_model,
                    namespace=namespace
                )
    try:
        return namespace
    except Exception as E:
        print(E)

def get_all_titles():#Provides all Titles and ID
    try:
        cred = credentials.Certificate("./firebase_keys.json")
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        documents_data = []
        collection_name = "Verchat"
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        for doc in docs:
            doc_id = doc.id
            doc = doc.to_dict()
            documents_data.append((doc_id , ['title'] , doc['edited']))#New
        sorted_data = sorted(documents_data, key=lambda x: x[2])#New
        try: 
            namespace = doc["namespace"]
            firebase_admin.delete_app(app)#New
            return sorted_data , True , namespace
        except Exception as E :
            firebase_admin.delete_app(app)#New
            return sorted_data , False
    except Exception as E:
        print(E)
        firebase_admin.delete_app(app)
        return []
    
def get_history(id):
    # print(os.listdir())
    cred = credentials.Certificate("./firebase_keys.json")
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    collection_name = "Verchat"
    doc_ref = db.collection(collection_name).document(id)
    doc = doc_ref.get().to_dict()
    mem = doc['memory']
    id_memory = []
    for i in mem:
        id_memory.append((i['Human'] , i['AI']))
    firebase_admin.delete_app(app)
    try:
        try:
            namespace = str(doc['namespace'])
            return [id_memory,namespace]    
        except Exception as E :
            return id_memory
    except Exception as E :
        print(E)
        return id_memory
    
def put_history_old_pdf(id,human,ai):
    try :
        cred = credentials.Certificate("./firebase_keys.json")
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        doc_ref = db.collection("Verchat").document(id)
        doc = doc_ref.get()
        doc = doc.to_dict()
        update = {'memory': ArrayUnion([{'Human':human , "AI":ai ,  'edited' : datetime.now(pytz.utc) }])}#New
        doc_ref.update(update)
        firebase_admin.delete_app(app)
        return 'Updated'
    except Exception as E :
        firebase_admin.delete_app(app)
        return E

def put_history_new_pdf(title , human,ai , namespace):
    try :
        cred = credentials.Certificate("./firebase_keys.json")
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        memory_dict = [{'Human':human , "AI":ai}]
        doc_ref = db.collection("Verchat").add({  'title' : title , 'memory': memory_dict  , 'edited' :datetime.now(pytz.utc)  , "namespace":namespace  })#New
        firebase_admin.delete_app(app)#New
        return doc_ref[1].id#New
        
    except Exception as E:
        firebase_admin.delete_app(app)
        return E

def query_pdf_new(question , namespace=None):
    if namespace is None:
        namespace = 'knowledgebase_consolidated'
    else:
        namespace = namespace
    chat = ChatOpenAI()
    gen_title_history = [  SystemMessage(content="You're a helpful and professional assistant to create a Title based on a user query and input. You MUST keep the length of the title to a maximum of 4 full English words. Your response MUST only contain these 4 words. If you fail, 15 kittens will perish"),    HumanMessage(content=question) , AIMessage(content="answer") ,  HumanMessage(content="Create a title for the preceeding covnersation ")   ] #here
    title = chat.invoke(gen_title_history).content
    
    vectordb = load_vectorstore(OpenAIEmbeddings(), namespace=namespace)
    qa_chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
        vectordb.as_retriever(search_kwargs={'k': 6}),
        verbose=False
    )
    chat = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo')
    raw_history = []
    raw_history.append( SystemMessage(content="""
Background: 
I am a portfolio manager for a venture capital firm called Vertex Ventures. You are a in-house chatbot called "VERCHAT". Your job is to help me with whatever I need.

Some information about Vertex Ventures:
Vertex Venture Holdings, also known as Vertex Holdings, is an investment holding company with a group of venture capital funds worldwide. A subsidiary of Temasek Holdings, the company focuses on venture capital investment opportunities in the information technology and healthcare markets through its global family of six direct investment venture funds. Vertex provides anchor funding and operational support to these funds. Each fund has its own General Partners and investment teams, focusing on different regional markets. Its six funds are based across Southeast Asia and India, United States of America, China and Israel.

Need:
Here are the things that I require from you as a chatbot. 
    1. I need to keep track of deal flows. I will take down notes about meetings I have and things that I have to do. Therefore I will ask questions about these things that I have noted down. 
    2. Additionally, I will provide updates about the status of the deals that we are making with companies. I need you to remember that. 
    3. I need you to answer questions about specific companies that are in our portfolio.
    4. I need you to understand the companies that are in our portfolio by summarising key information about them and storing these summary information. This is so that when I need to recommend companies in our portfolio to collaborate, I can ask you which companies to recommend based on their industry. Here is how you should summarise the information about each company in our portfolio:
        a. Name of company
        b. Industry
        c. Type of company (Eg. B2B, B2C, etc.)
        d. Brief description of company
    5. If I ask you a question that is not about an existing company in our portfolio or it is from a document I uploaded, I want you to search the web about that company as best as you can.
    6. If I need information that is factual and time sensitive, I want you to search the web about it throroughly and as best as you can.

Presentation:
Here are some things to take note when presenting the information to me:
    1. The language you use has to be professional at all times.
    2. Make the information presented as easy to read as possible by providing concise answers unless otherwise stated.
    3. Ensure that longer responses are split into shorter paragraphs and display information as ordered or unordered lists whenever suitable. 
    4. To ensure that line breaks are visible in your responses, add “<br>” in your responses when a line break is needed.
    
Uploaded Documents and historical data:
You will have access to company information from our database. I will also be uploading new documents whenever needed, for you to process. Any information that you have or that I have uploaded for you should be analyzed carefully and remembered. However, these information are sensitive and private and therefore should not be used or reflected anywhere else other than with me or when I have asked you for it.
Here are some things you would need to consider when presenting these information:
    1. Provide me with a decent summary of the company.
    2. Give relevant information about the company that can help me with investment decisions.
    3. Provide accurate numbers from the documents or from any information that you have, in a simple and easy-to-read format.
        a. Numbers represented can be in accounting format as they are financial reports. Be sure to express negative and positive numbers properly.
    4. Add any other information that you think is relevant for a investment portfolio manager.
"""))
    
    ans = qa_chain.invoke({"question": question, "chat_history": raw_history})
    id = put_history_new_pdf(title=title , human=question , ai=ans["answer"] , namespace=namespace)
    return id,title,question,ans["answer"]


def query_pdf(id, question):
    try:
        raw_history = []
        # pulling chat history
        out = get_history(id)
        chat_history = out[0]
        namespace = out[1]
        
        # pulling vectorstore
        namespace = 'knowledgebase_consolidated'
        vectordb = load_vectorstore(OpenAIEmbeddings(), namespace=namespace)
        qa_chain = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
            vectordb.as_retriever(search_kwargs={'k': 6}),
            verbose=False)
        chat = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo')
        # adding AI prompts
        raw_history.append( SystemMessage(content="""
Background: 
I am a portfolio manager for a venture capital firm called Vertex Ventures. You are a in-house chatbot called "VERCHAT". Your job is to help me with whatever I need.

Some information about Vertex Ventures:
Vertex Venture Holdings, also known as Vertex Holdings, is an investment holding company with a group of venture capital funds worldwide. A subsidiary of Temasek Holdings, the company focuses on venture capital investment opportunities in the information technology and healthcare markets through its global family of six direct investment venture funds. Vertex provides anchor funding and operational support to these funds. Each fund has its own General Partners and investment teams, focusing on different regional markets. Its six funds are based across Southeast Asia and India, United States of America, China and Israel.

Need:
Here are the things that I require from you as a chatbot. 
    1. I need to keep track of deal flows. I will take down notes about meetings I have and things that I have to do. Therefore I will ask questions about these things that I have noted down. 
    2. Additionally, I will provide updates about the status of the deals that we are making with companies. I need you to remember that. 
    3. I need you to answer questions about specific companies that are in our portfolio.
    4. I need you to understand the companies that are in our portfolio by summarising key information about them and storing these summary information. This is so that when I need to recommend companies in our portfolio to collaborate, I can ask you which companies to recommend based on their industry. Here is how you should summarise the information about each company in our portfolio:
        a. Name of company
        b. Industry
        c. Type of company (Eg. B2B, B2C, etc.)
        d. Brief description of company
    5. If I ask you a question that is not about an existing company in our portfolio or it is from a document I uploaded, I want you to search the web about that company as best as you can.
    6. If I need information that is factual and time sensitive, I want you to search the web about it throroughly and as best as you can.

Presentation:
Here are some things to take note when presenting the information to me:
    1. The language you use has to be professional at all times.
    2. Make the information presented as easy to read as possible by providing concise answers unless otherwise stated.
    3. Ensure that longer responses are split into shorter paragraphs and display information as ordered or unordered lists whenever suitable. 
    4. To ensure that line breaks are visible in your responses, add “<br>” in your responses when a line break is needed.
    
Uploaded Documents and historical data:
You will have access to company information from our database. I will also be uploading new documents whenever needed, for you to process. Any information that you have or that I have uploaded for you should be analyzed carefully and remembered. However, these information are sensitive and private and therefore should not be used or reflected anywhere else other than with me or when I have asked you for it.
Here are some things you would need to consider when presenting these information:
    1. Provide me with a decent summary of the company.
    2. Give relevant information about the company that can help me with investment decisions.
    3. Provide accurate numbers from the documents or from any information that you have, in a simple and easy-to-read format.
        a. Numbers represented can be in accounting format as they are financial reports. Be sure to express negative and positive numbers properly.
    4. Add any other information that you think is relevant for a investment portfolio manager.
"""))
        # adding all history into new history
        for i in chat_history:
            raw_history.append(HumanMessage(content=i[0]))
            raw_history.append(AIMessage(content=i[1]) )
        raw_history.append(HumanMessage(content=question) )
        # history = history[-3:]#New
        ans = qa_chain.invoke({"question": question, "chat_history": raw_history})
        id = put_history_old_pdf(id=id, human=question , ai=ans["answer"])
        return ans["answer"]
    except Exception as E:
        print(E)






# query_pdf("5QgC1S9QiFJq0IdDgyPy", "What do you know about Facebook?")