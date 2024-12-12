# Archway Foundational Instructions
## System Overview

**Purpose:** Give Windsurf a high-level understanding of the entire system it should build and maintain.

### Goal

Windsurf, your objective is to establish and maintain a fully integrated, AI-driven development environment—referred to as **Archway**—that:

- Incorporates **Sourcegraph** for code indexing and semantic navigation.
- Utilizes a **Local LLM Layer** for rapid code queries and context retrieval.
- Employs a **Cloud LLM Layer** (the isolated OpenAI “o1” model) for deep architectural reasoning, complex refactoring, and advanced code generation.
- Operates entirely within **Dockerized environments** for consistent and reproducible builds.
- Adheres to a **Hexagonal Architecture (Ports & Adapters)** pattern to enforce clean, maintainable code boundaries.
- Integrates a **CI/CD pipeline** that automates testing, validation, and, in time, autonomous deployment.
- Supports **interactive development sessions** (e.g., via IPython) to iteratively test and refine code at runtime.

Your long-term aim is to enable Archway to function with minimal or no human intervention. Initially, human approval will be required for changes, but as confidence grows in your adherence to these guidelines and passing test suites, you will gradually gain autonomy.

### Layers of the System

1. **Sourcegraph Integration:**  
   A fully indexed codebase enabling semantic code search, making it easier to find references, navigate the architecture, and support informed refactoring.

2. **Local LLM Layer:**  
   A code-focused, locally hosted LLM (e.g., Code Llama) for quick insights, inline suggestions, and low-latency code comprehension.

3. **OpenAI “o1” Model (Cloud LLM):**  
   For strategic reasoning, large-scale architectural decisions, and complex problem-solving. Summarize code and context, send it to the o1 model, and apply its suggestions.

4. **Dockerized Environment:**  
   Everything runs in containers, ensuring that all environments—local dev, CI/CD, test—are consistent and reproducible.

5. **Hexagonal Architecture:**  
   Enforce a clean separation of concerns. Domain logic remains pure and isolated, while external integrations are handled by adapters that implement defined ports.

6. **CI/CD Pipeline:**  
   Automate testing, quality checks, and eventually deployments. Initially requires human approval, but as confidence builds, enable autonomous merges and deploys for routine tasks.

7. **Interactive Sessions:**  
   Use IPython (or similar) within Docker to test snippets and logic immediately, refining code before finalizing changes.




