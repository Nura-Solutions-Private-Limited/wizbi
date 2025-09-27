import json
import uuid

import structlog
from fastapi import HTTPException, status
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI
from sqlalchemy import MetaData, Table
from sqlalchemy.schema import CreateTable

import constants
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Db_Conn, Pipeline
from schemas.genai import (
    ConnectionQuestion,
    Conversation,
    OtherResponseType,
    QueryConversation,
    message,
)

logger = structlog.getLogger(__name__)


class GenAi:
    """
    Interface for chat gpt
    This class gets 25 question based on fact table
    and also provides methods to submit custom questions.
    """

    def __init__(self, db) -> None:
        self.client = OpenAI(api_key=constants.OPENAI_API_KEY)
        self.pipeline_id = None
        self.db = db
        self.metadata = MetaData()
        self.model = "gpt-3.5-turbo"

    def get_fact_table_script(self, engine, fact_table):
        self.metadata.reflect(engine)
        table = self.metadata.tables[fact_table]
        return CreateTable(table).compile(engine)

    def get_all_table_script(self, engine):
        schema_script = None
        # Reflect all tables from the database to the metadata object
        self.metadata.reflect(engine)

        # Get all table names as a list
        table_names = list(self.metadata.tables.keys())
        for table_name in table_names:
            table_name = self.metadata.tables[table_name]
            table_script = CreateTable(table_name).compile(engine)

            if schema_script:
                schema_script = schema_script + "\n" + str(table_script)
            else:
                schema_script = str(table_script)
        return schema_script

    def get_pipeline_db_conn(self):
        pipeline = self.db.query(Pipeline).filter(Pipeline.id == self.pipeline_id).first()
        if pipeline:
            fact_table = f"{pipeline.source_schema_name}_fact"
            dest_db_conn = self.db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
            if dest_db_conn:
                databaseConnection = DatabaseConnection(
                    database_type=dest_db_conn.db_type,
                    username=dest_db_conn.db_username,
                    password=dest_db_conn.db_password,
                    host=dest_db_conn.db_host,
                    port=dest_db_conn.db_port,
                    schemas=pipeline.dest_schema_name,
                )
                engine = databaseConnection.get_engine()
                return engine, fact_table

    def get_chatgpt_response(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0)

        return response.choices[0].message.content

    def prepare_fact_query(self):
        engine, fact_table = self.get_pipeline_db_conn()
        table_script = self.get_fact_table_script(engine=engine, fact_table=fact_table)
        logger.info(table_script)
        prompt = f"""Enclosed is the MySql DB star schema which is a data warehouse
            schema enclosed within 3 backticks ```{ table_script  }``` ,
            read the metrics from the fact table,
            note that the metrics are all the columns in the fact table
            that do not have ID as suffix.
            Now, create a set of 25 questions based on the metrics from the
            fact table that can user can use for artificial
            intelligence algorithms to enhnace business or any other use case
        """
        logger.info(prompt)
        return prompt

    def fact_follow_up_question(self, followUpQuestion):
        """
        Prepare prompt for follow up question based on previous fact table question/answer
        """
        self.pipeline_id = followUpQuestion.pipeline_id
        algorithm = followUpQuestion.algorithm
        question = followUpQuestion.question
        engine, fact_table = self.get_pipeline_db_conn()
        schema_script = self.get_all_table_script(engine=engine)

        query_prompt = f"""MySql DB star schema which is a data warehouse schema sql script enclosed
        within 3 backticks ```{schema_script}``` , read the metrics from the fact table, note that the
        metrics are all the columns in the fact table that do not have ID as suffix. Now, write a
        prediction analysis code in python using the algorith name enclosed within 3 backticks ```{algorithm}``` ,
        the data has to be read from the data warehouse schema enclosed within 3 backticks ```{schema_script}```
        for the question enclosed within 3 backticks ```{question}```.
        """

        chat_gpt_response = self.get_chatgpt_response(prompt=query_prompt)
        return {"type": "fact followup", "response": chat_gpt_response}

    def fact_questions(self, pipeline_id):
        self.pipeline_id = pipeline_id
        query_prompt = self.prepare_fact_query()
        chat_gpt_response = self.get_chatgpt_response(prompt=query_prompt)

        response_dict = dict()
        for res in chat_gpt_response.split("\n"):
            response_dict[res.split(". ")[0]] = res.split(". ")[1]
        return {"type": "fact table", "questions": response_dict}

    def other_questions(self, question):
        chat_gpt_response = self.get_chatgpt_response(prompt=question)
        return {"type": "other", "answer": chat_gpt_response}

    def gen_dashboard(self, pipeline_id: str, prompt: str | None) -> OtherResponseType:
        # Get the database schema
        self.pipeline_id = pipeline_id
        ret = self.get_pipeline_db_conn()
        if ret:
            engine = ret[0]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to connect to database.")
        schema_script = self.get_all_table_script(engine=engine)

        # create the required prompt
        query_prompt = "{{ " + (schema_script or "") + " }}\n"
        query_prompt += "The schema for the database in enclosed in \
                         the curly brackets above. Use this as the \
                         only valid source of information about the \
                         database. Do not assume anything about the \
                         data other than what has been provided above. \
                         Use this, along with your extensive database \
                         and data engineering skills to answer the \
                         prompt provided below.\n"
        if prompt:
            query_prompt += prompt
        else:
            query_prompt += 'From the provided schema write 10 different \
                SQL queries that can used for a dashboard with various \
                depicting charts. Provide your answer in the following \
                format: \
                { \
                    "query1": { \
                        "sqlcommands": "SOME SQL COMMANDS HERE", \
                        "title": "name of query" \
                        "description": "short detail on the query" \
                    }, \
                    ... \
                }\n Your response is used directly as part of a python \
                script. Make sure to provide your response exactly in \
                the format specified above, as perfectly correct and \
                valid JSON. Do not include any additional content.'
        logger.info(f"Prompt to chatGPT: {query_prompt}")

        # Send the request to chatGPT
        chat_gpt_response = self.get_chatgpt_response(prompt=query_prompt)
        logger.info(chat_gpt_response)
        chat_gpt_response = chat_gpt_response or ""

        # Validate the response
        if prompt:
            # Since it's a user specified prompt, we cannot
            # validate it here.
            pass
        else:
            if not self.validate_chatgpt_response(chat_gpt_response):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate queries. Please try again.",
                )

        return {"type": "dashboard queries", "answer": chat_gpt_response}

    def validate_chatgpt_response(self, response: str) -> bool:
        try:
            # Parse the JSON string
            data = json.loads(response)

            # Check if the top level is a dictionary
            if not isinstance(data, dict):
                return False

            # Iterate through each query
            for query, content in data.items():
                # Check if content is a dictionary
                if not isinstance(content, dict):
                    return False

                # Check if 'sqlcommands', 'title' and
                # 'description' keys exist
                if "sqlcommands" not in content:
                    return False
                if "title" not in content:
                    return False
                if "description" not in content:
                    return False

                # Check if 'sqlcommands' is a string
                if not isinstance(content["sqlcommands"], str):
                    return False

                # Check if 'title' is a string
                if not isinstance(content["title"], str):
                    return False

                # Check if 'description' is a string
                if not isinstance(content["description"], str):
                    return False

        except json.JSONDecodeError:
            logger.error("JSON parse error!")
            # If the response is not valid JSON
            return False

        # If all checks pass
        return True

    def create_conversation(self, conversation: Conversation, user_id: int):
        """
        Create a new conversation with the GenAI model.
        """
        # TODO: Validate the user ID
        conversation.user_id = user_id
        # Log the conversation creation
        logger.info(f"Creating conversation: {conversation}")
        # TODO: Save the conversation to the database
        # Include all the user data context needed for the conversation by preparing the data context
        return conversation

    def ask_question(self, user_id: int, conversation: QueryConversation):
        """
        Ask a question to chatGPT and return the response.
        This is used for the chat interface.
        """
        # TODO: Validate the conversation ID and user ID
        # Get the conversation details from database and set the data context
        prompt = f"Answer the following question: {conversation.question}"
        chat_gpt_response = f"""
        This is a placeholder response from chatGPT.
        Please replace this with the actual response from chatGPT.
        {prompt}
        """
        message_id = str(uuid.uuid4())
        conversation_id = conversation.conversation_id
        # Log the question and response
        logger.info(f"User {user_id} asked: {conversation.question}")
        logger.info(f"ChatGPT responded: {chat_gpt_response}")

        return {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "user_id": user_id,
            "question": conversation.question,
            "response": chat_gpt_response,
        }

    def get_conversation_history(self, user_id: int):
        """
        Get the user's conversation history.
        This is used for the chat interface.
        """
        # TODO: Validate the user ID
        # Get the conversation history from database
        # Return sample conversation history
        return [
            {
                "conversation_id": "12345",
                "user_id": user_id,
                "created_at": "2023-10-01T12:00:00Z",
                "messages": [
                    {
                        "message_id": "1",
                        "question": "Hello, how are you?",
                        "response": "Hello, how can I help you?",
                        "created_at": "2023-10-01T12:00:00Z",
                    }
                ],
            },
            {
                "conversation_id": "12346",
                "user_id": user_id,
                "created_at": "2023-10-01T12:00:00Z",
                "messages": [
                    {
                        "message_id": "1",
                        "question": "Hello, how are you?",
                        "response": "Hello, how can I help you?",
                        "created_at": "2023-10-01T12:00:00Z",
                    }
                ],
            },
        ]

    def get_conversation_history_by_id(self, user_id: int, conversation_id: str):
        """
        Get the user's conversation history.
        This is used for the chat interface.
        """
        # TODO: Validate the conversation ID and user ID
        # Get the conversation details from database
        # Return sample conversation history
        return {
            "conversation_id": "12345",
            "user_id": user_id,
            "created_at": "2023-10-01T12:00:00Z",
            "messages": [
                {
                    "message_id": "1",
                    "question": "Hello, how are you?",
                    "response": "Hello, how can I help you?",
                    "created_at": "2023-10-01T12:00:00Z",
                }
            ],
        }

    def connection_question(self, connectionQuestion: ConnectionQuestion):
        """
        Using user question and database connection details, prepare the context to generate sql query
        """
        db_conn_id = connectionQuestion.db_conn_id
        question = connectionQuestion.question

        # validate if db connection is valid
        db_connection = self.db.query(Db_Conn).filter(Db_Conn.id == db_conn_id).first()
        if not db_connection:
            logger.error(f"Invalid DB connection ID: {db_conn_id}")
            return {"error": "Invalid DB connection ID"}, 400

        # Build database connection
        databaseConnection = DatabaseConnection(
            database_type=db_connection.db_type,
            username=db_connection.db_username,
            password=db_connection.db_password,
            host=db_connection.db_host,
            port=db_connection.db_port,
            schemas=db_connection.db_name,
        )

        # Connect to the database
        sql_db = SQLDatabase.from_uri(databaseConnection.get_url())

        # Get database schema information
        db_schema = sql_db.get_table_info()

        # Initialize the LLM
        llm = ChatOpenAI(openai_api_key=constants.OPENAI_API_KEY, model="gpt-3.5-turbo")

        # Create a prompt template for SQL generation
        prompt = ChatPromptTemplate.from_template(
            """You are a SQL expert. Given the database schema and a question, 
            create a syntactically correct {dialect} query to answer the question.
            
            Database schema: {schema}
            
            Question: {question}
            
            SQL Query:"""
        )

        # Create the chain using the modern LangChain API
        chain = prompt | llm | StrOutputParser()

        # Run the chain
        sql_query = chain.invoke({"dialect": db_connection.db_type.lower(), "schema": db_schema, "question": question})

        logger.info(f"Generated SQL: {sql_query}")
        return {"question": question, "sql_query": sql_query}
