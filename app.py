# ============================================
# RAG SYSTEM WITH FAISS + LANGCHAIN + OPENAI
# ============================================

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import hashlib
import pickle

class AdTechRAG:
    """Complete RAG system using FAISS + LangChain + OpenAI"""
    
    def __init__(self, api_key=None):
        # Initialize OpenAI
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key or st.secrets.get("OPENAI_API_KEY")
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # or "gpt-4"
            temperature=0.3,
            openai_api_key=api_key or st.secrets.get("OPENAI_API_KEY")
        )
        self.vectorstore = None
        self.retriever = None
        
    def load_and_index_documents(self, knowledge_base, kb_dir="./kb"):
        """
        Load documents from knowledge base and create FAISS index
        This is the core RAG indexing step
        """
        documents = []
        
        # Convert your existing knowledge_base dict to LangChain Documents
        for doc_key, content in knowledge_base.items():
            if content:
                # Create Document object
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": doc_key,
                        "type": "adtech_playbook",
                        "filename": f"{doc_key}.md"
                    }
                )
                documents.append(doc)
        
        # Also load raw markdown files if they exist
        if Path(kb_dir).exists():
            for file_path in Path(kb_dir).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": file_path.stem,
                            "type": "playbook",
                            "filename": file_path.name
                        }
                    )
                    documents.append(doc)
        
        # Split documents into chunks (important for retrieval quality)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # Size of each chunk
            chunk_overlap=200,     # Overlap between chunks (maintains context)
            separators=["\n## ", "\n### ", "\n\n", "\n", " "]
        )
        
        split_docs = text_splitter.split_documents(documents)
        st.info(f"📚 Created {len(split_docs)} document chunks from {len(documents)} playbooks")
        
        # Create FAISS vector store - THIS IS THE VECTOR DATABASE
        self.vectorstore = FAISS.from_documents(
            split_docs,
            self.embeddings
        )
        
        # Create retriever with search_kwargs (the parameter you asked about!)
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",  # Type of search
            search_kwargs={"k": 3}      # k = number of documents to retrieve
        )
        
        return len(split_docs)
    
    def save_index(self, path="./faiss_index"):
        """Save FAISS index to disk for reuse"""
        if self.vectorstore:
            self.vectorstore.save_local(path)
            st.success(f"💾 FAISS index saved to {path}")
    
    def load_index(self, path="./faiss_index"):
        """Load pre-built FAISS index"""
        if Path(path).exists():
            self.vectorstore = FAISS.load_local(
                path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            )
            return True
        return False
    
    def retrieve_context(self, query):
        """
        Retrieve relevant documents from FAISS
        This is the retrieval step in RAG
        """
        if not self.retriever:
            return []
        
        docs = self.retriever.invoke(query)
        
        # Display which documents were retrieved (for debugging)
        for i, doc in enumerate(docs):
            st.caption(f"📄 Retrieved chunk {i+1}: {doc.metadata.get('source', 'unknown')}")
        
        return docs
    
    def generate_recommendations_rag(self, df, query):
        """
        Complete RAG pipeline:
        1. Calculate statistics from CSV
        2. Retrieve relevant context from FAISS
        3. Generate response with OpenAI
        """
        
        # Step 1: Extract data insights from CSV
        campaign_stats = self._extract_campaign_stats(df)
        
        # Step 2: Retrieve relevant documents from FAISS
        retrieved_docs = self.retrieve_context(query)
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Step 3: Build prompt with CSV data + Retrieved context
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AdTech optimization consultant with 10+ years experience.
            
            CONTEXT FROM KNOWLEDGE BASE (AdTech best practices, optimization frameworks):
            {context}
            
            CAMPAIGN PERFORMANCE DATA:
            {campaign_data}
            
            Your task: Provide actionable, specific recommendations based on the data and best practices.
            Focus on:
            - Diagnosing root causes of underperformance
            - Providing specific, implementable actions
            - Prioritizing recommendations (High/Medium/Low impact)
            - Including expected lift/improvement metrics
            """),
            ("human", "{question}")
        ])
        
        # Step 4: Generate response using LangChain's LCEL (new syntax)
        chain = (
            {
                "context": lambda x: context,
                "campaign_data": lambda x: campaign_stats,
                "question": lambda x: x["question"]
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        response = chain.invoke({"question": query})
        
        return response, retrieved_docs
    
    def _extract_campaign_stats(self, df):
        """Extract meaningful statistics from CSV for the prompt"""
        stats = []
        
        # Overall metrics
        if 'spend' in df.columns:
            stats.append(f"Total Spend: ${df['spend'].sum():,.2f}")
        if 'ctr' in df.columns:
            stats.append(f"Average CTR: {df['ctr'].mean():.2f}%")
            stats.append(f"CTR Range: {df['ctr'].min():.2f}% - {df['ctr'].max():.2f}%")
        if 'cpc' in df.columns:
            stats.append(f"Average CPC: ${df['cpc'].mean():.3f}")
        if 'conversions' in df.columns:
            stats.append(f"Total Conversions: {df['conversions'].sum():,.0f}")
        if 'cpa' in df.columns and not df['cpa'].isna().all():
            stats.append(f"Average CPA: ${df['cpa'].mean():.2f}")
            stats.append(f"Best CPA: ${df['cpa'].min():.2f}")
        
        # Performance by segment
        if 'audience_segment' in df.columns and 'cpa' in df.columns:
            best_segment = df.groupby('audience_segment')['cpa'].mean().idxmin()
            worst_segment = df.groupby('audience_segment')['cpa'].mean().idxmax()
            stats.append(f"Best performing audience: {best_segment}")
            stats.append(f"Worst performing audience: {worst_segment}")
        
        # Top/bottom campaigns
        if 'campaign_name' in df.columns and 'ctr' in df.columns:
            top_ctr = df.nlargest(3, 'ctr')['campaign_name'].tolist()
            stats.append(f"Top CTR campaigns: {', '.join(top_ctr)}")
        
        return "\n".join(stats)
    
    def chat_with_campaign(self, df, user_question):
        """Interactive chat using RAG"""
        return self.generate_recommendations_rag(df, user_question)

# ============================================
# MODIFIED MAIN FUNCTION WITH RAG
# ============================================

def main_with_rag():
    """New main function with RAG integration"""
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Load knowledge base from files
    knowledge_base = load_knowledge_base()
    
    # Display upload interface
    uploaded_file = display_minimal_upload()
    
    # Process file when uploaded
    if uploaded_file is not None:
        try:
            # Read and process CSV
            df = pd.read_csv(uploaded_file)
            df = calculate_kpis(df)
            
            # Initialize RAG system
            if st.session_state.rag_system is None:
                with st.spinner("🔧 Initializing RAG system with FAISS + LangChain..."):
                    rag = AdTechRAG()
                    
                    # Try to load existing index, or create new one
                    if not rag.load_index():
                        st.info("📚 Building FAISS index from knowledge base documents...")
                        rag.load_and_index_documents(knowledge_base)
                        rag.save_index()  # Save for next time
                    
                    st.session_state.rag_system = rag
            
            # Store in session state
            st.session_state.df = df
            st.session_state.data_loaded = True
            
            # Display dashboard (your existing function)
            display_rich_dashboard(df, generate_recommendations(df, knowledge_base))
            
            # NEW: RAG Chat Section
            st.markdown("---")
            st.subheader("🤖 AI Consultant Chat (Powered by RAG + FAISS)")
            st.caption("Ask questions about your campaign data - the AI will retrieve relevant AdTech best practices from our knowledge base")
            
            # Chat input
            user_question = st.text_input(
                "Ask a question:",
                placeholder="e.g., 'Why is my CTR low in France?' or 'How can I improve CPA for 18-24 segment?'"
            )
            
            if user_question:
                with st.spinner("🔍 Retrieving relevant documents from FAISS + Generating response with OpenAI..."):
                    response, retrieved_docs = st.session_state.rag_system.chat_with_campaign(df, user_question)
                    
                    # Store in history
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("assistant", response))
                    
                    # Display response
                    st.markdown("### 💡 AI Response")
                    st.markdown(response)
                    
                    # Optionally show retrieved documents
                    with st.expander("🔍 View retrieved context from FAISS"):
                        for i, doc in enumerate(retrieved_docs):
                            st.markdown(f"**Document {i+1}:** {doc.metadata.get('source', 'unknown')}")
                            st.text(doc.page_content[:500] + "...")
                            st.markdown("---")
            
            # Display chat history
            if st.session_state.chat_history:
                with st.expander("📝 Chat History", expanded=False):
                    for role, msg in st.session_state.chat_history:
                        if role == "user":
                            st.markdown(f"**You:** {msg}")
                        else:
                            st.markdown(f"**AI:** {msg}")
                        st.markdown("---")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.data_loaded = False
    
    else:
        st.session_state.data_loaded = False
