import streamlit as st 
import vertexai
from vertexai.generative_models import GenerativeModel
from openai import OpenAI
import keys

GEMINI_PROJECT = keys.GEMINI_PROJECT
GEMINI_LOCATION = keys.GEMINI_LOCATION
GEMINI_MODEL = keys.GEMINI_MODEL
OPENAI_API_KEY = keys.OPENAI_API_KEY
GPT_MODEL = keys.GPT_MODEL


def text_troubleshooting():
    st.session_state.system_persona = "You are an assistant who debugs the code."
    st.session_state.system_context = "The user is looking for a solution to the problem."
    st.session_state.system_instructions = "Your task is to figure out the problem and propose a solution."
    st.session_state.system_tone = "Propose consistent and proven solutions."
    st.session_state.system_format = "Write the result as text or a code snippet."
    st.session_state.system_custom = "\"\"\"\n" + st.session_state.system_persona + " " + st.session_state.system_context + " " + st.session_state.system_instructions + " " + st.session_state.system_tone + " " + st.session_state.system_format + "\n\nUse the enclosed SYSTEM_FILES as context.\n\nSYSTEM_FILES:\n{SYSTEM_FILES}\n\"\"\"\n"
    st.session_state.user_prompt = "\"\"\"\n{PRIMING} \n\n{QUESTION}\n\n{DECORATION}\n\nCONTEXT_FILES:\n\n{CONTEXT_FILES}\n\"\"\" "
    st.session_state.example_user_prompt = "{PRIMIMG} = I run the command ping notexistingsite.com \n{QUESTION} = I get the error ping: cannot resolve notexistingsite.com: Unknown host. What is the error?\n{DECORATION} = Insert comments and examples."


def text_audit_and_qualify():
    st.session_state.system_persona = "You are a code assistant who reviews the code."
    st.session_state.system_context = "The user searches for issues, risks and threads, as well as quality issues."
    st.session_state.system_instructions = "Your task is to review the code, identify problems and suggest improvements."
    st.session_state.system_tone = "Suggest consistent and proven solutions."
    st.session_state.system_format = "Write the result as text or a code snippet. Give examples."
    st.session_state.system_custom = "\"\"\"\n" + st.session_state.system_persona + " " + st.session_state.system_context + " " + st.session_state.system_instructions + " " + st.session_state.system_tone + " " + st.session_state.system_format + "\n\nUse the enclosed SYSTEM_FILES as context.\n\nSYSTEM_FILES:\n{SYSTEM_FILES}\n\"\"\"\n"
    st.session_state.user_prompt = "\"\"\"\n{PRIMING} \n\n{QUESTION}\n\n{DECORATION}\n\nCONTEXT_FILES:\n\n{CONTEXT_FILES}\n\"\"\" "
    st.session_state.example_user_prompt = "{PRIMIMG} = I want to audit the code which is in the CONTEXT_FILES.\n{QUESTION} = What are the most serious security issues?\n{DECORATION} = Insert comments and examples"


def initialize_session_parameters():
    st.session_state.context = "init"
    st.session_state.chosen_id = "1"
    st.session_state.gemini15 = "True"
    st.session_state.openai4o = "True"
    st.session_state.temperature_Flash = 0.1
    st.session_state.max_tokens_Flash = 2048
    st.session_state.top_p_Flash = 1.0
    st.session_state.top_k_Flash = 32
    st.session_state.temperature_gpt = 0.1
    st.session_state.max_tokens_gpt = 2048
    st.session_state.top_p_gpt = 1.0
    st.session_state.prompt_type = "Default"
    st.session_state.prompt_index = 0
    st.session_state.model_index = 0
    st.session_state.model_type = "Gemini"
    st.session_state.input_priming = ""
    st.session_state.input_question = ""
    st.session_state.input_decoration = ""
    st.session_state.uploaded_files1 = ""
    st.session_state.uploaded_files2 = ""
    st.session_state.user_prompt_sent_gemini = 0
    st.session_state.user_prompt_sent_gpt = 0
    st.session_state.selectbox = "Troubleshoot a problem"
    text_troubleshooting()


