# Ask.AI
A highly Interactive RAG system that uses Large Language Models (LLMs) to process natural language queries and retrieve relevant information from large unstructured documents such as policy documents, and contracts.

### Features

#### (i)Parsed Query:
Input documents may include PDFs, or Word files. It Parse and structure the query to identify key details such as age, procedure, location, and policy duration even if the query is vague, incomplete, or written in plain English.

#### (ii) Semantic Search:
Search and retrieve relevant clauses or rules from the provided documents using semantic understanding rather than simple keyword matching.

#### (iii) Highly efficienct decision Engine:
Evaluate the retrieved information to determine the correct decision, such as approval status or payout amount, based on the logic defined in the clauses.

#### (iv) Structured Output:
Return a structured JSON response containing: Decision (e.g., approved or rejected), Amount (if applicable), and Justification, including mapping of each decision to the specific clause(s) it was based on. The output is consistent, interpretable, and usable for downstream applications such as claim processing or audit tracking.


### Applications:
This system can be applied in domains such as insurance, legal compliance, human resources, and contract management.


### Colab Notebook
https://colab.research.google.com/drive/17NtC-wSuWV8QJFPD6P52n5qerT2eLqyk

### Setup

Follow the steps below to set up and run the Query.AI project:

1. Clone the repository:
   ```bash
   git clone https://github.com/Mayank2177/Ask.ai.git
   ```

2. Install the required dependencies:
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

3. Add your configuration files:
   Place any necessary configuration files (e.g., `.env` files) in the project directory.
      ```bash
   export GEMINI_API_KEY=your_gemini_api_key_here
   export MILVUS_TOKEN= <your_milvus_api_key>
   export LANGSMITH_API_KEY=<your_langsmith_api_key>

   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
   or
      ```bash
   python main.py
   ```

Ensure you have Python and any other required tools installed before proceeding with the setup.
