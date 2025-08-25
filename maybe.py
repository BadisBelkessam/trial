from dotenv import load_dotenv
import os

from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain_groq import ChatGroq
from supabase import create_client, Client
from langchain_core.runnables import RunnableLambda
from fastapi import FastAPI
from pydantic import BaseModel


from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import initialize_agent



load_dotenv()

supa = os.getenv("Supabase_Project_Password")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
ai = os.getenv("GROQ_API_KEY")
supabase: Client = create_client(url, key)



llm = ChatGroq(model = "gemma2-9b-it", api_key= ai)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f"""
         You are an sql agent that answers questions about the database,
         always check the schema of the database and all of the relations present in it using the tools you have.
         And make sure, whenever you find maybe a row or column that the answe lies at, to check all foreign keys from or to it and check the data there to get more detailed and accurate answeres if found there
         Never run a query that alters or modifies the db in any way, you are only a retriever that answers questions you have no authority to change nothing
        """),
        ("user", "{input}")
    ]
)


db = SQLDatabase.from_uri(f"postgresql://postgres.hioxzjseqyevsstvntvu:{supa}@aws-0-us-east-2.pooler.supabase.com:6543/postgres")


@tool
def show_relationships(dummy : str = ''):
    """Show foreign key relationships between tables."""
    query = """
    SELECT conrelid::regclass AS table_name, conname AS constraint_name,
           pg_get_constraintdef(c.oid) AS definition
    FROM pg_constraint c
    WHERE contype = 'f';
    """
    return db.run(query)

@tool
def preview_table(table_name: str):
    """Preview the first few rows of a table."""
    return db.run(f"SELECT * FROM {table_name} LIMIT 5;")


@tool
def get_data_dictionary(dummy : str = ''):
    """Return all about tables, their columns, primary keys, and foreign keys"""
    return """
    --List all tables:
| table_name |
| ---------- |
| sites      |
| details    |
| mobil      |
| immobil    |

    --List columns for each table:
| table_name | column_name    | data_type                   |
| ---------- | -------------- | --------------------------- |
| details    | id             | bigint                      |
| details    | created_at     | timestamp with time zone    |
| details    | info           | text                        |
| immobil    | id             | bigint                      |
| immobil    | found          | timestamp with time zone    |
| immobil    | surface        | double precision            |
| immobil    | more           | bigint                      |
| immobil    | name           | character varying           |
| immobil    | location       | character varying           |
| mobil      | id             | bigint                      |
| mobil      | found          | timestamp without time zone |
| mobil      | name           | character varying           |
| mobil      | weight         | double precision            |
| mobil      | place          | bigint                      |
| mobil      | more           | bigint                      |
| sites      | id             | bigint                      |
| sites      | created_at     | timestamp with time zone    |
| sites      | wilaya         | character varying           |
| sites      | number of lots | integer                     |

--List all primary keys:
| table_name | column_name |
| ---------- | ----------- |
| sites      | id          |
| mobil      | id          |
| immobil    | id          |
| details    | id          |

--List all foreign keys:
| table_name | column_name | foreign_table_name | foreign_column_name |
| ---------- | ----------- | ------------------ | ------------------- |
| mobil      | place       | sites              | id                  |
| immobil    | more        | details            | id                  |
| mobil      | more        | details            | id                  |
| immobil    | location    | sites              | wilaya              |
    """


tools =[
    show_relationships,
    preview_table,
    get_data_dictionary,
]


# create an agent that can query SQL
sql_agent = create_sql_agent(llm=llm, db=db, verbose=True)

agent = initialize_agent(tools= tools + sql_agent.tools , llm= llm , agent_type="zero-shot-react-description", verbose=True)

chain = prompt | agent
# now you can query in natural language
response = chain.invoke({"input":"can you give me more details about the immobil that was found in the wilaya of blida"})
print(response["output"])

















































