def sidebar_menus():
    # Using object notation

    st.sidebar.header("AI Assistant")

    selectbox_new_value = st.sidebar.selectbox(
        "What do you want to do?",
        ("Troubleshoot a problem", "Audit and qualify")
    )

    # we chech that the value has been changed from the previous value
    if selectbox_new_value != st.session_state.selectbox:
        st.session_state.selectbox = selectbox_new_value
        if st.session_state.selectbox == "Troubleshoot a problem":
            text_troubleshooting()
        if st.session_state.selectbox == "Audit and qualify":
            text_audit_and_qualify()
        # clear user prompt
        st.session_state.input_priming = ""
        st.session_state.input_question = ""
        st.session_state.input_decoration = "" 
        st.session_state.user_prompt = "\"\"\"\n{PRIMING} \n\n{QUESTION}\n\n{DECORATION}\n\nCONTEXT_FILES:\n\n{CONTEXT_FILES}\n\"\"\" "          
        # clear chat history
        if "chat" in st.session_state:
            del st.session_state.chat
        if "messages" in st.session_state:
            del st.session_state.messages

    # Select the page
    with st.sidebar:
        st.session_state.chosen_id = st.radio(
            "Steps to complete:",
            ("1 Models selection","2 System prompt", "3 User prompt", "4 Chat","5 Info"),
            index=0
        )   

    if st.session_state.chosen_id == "4 Chat" and st.session_state.gemini15 and st.session_state.openai4o:
        with st.sidebar:
            st.session_state.model_type = st.radio(
                "Select active chat window: \n\n",
                options=["Gemini", "GPT-4o"],
                index=st.session_state.model_index,
                key=50,
                horizontal=True,
            )

    if st.session_state.chosen_id == "4 Chat":
        with st.sidebar:
            if st.button("Clear Chat history", type="primary"):
                if "chat" in st.session_state:
                    del st.session_state.chat
                if "messages" in st.session_state:
                    del st.session_state.messages

    with st.sidebar:
        uploaded_side_files1 = st.file_uploader("Import files for system prompt, {SYSTEM_FILES}", accept_multiple_files=True, key=23)
        if uploaded_side_files1 != []:
            st.session_state.uploaded_files1 = ""
            for uploaded_side_file1 in uploaded_side_files1:
                st.session_state.uploaded_files1 = st.session_state.uploaded_files1 + "File: " + uploaded_side_file1.name + "\n\nContent: " + "\n" + uploaded_side_file1.getvalue().decode("utf-8") + "\n"
        else:
            st.session_state.uploaded_files1 = ""

    with st.sidebar:
        uploaded_side_files2 = st.file_uploader("Import relevant context files, {CONTEXT_FILES}", accept_multiple_files=True, key=24)
        if uploaded_side_files2 != []:
            st.session_state.uploaded_files2 = ""
            for uploaded_side_file2 in uploaded_side_files2:
                st.session_state.uploaded_files2 = st.session_state.uploaded_files2 + "File: " + uploaded_side_file2.name + "\n\nContent: " + "\n" + uploaded_side_file2.getvalue().decode("utf-8") + "\n"
        else:
            st.session_state.uploaded_files2 = ""


