# import openai
import markdown2
from docx import Document
import google.generativeai as genai
import gradio as gr
from bs4 import BeautifulSoup
import os

# Set base directory for files
BASE_DIR = os.path.expanduser("~/Desktop")

# Set your OpenAI API key
# openai.api_key = ""

# SRS prompt template


input_sources = ""

def generate_proposal(prompt):
    # Call OpenAI API to generate markdown content
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes software proposal documents in markdown."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']


def generate_proposal_gemini(prompt):
    # Configure the API
    genai.configure(api_key="AIzaSyC1_RojylkSebymOyIdWYtivVjgKZ3d9MQ")
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    
    # Generate content
    print(f"\nInput tokens: {model.count_tokens(prompt)}")
    response = model.generate_content(prompt)
    print(f"Output tokens: {model.count_tokens(response.text)}")
    
    return response.text

def markdown_to_docx(markdown_text, output_path):
    # Convert markdown to HTML
    html = markdown2.markdown(markdown_text)
    # Create a new Word document
    template_path = os.path.join(BASE_DIR, "SRSTemplate.docx")
    doc = Document(template_path)
    # Add content (simple approach: strip HTML tags, or use a library for better conversion)
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.descendants:
        if element.name == 'h1':
            doc.add_heading(element.get_text(), level=1)
        elif element.name == 'h2':
            doc.add_heading(element.get_text(), level=2)
        elif element.name == 'h3':
            doc.add_heading(element.get_text(), level=3)
        elif element.name == 'ul':
            for li in element.find_all('li'):
                doc.add_paragraph(li.get_text(), style='List Bullet')
        elif element.name == 'ol':
            for li in element.find_all('li'):
                doc.add_paragraph(li.get_text(), style='List Number')
        elif element.name == 'p':
            doc.add_paragraph(element.get_text())
    # Save the document
    doc.save(output_path)

