# A Basic Bot that Answers Product Questions

This app is a basic demo of an AI-driven product Q&A system, inspired by Amazon's AI assistant on product pages. It allows users to ask product-related questions and receive AI-generated responses based on pre-trained data.

Demo: https://appuct-app-bot-demo-lcvxuqfhe5ranq3m9skqdc.streamlit.app/

### How It Works**
1. **Uses the Product ID to Define the Search Space**  
   When a user is browsing a product page, the app uses its **product ID** to filter the search space. 

2. **Searches User Query for the Best Match**  
   The app takes the user’s question, converts it into an embedding, and searches for the most relevant match within the FAQ dataset specific to the product ID.  

3. **Generates & Outputs a Response**  
   - If a close match is found, a **contextual response** based on available information is given, helping guide the user toward relevant details. 
   - If no close match exists, the app provides the **pre-written answer**.  


![Amazon's AI Shopping Assistant](https://www.zdnet.com/a/img/resize/bfe0cf812fbd870450216fcab47130ad220d2f36/2024/01/18/bcdfae7e-45ae-4ca1-b893-7940307251ac/figure-1-amazons-new-generative-ai-bot-will-answer-your-questions-as-you-shop-for-products.png?auto=webp&width=1280)