def models_selection():

    st.header("1. Models selection", divider="rainbow")
    st.subheader("Choose models and give model parameters")

    st.write('Select LLM models you want to use:')
    st.session_state.gemini15 = st.checkbox("Gemini 1.5 Flash", value=st.session_state.gemini15)
    st.session_state.openai4o = st.checkbox("OpenAI GPT-4o", value=st.session_state.openai4o)

    if st.session_state.gemini15:
        st.subheader("Gemini 1.5 Flash parameters")
        st.session_state.temperature_Flash = st.slider("Temperature", min_value=0.0, max_value=2.0, value=st.session_state.temperature_Flash, step=0.1,key=18)
        st.session_state.top_p_Flash = st.slider("Top_p", min_value=0.0, max_value=1.0, value=st.session_state.top_p_Flash, step=0.1,key=118)
        st.session_state.top_k_Flash = st.slider("Top_k", min_value=1, max_value=40, value=st.session_state.top_k_Flash, step=1,key=128)
        st.session_state.max_tokens_Flash = st.slider("Max output tokens", min_value=1, max_value=8192, value=st.session_state.max_tokens_Flash, step=1,key=138)

    if st.session_state.openai4o:
        st.subheader("OpenAI GPT-4o parameters")
        st.session_state.temperature_gpt = st.slider("Temperature", min_value=0.0, max_value=2.0, value=st.session_state.temperature_gpt, step=0.1,key=19)          
        st.session_state.top_p_gpt = st.slider("Top_p", min_value=0.0, max_value=1.0, value=st.session_state.top_p_gpt, step=0.1,key=218)
        st.session_state.max_tokens_gpt = st.slider("Max output tokens", min_value=1, max_value=4096, value=st.session_state.max_tokens_gpt, step=1,key=17)           

    if not st.session_state.gemini15 and not st.session_state.openai4o:
        st.session_state.gemini15 = True
    if st.session_state.gemini15:
        st.session_state.model_type = "Gemini"
    if st.session_state.openai4o:
        st.session_state.model_type = "GPT-4o"
    if st.session_state.gemini15 and st.session_state.openai4o:
        st.session_state.model_type = "Gemini"


def create_system_prompt():
        
    st.header("2. System prompt", divider="rainbow")
    st.subheader("Define system prompt")
    st.text("Use Ctrl+Enter (or Enter) to save changes.")

    st.session_state.prompt_type = st.radio(
        "Select system prompt type: \n\n",
        options=["Default", "Custom"],
        index=st.session_state.prompt_index,
        key=20,
        horizontal=True,
    )

    if st.session_state.prompt_type == "Default":
        st.session_state.prompt_index = 0
        st.session_state.system_persona = st.text_area(
            "System persona", value=st.session_state.system_persona, height=100, key=1
        )

        st.session_state.system_context = st.text_area(
            "System context", value=st.session_state.system_context, height=100, key=2
        )

        st.session_state.system_instructions = st.text_area(
            "System instructions", value=st.session_state.system_instructions, height=100, key=3
        )

        st.session_state.system_tone = st.text_area(
            "System tone", value=st.session_state.system_tone, height=100, key=4
        )

        st.session_state.system_format = st.text_area(
            "System format", value=st.session_state.system_format, height=100, key=5
        )
    else:
        st.session_state.prompt_index = 1
        st.session_state.system_custom = st.text_area(
            "Custom system prompt", value=st.session_state.system_custom, height=500, key=1
        )          
    

def create_user_prompt():
        
    st.header("3. User prompt", divider="rainbow")
    st.subheader("Create a prompt template")
    st.text("Use Ctrl+Enter to save changes.")

    st.session_state.user_prompt = st.text_area(
        "User prompt", value=st.session_state.user_prompt, height=260, key=10
    )

    if st.button("Send User prompt to model", type="primary"):
        st.text("Prompt sent. Chat screen shows the answer and you can talk with your documents.")
        # set a flag that models will create responses to the user prompt
        st.session_state.user_prompt_sent_gemini = 1
        st.session_state.user_prompt_sent_gpt = 1

    st.session_state.input_priming = st.text_area(
        "Write here the context what you are doing, {PRIMING}", value=st.session_state.input_priming, height=100, key=11
    )

    st.session_state.input_question = st.text_area(
        "Write here the question or action you want to make, {QUESTION}", value=st.session_state.input_question, height=100, key=12
    )

    st.session_state.input_decoration = st.text_area(
        "What additional things you want the model to do, {DECORATION}", value=st.session_state.input_decoration, height=100, key=13
    )       

    st.text("Example of prompt:")
    st.text(st.session_state.example_user_prompt)    


def role_to_streamlit(role):
  if role == "model":
    return "assistant"
  else:
    return role

