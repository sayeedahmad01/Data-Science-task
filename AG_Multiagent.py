import asyncio
import os
from dotenv import load_dotenv
import streamlit as st
from typing import AsyncGenerator, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat 
from autogen_agentchat.conditions import TextMentionTermination 
from autogen_ext.models.openai import OpenAIChatCompletionClient  

st.set_page_config(page_title="Autogen Multi-Agent Chat created by PRAKASH SENAP", page_icon="**", layout="wide" )
st.title("Autogen Multi-Agent Chat created by PRAKASH SENAPATI") 

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
st.sidebar.header("API Key Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password", value=gemini_api_key)

task_description = ''' 
It is 7:30 am at home.
Father has 3 responsibilities to complete before leaving for work.
1. kid 1 needs to go to school A (Arrive By 8:00AM)
2. kid 2 needs to go to school B (Arrive By 8:15AM)
3. Father needs to reach office by 9:00AM)
Create a coordinated plan for ensure all deadlines are completed on time.
'''
st.info(f"**Task:** {task_description}")

# Autogen logic steps

async def get_team_stream(task:str, key:str) -> AsyncGenerator[Any, None]:
    '''sets up agent and return the message stream generator'''

    model_client = OpenAIChatCompletionClient(
        model = 'gemini-3-flash-preview',
        api_key = key,
        model_info = {
            'vision':True,
            'function_calling':True,
            'json_output':True,
            'family':'gemini'} )
    

# define agents 
    agent1 = AssistantAgent(
        name='School_Agent_1',
        model_client=model_client,
        system_message=''' 
        You are School Agent 1.
        Responsibility : Taske kid 1 to school A.
        Must arrive before 8:00AM 
        Create a specific plan with times (eg- leave at 7:30)
        Do not handle kid 2 or Fathers office ''' )

    agent2 = AssistantAgent(
        name='School_Agent_2',
        model_client=model_client,
        system_message=''' 
        You are School Agent 2.
        Responsibility : Task kid 2 to school B.
        Must arrive before 8:15AM 
        Create a specific plan with times (eg- leave at 7:45)
        Do not handle kid 1 or Fathers office ''' )

    agent3 = AssistantAgent(
        name='Office_Agent',
        model_client=model_client,
        system_message=''' 
        You are Office Agent .
        Responsibility : Taske Father to office.
        Must arrive before 9:00AM 
        Reas plans from School Agent 1 and 2
        Ensure all three plans exists and are timed realistically.
        If coordinated, say exactly: ALL TASK COMPLETED TERMINATE''')

    termination = TextMentionTermination('Terminate')

    team = RoundRobinGroupChat(
        participants=[agent1, agent2, agent3],
        termination_condition=termination)

    async for message in team.run_stream(task=task):
            yield message


if "messages" not in st.session_state:
    st.session_state.messages = []
# Display existing chat history using native Streamlit chat bubbles
for msg in st.session_state.messages:
    with st.chat_message(msg["source"]):
        st.write(msg["content"])
# Trigger planning process
if st.sidebar.button("Start Planning", type="primary"):
    if not api_key:
        st.error("Please enter a valid Gemini API Key.")
    else:
        # Clear previous conversation history
        st.session_state.messages = []
        async def run_workflow():
            with st.status(" Planning in progress...", expanded=True) as status:
                try:
                    async for message in get_team_stream(task_description, api_key):
                        # Extract source and content safely
                        source = getattr(message, "source", "System")
                        content = getattr(message, "content", str(message))

                        # Skip empty or internal system objects if content is empty
                        if not content:
                            continue
                        # Save to session history
                        st.session_state.messages.append({
                            "source": source,
                            "content": content
                        })
                        # Render natively using Streamlit chat message component
                        with st.chat_message(source):
                            st.write(content)
                    status.update(label="✅ Planning Completed!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="❌ Error occurred", state="error", expanded=True)
                    st.error(f"Execution Error: {e}")
        # Run the async loop safely inside Streamlit
        asyncio.run(run_workflow())