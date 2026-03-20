import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

#step 1: Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
#Load the vector database
db = Chroma(
    persist_directory="../vectorstore",
    embedding_function=embeddings
)

#Load model
llm = OllamaLLM(model = "phi")

#UI Title
st.title("🚗 EV Diagnostic Assistant")

#Ask a question
query = st.text_input("Ask your EV question: ")

#Input box
if st.button("Get Answer"):

     if query.strip() == "":
        st.warning("Please enter a question first!")
     else:
         with st.spinner("Thinking... ⏳"):
             docs = db.similarity_search(query, k=3)

             if len(docs)==0:
                 st.error("No relevant information found in the database.")
             else:
               context = ""
               sources = []

             for doc in docs:
                context += doc.page_content + "\n\n"
                page = doc.metadata.get("page", "N/A")
                sources.append(f"Page {page}")

             prompt = f"""
             You are an EV diagnostic assistant.

             Answer ONLY based on context.
             Give clear steps.

             Context:
             {context}

             Question: {query}
            
             Answer clearly:
             """

             response = llm.invoke(prompt).strip()
             response = "\n".join(response.split("\n")[:5])  # Limit to 3 lines

             st.subheader("AI Answer:")
             st.write(response)

             st.subheader("Sources:")
             for s in sources:
                 st.write(s)

