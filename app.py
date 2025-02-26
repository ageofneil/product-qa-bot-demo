import streamlit as st
import difflib
import pandas as pd
import numpy as np
from annoy import AnnoyIndex
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Load Q&A Data
df_qa = pd.read_csv("qa_data.csv")

# Create product mapping (id -> name)
product_mapping = df_qa[['product_id', 'product_name']].drop_duplicates().set_index("product_id").to_dict()["product_name"]

# Create dictionary mapping product_id to Q&A indices
product_id_to_indices = {product_id: df_qa[df_qa["product_id"] == product_id].index.tolist()
                         for product_id in df_qa["product_id"].unique()}

# Load Annoy index
embedding_dim = 1536  # Based on OpenAI model output
annoy_index = AnnoyIndex(embedding_dim, "euclidean")
annoy_index.load("qa_embeddings.ann")

# Function to generate query embedding
def generate_query_embedding(query):
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-ada-002"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# Function to search for relevant Q&A
def search_product_faq(query, product_id, top_k=1, threshold=0.55):
    query_embedding = generate_query_embedding(query)

    if product_id not in product_id_to_indices:
        return None, None

    filtered_indices = product_id_to_indices[product_id]
    if not filtered_indices:
        return None, None

    # Perform Annoy search
    all_indices, distances = annoy_index.get_nns_by_vector(query_embedding, len(df_qa), include_distances=True)

    for idx, dist in zip(all_indices, distances):
        if idx in filtered_indices:
            match = df_qa.iloc[idx]
            text_similarity = difflib.SequenceMatcher(None, query.lower(), match["question"].lower()).ratio()
            
            if dist > threshold or text_similarity < 0.5:
                return None, None
            
            return match["question"], match["answer"]

    return None, None

# Function to generate chatbot response
def generate_conversational_answer(user_query, product_id):
    matched_question, matched_answer = search_product_faq(user_query, product_id)

    if matched_question is None:
        return "I'm not sure about that. Please check the product details for more info!"

    # Generate conversational response
    prompt = f"""
    A customer asked: "{user_query}" about {product_mapping[product_id]}
    
    The closest matching question we found: "{matched_question}"
    
    Answer: "{matched_answer}"
    
    Rephrase this answer to be **short, friendly, and conversational**.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a friendly, knowledgeable product expert."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("🛥️ Product Q&A Chatbot")

# Select Product (show name instead of ID)
product_names = list(product_mapping.values())
product_ids = list(product_mapping.keys())
selected_product_name = st.selectbox("Select a product:", product_names)
selected_product_id = product_ids[product_names.index(selected_product_name)]

# Show available questions for this product
st.subheader(f"💡 Question Space for: {selected_product_name}")
st.write("If your question is related to the ones listed below, an answer will be provided. If not, you'll receive a generic response.")
available_questions = df_qa[df_qa["product_id"] == selected_product_id]["question"].tolist()
for q in available_questions:
    st.markdown(f"- **{q}**")

# User Input
user_query = st.text_input("Ask a question about the product:")

if st.button("Get Answer"):
    if user_query.strip():
        response = generate_conversational_answer(user_query, selected_product_id)
        st.markdown(f"**🗣️ Answer:** {response}")
    else:
        st.warning("Please enter a question.")