def gemini_model():

    # select chat window as Gemini
    st.session_state.model_index = 0
    st.header("4. Chat - Gemini", divider="rainbow")       
    st.subheader("Here you can chat with your data and files")

    # chat page is opened first time or chat history has been cleared
    if "chat" not in st.session_state:
        # default system prompt
        if st.session_state.prompt_index == 0:
            system_template = "\"\"\"\n" + st.session_state.system_persona + " " + st.session_state.system_context + " " + st.session_state.system_instructions + " " + st.session_state.system_tone + " " + st.session_state.system_format + "\n\nUse the enclosed SYSTEM_FILES as context.\n\nSYSTEM_FILES:\n{SYSTEM_FILES}\n\"\"\"\n"
            sys_instructions = system_template.format(SYSTEM_FILES=st.session_state.uploaded_files1)
        # custom system prompt
        if st.session_state.prompt_index == 1:
            system_template = st.session_state.system_custom
            sys_instructions = system_template.format(SYSTEM_FILES=st.session_state.uploaded_files1)
        # initialize gemini
        vertexai.init(project=GEMINI_PROJECT, location=GEMINI_LOCATION)
        model = GenerativeModel(GEMINI_MODEL,system_instruction=[sys_instructions]) 
        # clear chat history
        st.session_state.chat = model.start_chat(history = [])

    # Show chat messages from history
    for message in st.session_state.chat.history:
        with st.chat_message(role_to_streamlit(message.role)):
            if message.role == "user":
                st.text(message.parts[0].text)
            else:
                st.markdown(message.parts[0].text)   

    # user has created user prompt and pressed "Send" button
    if st.session_state.user_prompt_sent_gemini == 1:
        prompt_template = st.session_state.user_prompt
        # fill in the prompt template
        user_prompt = prompt_template.format(PRIMING=st.session_state.input_priming,
                                            QUESTION=st.session_state.input_question,
                                            DECORATION=st.session_state.input_decoration,
                                            CONTEXT_FILES=st.session_state.uploaded_files2)
        st.chat_message("user").text(user_prompt)
        generation_config = {
                "max_output_tokens" : st.session_state.max_tokens_Flash,
                "temperature" : st.session_state.temperature_Flash,
                "top_p" : st.session_state.top_p_Flash,
                "top_k" : st.session_state.top_k_Flash
            }
        # create response to prompt template of user prompt
        response = st.session_state.chat.send_message(user_prompt, generation_config=generation_config) 
        with st.chat_message("assistant"):
            st.markdown(response.text)
        # clear the flag that user prompt has been created
        st.session_state.user_prompt_sent_gemini = 0

        # chat with your documents, ask a question
    if prompt := st.chat_input("What would you like to know?"):
        st.chat_message("user").text(prompt)
                
        generation_config = {
                "max_output_tokens" : st.session_state.max_tokens_Flash,
                "temperature" : st.session_state.temperature_Flash,
                "top_p" : st.session_state.top_p_Flash,
                "top_k" : st.session_state.top_k_Flash
            }

     #     create response to the question and store response to session data
        response = st.session_state.chat.send_message(prompt, generation_config=generation_config)  
                
    # Display the response
        with st.chat_message("assistant"):
            st.markdown(response.text)    


