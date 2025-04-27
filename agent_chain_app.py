import streamlit as st
import openai
from typing import Dict, Any, List
import json
from datetime import datetime
import time
import os

# Corporate Identity
AUTHOR = "Dirk Wonhoefer"
COMPANY = "AI Engineering"
EMAIL = "dirk.wonhoefer@ai-engineering.ai"
WEBSITE = "ai-engineering.ai"

# Define the 11 research categories from DetectiveGPT
CATEGORIES = [
    "Company Overview and History",
    "Products and Services",
    "Market Position and Competitors",
    "Financial Status and Business Figures",
    "Company Culture and Employees",
    "Sustainability and CSR Activities",
    "Latest News and Developments",
    "Legal Matters and Compliance",
    "Technology and Innovation",
    "Customer Reviews and Reputation",
    "Defense-Specific Information"
]

# Define the default prompts for each category
DEFAULT_PROMPTS = [
    """Analyze the company overview and history of {company_name}.
Research: Year of foundation, founders, key milestones, company mission and vision, headquarters and international presence.
Consider the following criteria for your analysis:
- Company size (larger companies with more resources are preferred)
- Age and stability (established companies with stable history)
- Location (primary focus) or with strong presence
- Connections to the defense industry
- Growth dynamics (expanding companies likely have new needs)
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the products and services of {company_name}.
Research: Main product lines, key services, pricing models (if available), newly introduced offerings and unique selling points.
Consider the following criteria for your analysis:
- Products requiring metal processing (especially cutting/sawing)
- Types of materials being processed (compatibility with cutting blades)
- Production volume (higher volume means more need for consumables)
- Diversity of product line (diverse products need different types of cutting blades)
- Quality standards of products (high-quality products require precise cuts)
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the market position and competitors of {company_name}.
Research: Market share (if available), positioning compared to competitors, direct and indirect competitors, industry trends.
Consider the following criteria for your analysis:
- Market position (market leaders often have higher quality requirements)
- Competitive strategy (quality leadership requires better tools)
- Market growth in relevant segments
- Specialization in niches requiring precise metal processing
- Influence on the supply chain (can help reach additional customers)
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the financial status and business figures of {company_name}.
Research: Revenue, profit, growth rates, investments, funding rounds or stock price development.
Consider the following criteria for your analysis:
- Financial stability and solvency
- Investments in production facilities/equipment
- Budgets for operating resources and tools
- Growth rate (growing companies invest more)
- Profitability (better margins allow investments in quality tools)
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the company culture and employees of {company_name}.
Research: Company values, employer brand, number of employees and growth, working conditions, training opportunities.
Consider the following criteria for your analysis:
- Focus on quality and precision in company culture
- Innovation culture and openness to new solutions
- Technical expertise of workforce
- Decision-making processes and procurement policy
- Appreciation of supplier relationships
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the sustainability and CSR activities of {company_name}.
Research: Environmental initiatives, social engagement, ethical business practices, sustainability reports, certifications.
Consider the following criteria for your analysis:
- Sustainability goals requiring more efficient production processes
- Resource efficiency (durable cutting blades reduce waste)
- Compliance with environmental regulations
- Willingness to invest in sustainable production technologies
- Quality certifications requiring precise manufacturing processes
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze the latest news and developments of {company_name}.
Research: Important announcements, product launches, acquisitions or mergers, leadership changes, partnerships.
Consider the following criteria for your analysis:
- Expansion or new projects requiring metal processing
- Realignment of product lines or market entry into new segments
- Technological changes or production modernizations
- Acquisition of new orders, especially in the defense sector
- Strategic partnerships favoring new supplier relationships
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze legal matters and compliance at {company_name}.
Research: Current or past litigation, regulatory challenges, compliance programs, data protection policies.
Consider the following criteria for your analysis:
- Compliance with quality and safety standards
- Regulatory requirements requiring precise manufacturing
- Supply chain transparency
- Certifications for defense contracts
- Stability of legal situation (less risk for business relationships)
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze technology and innovation at {company_name}.
Research: Core technologies, R&D activities, patents, technological unique selling points, digital transformation.
Consider the following criteria for your analysis:
- Use of modern manufacturing technologies
- Material innovations that might require special cutting blades
- R&D focus on new materials or production processes
- Degree of automation in manufacturing
- Technology leadership in relevant areas
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze customer reviews and reputation of {company_name}.
Research: Customer feedback on various platforms, product reviews, customer satisfaction indicators.
Consider the following criteria for your analysis:
- Customer feedback on product quality (high quality standards)
- Reputation for precision and reliability
- Relationships with existing customers/suppliers
- Complaints about current manufacturing processes or quality
- Brand reputation and positioning
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources.""",

    """Analyze defense-specific information about {company_name}.
Research: Defense contracts and projects, military certifications, relationships with governments and defense ministries, participation in defense trade shows.
Consider the following criteria for your analysis:
- Type and scope of defense contracts
- Materials used in defense projects
- Specific requirements for metal processing
- Existing suppliers for metal processing tools
- Participation in relevant defense trade shows and conferences
Website: {website}

Use your browser tool and python to conduct your online research. Always cite all sources."""
]