def generate_srs_via_gradio(project_name, client_name, high_level_scope):
    """
    Handles SRS generation based on inputs from the Gradio UI.
    """

    try:
        # Construct the user prompt using the global template

        user_prompt = """
        You are a professional AI assistant tasked with generating a System Requirements Specification (SRS) document in markdown format. The document should accurately capture the requirements for the system based on provided inputs. Maintain a professional, clear, precise, and unambiguous tone suitable for technical documentation.

        Use the following parameters to customize the SRS:

        Client Name: {client_name}

        Project/System Name: {project_name}

        High-Level System Scope: {high_level_scope}

        Input Sources (e.g., Transcripts, Artifacts): {input_sources}


        Your task is to analyze the information contained within the Input sources to extract, synthesize, and document the system requirements for the {project_name} being developed for {client_name}. Structure the document based on the sections and subsections outlined below, drawing inspiration from the provided example SRS document structure. You are also authorized to create new sections or subsections if the analyzed input sources reveal requirements or context that do not fit neatly into the predefined structure but are essential for a complete SRS, guided by the overall project scope and goals.

        Here is the recommended structure and guidance for each section of the SRS, inspired by the example document:

        Document Title:

        Guidance: Create a clear title for the document, incorporating the Project/System Name and indicating it is a Software Requirements Specification.

        1. Introduction:

        Guidance: Provide a foundational overview of the document and the project.

        Content to include:

        1.1 Purpose: Explain the purpose of this SRS document.

        1.2 Project Scope: Detail the boundaries and key features included in the {project_name} based on the High-Level System Scope and input sources.

        1.3 Intended Audience: Specify who this document is for (e.g., developers, testers, stakeholders).

        2. Overall Description:

        Guidance: Describe the general context and factors influencing the system.

        Content to include:

        2.1 Product Perspective: Explain how the {project_name} fits into the larger picture or interacts with other systems.

        2.2 Operating Environment: Describe the environments where the system will operate (e.g., mobile platforms, web browsers, servers).

        2.3 Assumption & Dependency: List factors assumed to be true and external dependencies the project relies on (e.g., third-party services, data availability).

        3. [Main System Component/Interface Name, e.g., App Interface]:

        Guidance: Detail the requirements related to a major component or interface of the system. Use the example's structure as inspiration for breaking down complex interfaces into logical subsections.

        Content to include: Describe the overall interface/component and then break down specific flows, screens, or features as subsections (e.g., Onboarding, Profile Setting, specific feature flows). Extract these details from input_sources.

        4. [Another Main System Component/Feature Area, e.g., Login Account Setup]:

        Guidance: Detail requirements for another significant part of the system. Continue breaking down into subsections as needed.

        Content to include: Specific features or processes within this area (e.g., Sign-Up, Sign-In, Password Recovery).

        (Continue adding sections for other major components/feature areas as identified from the example document structure and the input sources, e.g., Plan Subscription, Bank Account Integration, Demo Mode, Credit Monitoring Service Integration, Home Screen, Calendar, Spending Tips & Score Impact, Profile Setting, Payment Reminder, Update Goals, Rewards, Inquiry Removal & Credit Repair, etc.)

        [Section for Functional Requirements - Can be integrated within component sections or as a dedicated section]:

        Guidance: Clearly state what the system must do. Organize these logically. Each should be a testable requirement. Extract from {input_sources}.

        [Section for Non-Functional Requirements - Can be integrated within component sections or as a dedicated section]:

        Guidance: Describe the quality attributes of the system (e.g., performance, security, usability, reliability, scalability, environmental constraints). Extract from {input_sources}.

        [Other Relevant Sections from Example, e.g., Terms & Conditions, Privacy Policy, System Architecture, References, Out of Scope for MVP]:

        Guidance: Include sections for important related information as seen in the example SRS. For sections marked "Pending" in the example, note that the details are TBD based on input sources. For "Out of Scope," clearly list items explicitly excluded from the current phase.

        [New Sections (if needed)]:

        Guidance: If the Input sources contain significant requirements, constraints, or context that do not fit into the above structure, create new, appropriately titled sections or subsections to capture them. Ensure these new sections are relevant to the {project_name} and its scope.

        Conclusion:

        Guidance: Provide a brief concluding statement summarizing the SRS and its role in the project.

        General Instructions for AI:

        Generate the entire response in markdown format.

        Use clear headings and subheadings corresponding to the SRS structure outlined above. Use appropriate markdown heading levels (#, ##, ###, etc.).

        Use bullet points or numbered lists for requirements within sections, particularly in Functional and Non-Functional Requirements, to ensure clarity and organization.

        Maintain a formal, technical, and objective tone throughout the document.

        Carefully analyze the Input sources to extract accurate, complete, and unambiguous requirements. Synthesize information from multiple sources if necessary.

        Incorporate the values provided for each parameter throughout the relevant sections of the document.

        Creatively include new sections or subsections if the input data necessitates them for a comprehensive SRS, ensuring they align with the project scope and goals.
        """

        #Read artifacts from a hardcoded file
        artifacts_file = os.path.join(BASE_DIR, "artifacts.txt")
        try:
            with open(artifacts_file, "r", encoding="utf-8") as f:
                artifacts = f.read()
        except FileNotFoundError:
            print(f"Artifacts file not found at {artifacts_file}.")
            artifacts = ""

        # Read transcripts from a hardcoded file with encoding fallback
        transcripts_file = os.path.join(BASE_DIR, "transcript.txt")
        try:
            with open(transcripts_file, "r", encoding="utf-8") as f:
                transcripts = f.read()
        except UnicodeDecodeError:
            with open(transcripts_file, "r", encoding="latin-1") as f:
                transcripts = f.read()
        except FileNotFoundError:
            print(f"Transcripts file not found at {transcripts_file}.")
            transcripts = ""

        input_sources = f"Client Meeting Transcripts:\n{transcripts}\n\nAdditional Artifacts:\n{artifacts}"


        user_prompt = user_prompt.replace(
            "{project_name}", project_name
        ).replace(
            "{client_name}", client_name
        ).replace(
            "{high_level_scope}", high_level_scope
        ).replace(
            "{Input Sources}", input_sources
        )

        print(f"\n[Gradio] Generating SRS document for: {project_name}")
        print("Complete User prompt:" + user_prompt)
        markdown_content = generate_proposal_gemini(user_prompt)

        # # Read SRS template from file
        # markdown_file = os.path.join(BASE_DIR, "SRS_PrimetimePharmacy.md")
        # try:
        #     with open(markdown_file, "r", encoding="utf-8") as f:
        #         markdown_content = f.read()
        # except FileNotFoundError:
        #     print(f"Template file not found at {markdown_file}")
        
        # Save markdown content to .md file
        md_file_gradio = os.path.join(BASE_DIR, f"SRS_{project_name}.md")
        with open(md_file_gradio, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"\n[Gradio] Markdown file saved to {md_file_gradio}")

        # Convert markdown to .docx file
        output_file_gradio = os.path.join(BASE_DIR, f"SRS_{project_name}.docx")
        markdown_to_docx(markdown_content, output_file_gradio)
        print(f"\n[Gradio] Word document saved to {output_file_gradio}")

        return f"SRS document generated successfully for '{project_name}'.\nMarkdown: {md_file_gradio}\nWord: {output_file_gradio}"
    except Exception as e:
        print(f"[Gradio] Error during SRS generation: {e}")
        return f"Error generating SRS: {e}"