def gpt_model():

    # select chat window as GPT
    st.session_state.model_index = 1
    st.header("4. Chat - GPT-4o", divider="rainbow")       
    st.subheader("Here you can chat with your data and files")  

    # if first time opening this chat page or chat history is cleared
    if "messages" not in st.session_state:
        # default system messsage
        if st.session_state.prompt_index == 0:
            system_template = "\"\"\"\n" + st.session_state.system_persona + " " + st.session_state.system_context + " " + st.session_state.system_instructions + " " + st.session_state.system_tone + " " + st.session_state.system_format + "\n\nUse the enclosed SYSTEM_FILES as context.\n\nSYSTEM_FILES:\n{SYSTEM_FILES}\n\"\"\"\n"
            sys_instructions = system_template.format(SYSTEM_FILES=st.session_state.uploaded_files1)
        # custom system message
        if st.session_state.prompt_index == 1:
            system_template = st.session_state.system_custom
            sys_instructions = system_template.format(SYSTEM_FILES=st.session_state.uploaded_files1)
        # initialize openai client
        st.session_state.client = OpenAI(api_key=OPENAI_API_KEY)

        # clear chat and message history
        st.session_state.messages = []
        # add the system message as the first message
        st.session_state.messages.append(
                {
                    "role": "system", 
                    "content": sys_instructions
                }
            )

        # show chat history
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.text(message["content"])
                else:
                    st.markdown(message["content"])  

    # user has created a user prompt and pressed Send to the model button
    if st.session_state.user_prompt_sent_gpt == 1:
        prompt_template = st.session_state.user_prompt
        # user prompt is created using the prompt template
        user_prompt = prompt_template.format(PRIMING=st.session_state.input_priming,
                                                 QUESTION=st.session_state.input_question,
                                                 DECORATION=st.session_state.input_decoration,
                                                 CONTEXT_FILES=st.session_state.uploaded_files2)
        # user prompt is added to message history
        st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": user_prompt
                }
            )
        st.chat_message("user").text(user_prompt)
 
        response = st.session_state.client.chat.completions.create(
                model = "gpt-4o-2024-05-13",
                messages = st.session_state.messages,
                temperature = st.session_state.temperature_gpt,
                max_tokens = st.session_state.max_tokens_gpt,
                top_p = st.session_state.top_p_gpt)
        # response to prompt template is created
        response_text = response.choices[0].message.content
        st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text
                })
                
        # response is shown
        with st.chat_message("assistant"):
            st.markdown(response_text)
        # user prompt template has been processed and the flag can be cleared
        st.session_state.user_prompt_sent_gpt = 0

        # user can chat with the documents
    if prompt := st.chat_input("What would you like to know?"):
        # show user's last message
        st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": prompt
                }
            )
        st.chat_message("user").markdown(prompt)
        
        # response to the question is generated
        response = st.session_state.client.chat.completions.create(
                model = GPT_MODEL,
                messages = st.session_state.messages,
                temperature = st.session_state.temperature_gpt,
                max_tokens = st.session_state.max_tokens_gpt,
                top_p = st.session_state.top_p_gpt)
        response_text = response.choices[0].message.content
        st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text
                })
                
        # show the answer
        with st.chat_message("assistant"):
            st.markdown(response_text)


def info():

    st.header("5. Info", divider="rainbow")       
    st.subheader("Instructions for usage")

    st.write("1. First select the main action from the left sidebar dropdown list:\n- Troubleshoot a problem\n- Audit and qualify (these items can be added)")
    st.write("2. Select the LLM Models and define their parameters from the left sidebar.")
    st.write("3. Check the system prompt or define your own custom prompt (from the left sidebar). You may add a file in the text format {SYSTEM_FILES} to your system prompt.")
    st.write("4. Now you can already go to Chat panel and start chatting.")
    st.write("5. Alternatively, you may define an User prompt using a prompt template and send this prompt to both models, from the left sidebar. You may add an additional file in the text format {CONTEXT_FILES} that is added to prompt template.")
    st.write("6. Note, that only the contents of the \"User Prompt\" window are sent to the models. You can edit the content as you wish.")
    st.write("7. User prompt (prompt template) is always sent to both models. The responses and additional chatting is made within each model separately.")

def streamlit_ui():

    if "context" not in st.session_state:
        initialize_session_parameters()

    sidebar_menus()

    if st.session_state.chosen_id == "1 Models selection":
        models_selection()
 
    if st.session_state.chosen_id == "2 System prompt":
        create_system_prompt()
  
    if st.session_state.chosen_id == "3 User prompt":
        create_user_prompt()

    if st.session_state.chosen_id == "4 Chat" and st.session_state.model_type == "Gemini":
        gemini_model()

    if st.session_state.chosen_id == "4 Chat" and st.session_state.model_type == "GPT-4o":
        gpt_model()

    if st.session_state.chosen_id == "5 Info":
        info()