# Final report prompt
FINAL_REPORT_PROMPT = """Create a comprehensive final report based on all the analyses conducted for {company_name}.
This report should include:
1. A summary of the most important findings from all 11 research categories
2. An overall matching score based on the evaluation of all categories
3. Identification of the three most promising entry points for a business relationship
4. Recommendation of specific products that best match the company's requirements
5. Outline of a potential acquisition strategy with concrete next steps

Company: {company_name}
Website: {website}

The report should highlight the most relevant opportunities and challenges for approaching this company
as a potential customer, focusing on how our premium cutting solutions could meet their specific needs.

Use your browser tool and python to conduct your online research if needed. Always cite all sources.
"""

class BaseAgent:
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        
    def execute(self, prompt: str) -> str:
        try:
            client = openai.OpenAI(api_key=st.session_state.api_key)
            messages = [
                {"role": "user", "content": prompt}
            ]
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error in agent execution: {str(e)}")
            return ""

class AgentChain:
    def __init__(self, agent_prompts: List[str], model_name: str = "gpt-4"):
        self.num_agents = len(agent_prompts)
        self.agents = [BaseAgent(model_name) for _ in range(self.num_agents)]
        self.agent_prompts = agent_prompts
        
    def process_input(self) -> Dict[str, str]:
        results = {}
        
        for i in range(self.num_agents):
            agent_num = i + 1
            st.write(f"🔄 Running analysis for: {CATEGORIES[i]}")
            
            # Get agent prompt
            agent_prompt = self.agent_prompts[i]
            
            # Execute agent
            results[f"agent{agent_num}_output"] = self.agents[i].execute(
                agent_prompt
            )
            st.write(f"✅ Completed: {CATEGORIES[i]}")
        
        return results
    
    def generate_final_report(self, company_name: str, website: str, results: Dict[str, str]) -> str:
        """Generate a final comprehensive report based on all agent outputs"""
        # Create the final report prompt with context from all previous analyses
        final_prompt = FINAL_REPORT_PROMPT.format(
            company_name=company_name,
            website=website
        )
        
        # Add context from all previous analyses
        final_prompt += "\n\nAnalysis results from all categories:\n\n"
        for i in range(self.num_agents):
            final_prompt += f"--- {CATEGORIES[i]} ---\n{results[f'agent{i+1}_output']}\n\n"
        
        # Execute final report agent
        final_agent = BaseAgent()
        return final_agent.execute(final_prompt)

def create_markdown(results: Dict[str, str], company_name: str, website: str, final_report: str = None) -> str:
    markdown = f"""# Company Analysis Report: {company_name}
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Company:** {company_name}  
**Website:** {website}

"""
    
    # Add each agent's output
    for i in range(1, len(results) + 1):
        markdown += f"\n## {CATEGORIES[i-1]}\n{results[f'agent{i}_output']}\n"
    
    # Add final report if available
    if final_report:
        markdown += f"\n## Final Report\n{final_report}\n"
    
    return markdown