if __name__ == "__main__":
    print("\n=== SRS Document Generator ===\n")
    # project_name = input("Project Name: ")
    # client_name = input("Client Name: ")
    # high_level_scope = input("High-Level System Scope: ")
        

    print("\nGenerating SRS document...")
    # markdown_content = generate_proposal_gemini(user_prompt)


    #Save markdown content to .md file
    # md_file = f"Desktop/SRS_{project_name}.md"
    # with open(md_file, "w") as f:
    #     f.write(markdown_content)
    # print(f"\nMarkdown file saved to {md_file}")
    # output_file = f"Desktop/SRS_{project_name}.docx"
    # markdown_to_docx(markdown_content, output_file)
    # print(f"\nSRS document saved to {output_file}")

    # Define the Gradio interface
    # This interface will be launched if the surrounding code block is executed.
    srs_interface = gr.Interface(
        fn=generate_srs_via_gradio,
        inputs=[
            gr.Textbox(label="Project Name", placeholder="Enter the project name"),
            gr.Textbox(label="Client Name", placeholder="Enter the client name"),
            gr.Textbox(label="High-Level System Scope", placeholder="Enter the project goal)", lines=5),
            # gr.Textbox(label="Project Transcript Location", placeholder="Enter the Project transcript file location)"),
        ],
        outputs=gr.Textbox(label="Generation Status and File Paths", lines=3),
        title="Software Requirements Specification (SRS) Generator",
        description="Enter project details to generate an SRS document."
    )

    # Define the handler function for proposal generation
    def generate_proposal_via_gradio(industry_name,client_name, client_request, tech_stack, estimation_notes=None):
        try:
            print(f"\n[Gradio Proposal] Received request for: {client_name}")
            
            # BASE_DIR is used in generate_srs_via_gradio, assuming "Desktop"
            BASE_DIR = "Desktop" 
            if not os.path.exists(BASE_DIR):
                os.makedirs(BASE_DIR)
                print(f"[Gradio Proposal] Created directory: {BASE_DIR}")

            prompt = f"""
            You are a professional AI assistant tasked with generating a project proposal document in markdown format. The proposal should follow a standard structure and incorporate the specific project details provided through parameters. For sections like responsibilities, timeline, and cost, generate content creatively based on the project scope described by the other parameters. Maintain a professional, clear, and persuasive tone, allowing for creativity while ensuring accuracy and adherence to the structure.

            Use the following parameters to customize the proposal:
            - Industry Name: {{industry_name}}
            - Client Name: {{client_name}}
            - Client Request: {{client_request}}
            - Preferred Technology Stack: {{tech_stack}}
            - Additional Notes/Disclaimers for Effort Estimation: {{estimation_notes}}

            Here is the structure and guidance for each section:

            **Document Title:**
            * **Guidance:** Create a concise title for the proposal, incorporating the Industry Name and Client Name.

            **Executive Summary:**
            * **Guidance:** Provide a brief overview. Summarize the problem addressed by the Client Request, the proposed solution, the scope of work (creatively define typical responsibilities based on the project type and client/your roles), and key benefits for the Client Name in the {{industry_name}} sector. Keep the content within 100 words.

            **Project Overview:**
            * **Guidance:** Describe the project context based on the Client Request, the objectives, and the Client Name's goals. Explain the value proposition of the proposed solution for their specific needs in the {{industry_name}} sector.

            **Project Approach:**
            * **Guidance:** Outline a typical methodology and phases for a project addressing the Client Request using the Preferred Technology Stack. Describe the key activities in each phase and creatively estimate a plausible timeline based on the project scope. Emphasize collaboration and integration. Keep the content within 150 words. Structure the content using bullet points in a way that is easy to understand and follow.

            **Proposed Solution Details:**
            * **Guidance:** Provide detailed descriptions of the core components, modules, or features of the proposed solution designed to address the Client Request. Structure the solution in bullet points in a way that is easy to understand and follow.
            * **Content to include:** Describe the main modules and features of the solution and keep it concise.

            **Proposed Technology Stack & Tools:**
            * **Guidance:** Think about the {{client_request}} core modules and features and briefly describe the technologies, frameworks, and tools you propose to use, incorporating the Preferred Technology Stack. Mention the rationale for selection based on the Client Request and {{industry_name}} needs. Keep the content within 150 words. Structure the content in bullet points in a way that is easy to understand and follow.

            **Assumptions & Dependencies:**
            * **Guidance:** List any assumptions made about the Client Name's environment, data, or resources related to the Client Request. List any dependencies typically required for project success, including dependencies related to client responsibilities (creatively defined).

            **Effort Estimation:**
            * **Guidance:** Creatively estimate a plausible Timeline and Cost range for a project of this scope, considering the Client Request and Preferred Technology Stack. Keep the content within 100 words. Structure the content in bullet points in a way that is easy to understand and follow.

            **Conclusion:**
            * **Guidance:** Write a concluding statement reinforcing commitment to the Client Name and expressing enthusiasm for collaboration on the project addressing the Client Request.

            **General Instructions for AI:**
            * Generate the entire response in markdown format.
            * Use clear headings and subheadings, bullet points and formatted text to make the content more readable.
            * Use bullet points instead of numbers where appropriate (e.g., for solution details, technology stack, approach assumptions, dependencies).
            * Maintain a professional tone.
            * Incorporate the values provided for each parameter throughout the relevant sections of the proposal.
            * Creatively generate content for team responsibilities, client responsibilities, estimated time range based on the context provided by the other parameters and the general nature of the project described in the Client Request and Solution Details
            * The estimated cost for a week is $1000 so accordingly give a estimated range of costing based on the estimated time range
            * Ensure to keep the proposal concise and to the point and avoid any duplication or fluff.
            * Don't mention the word count in the proposal.
            """

            # Assuming generate_proposal_gemini is available in the scope (e.g., imported)
            markdown_content = generate_proposal_gemini(prompt)
            print(f"[Gradio Proposal] Markdown content generated for proposal.")

            # Sanitize project_name for filename to avoid issues with special characters
            safe_project_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in client_name).replace(' ', '_')
            
            md_file_proposal = os.path.join(BASE_DIR, f"Proposal_{safe_project_name}.md")
            with open(md_file_proposal, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"\n[Gradio Proposal] Markdown file saved to {md_file_proposal}")

            output_file_proposal = os.path.join(BASE_DIR, f"Proposal_{safe_project_name}.docx")
            # Assuming markdown_to_docx is available in the scope (e.g., imported)
            # and uses a template.docx from "Desktop/template.docx" as per genai.py context
            markdown_to_docx(markdown_content, output_file_proposal)
            print(f"\n[Gradio Proposal] Word document saved to {output_file_proposal}")

            return f"Proposal document generated successfully for '{client_name}'.\nMarkdown: {md_file_proposal}\nWord: {output_file_proposal}"
        except Exception as e:
            print(f"[Gradio Proposal] Error during proposal generation: {e}")
            # For more detailed debugging, one might add:
            # import traceback
            # traceback.print_exc()
            return f"Error generating proposal: {e}"

    # Define the Gradio interface for proposal generation
    proposal_interface = gr.Interface(
        fn=generate_proposal_via_gradio,
        inputs=[
            gr.Textbox(label="Industry Name"),
            gr.Textbox(label="Client Name"),
            gr.Textbox(label="Client Request"),
            gr.Textbox(label="Tech Stack"),
            gr.Textbox(label="Project Goal", placeholder="Describe the project goal and key objectives", lines=5),
        ],
        outputs=gr.Textbox(label="Generation Status and File Paths", lines=3),
        title="Software Proposal Generator",
        description="Enter project details to generate a proposal document (Markdown and DOCX)."
    )

    # Combine the existing SRS interface and the new Proposal interface into a TabbedInterface
    # The colleague will need to change the .launch() call from srs_interface.launch() to 
    tabbed_interface = gr.TabbedInterface(
        [srs_interface, proposal_interface], 
        tab_names=["SRS Generator", "Proposal Generator"]
    )


    print("\nGradio interface launching...")
    tabbed_interface.launch(share=True)