def save_configuration(agent_prompts: List[str], company_name: str, website: str, file_name: str) -> tuple[bool, str, str]:
    """Save the current configuration as a downloadable file."""
    try:
        # Prepare configuration data
        config = {
            "company_name": company_name,
            "website": website,
            "agent_prompts": agent_prompts,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Convert to JSON string
        json_str = json.dumps(config, indent=2, ensure_ascii=False)
        
        # Ensure the filename ends with .json
        if not file_name.endswith('.json'):
            file_name += '.json'
            
        # Return the JSON string for download
        return True, json_str, file_name
        
    except Exception as e:
        return False, str(e), ""

def load_configuration(file_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return None

def generate_agent_prompts(company_name: str, website: str) -> List[str]:
    """Generate prompts for all agents based on company name and website"""
    prompts = []
    for prompt_template in DEFAULT_PROMPTS:
        # Format the prompt with the company name and website
        prompt = prompt_template.format(
            company_name=company_name,
            website=website
        )
        prompts.append(prompt)
    return prompts

def main():
    st.set_page_config(
        page_title="Company Analysis Tool",
        page_icon="🔍",
        layout="wide"
    )
    
    # Header with corporate identity
    st.title("🔍 Corporate Intelligence Analysis Tool")
    st.markdown(f"""
    Comprehensive research and analysis of potential customer companies.
    Input company name and website to generate detailed reports across 11 key categories.
    
    ---
    **Created by [{AUTHOR}]({WEBSITE}) | [{COMPANY}]({WEBSITE})**  
    Contact: [{EMAIL}](mailto:{EMAIL})
    """)
    
    # Initialize session state if needed
    if 'agent_prompts' not in st.session_state:
        st.session_state.agent_prompts = []
    
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""
    
    if 'website' not in st.session_state:
        st.session_state.website = ""
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    if 'final_report' not in st.session_state:
        st.session_state.final_report = ""
    
    # API Key input in sidebar
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            st.session_state.api_key = api_key
        
        # Company information inputs
        st.header("Company Information")
        company_name = st.text_input(
            "Company Name", 
            value=st.session_state.company_name,
            help="Enter the name of the company to analyze"
        )
        
        website = st.text_input(
            "Company Website", 
            value=st.session_state.website,
            help="Enter the URL of the company website"
        )
        
        # Apply button for company information
        if st.button("Apply Company Info"):
            st.session_state.company_name = company_name
            st.session_state.website = website
            # Generate prompts based on new company info
            st.session_state.agent_prompts = generate_agent_prompts(company_name, website)
            st.session_state.analysis_complete = False
            st.success(f"Company information updated: {company_name}")
        
        # Save/Load Configuration
        st.markdown("---")
        st.header("Save/Load Configuration")
        
        # Save current configuration
        save_col1, save_col2 = st.columns([3, 1])
        with save_col1:
            save_name = st.text_input("Configuration Name", 
                value=company_name.lower().replace(" ", "_") if company_name else "my_config",
                help="Enter a name for your configuration")
        
        with save_col2:
            if st.button("💾 Save"):
                if 'agent_prompts' in st.session_state and company_name and website:
                    success, content, filename = save_configuration(
                        st.session_state.agent_prompts,
                        company_name,
                        website,
                        save_name
                    )
                    if success:
                        st.download_button(
                            label="📥 Download",
                            data=content,
                            file_name=filename,
                            mime="application/json",
                            help="Click to download your configuration file"
                        )
                    else:
                        st.error(f"Error saving configuration: {content}")
                else:
                    st.error("Please enter company information first")
        
        # Load configuration
        st.markdown("---")
        uploaded_file = st.file_uploader("Load Configuration", type=['json'],
            help="Upload a previously saved configuration file")
        
        if uploaded_file is not None:
            try:
                config = json.load(uploaded_file)
                if config:
                    st.session_state.company_name = config.get('company_name', "")
                    st.session_state.website = config.get('website', "")
                    st.session_state.agent_prompts = config.get('agent_prompts', [])
                    st.success(f"Configuration loaded! (Company: {st.session_state.company_name})")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error loading configuration: {str(e)}")
    
    # Main content
    if 'api_key' not in st.session_state:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    if not st.session_state.company_name or not st.session_state.website:
        st.info("Please enter company name and website in the sidebar to begin analysis.")
        return
    
    # Display company information
    st.header(f"Analysis for: {st.session_state.company_name}")
    st.subheader(f"Website: {st.session_state.website}")
    
    # Check if prompts are generated
    if not st.session_state.agent_prompts or len(st.session_state.agent_prompts) != len(CATEGORIES):
        st.session_state.agent_prompts = generate_agent_prompts(st.session_state.company_name, st.session_state.website)
    
    # Create tabs for each category
    tabs = st.tabs(CATEGORIES + ["Final Report"])
    
    # Show prompts in each tab with ability to edit
    for i, tab in enumerate(tabs[:-1]):  # All except final report tab
        with tab:
            st.subheader(f"Analysis Prompt for {CATEGORIES[i]}")
            if i < len(st.session_state.agent_prompts):
                prompt = st.text_area(
                    "Prompt (can be edited)",
                    value=st.session_state.agent_prompts[i],
                    height=200,
                    key=f"prompt_{i}"
                )
                st.session_state.agent_prompts[i] = prompt
                
                # Show results if analysis is complete
                if st.session_state.analysis_complete and f"agent{i+1}_output" in st.session_state.results:
                    st.subheader("Analysis Results")
                    st.markdown(st.session_state.results[f"agent{i+1}_output"])
    
    # Final report tab
    with tabs[-1]:
        if st.session_state.analysis_complete and st.session_state.final_report:
            st.markdown(st.session_state.final_report)
        else:
            st.info("The final report will be generated after all analyses are complete.")
    
    # Process button
    if not st.session_state.analysis_complete:
        if st.button("Run Complete Analysis", type="primary"):
            if not all(st.session_state.agent_prompts):
                st.error("Please ensure all prompts are filled.")
                return
            
            try:
                # Create progress container
                progress_container = st.empty()
                with progress_container.container():
                    st.write("🚀 Starting comprehensive analysis process...")
                    
                    # Initialize and run agents
                    chain = AgentChain(st.session_state.agent_prompts)
                    results = chain.process_input()
                    
                    # Store results
                    st.session_state.results = results
                    
                    # Generate final report
                    st.write("🔄 Generating final comprehensive report...")
                    final_report = chain.generate_final_report(
                        st.session_state.company_name,
                        st.session_state.website,
                        results
                    )
                    st.session_state.final_report = final_report
                    
                    # Create markdown output
                    markdown_output = create_markdown(
                        results, 
                        st.session_state.company_name,
                        st.session_state.website,
                        final_report
                    )
                    
                    st.write("✨ Analysis complete!")
                    st.session_state.analysis_complete = True
                    
                    # Download button
                    st.download_button(
                        label="Download Complete Report as Markdown",
                        data=markdown_output,
                        file_name=f"{st.session_state.company_name.lower().replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                    
                # Refresh the page to show results
                st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        # Show download button for completed analysis
        markdown_output = create_markdown(
            st.session_state.results, 
            st.session_state.company_name,
            st.session_state.website,
            st.session_state.final_report
        )
        
        st.download_button(
            label="Download Complete Report as Markdown",
            data=markdown_output,
            file_name=f"{st.session_state.company_name.lower().replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        
        # Reset button
        if st.button("Start New Analysis"):
            st.session_state.analysis_complete = False
            st.session_state.results = {}
            st.session_state.final_report = ""
            st.experimental_rerun()

if __name__ == "__main__":
    main() 