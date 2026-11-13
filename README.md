# DBA-AI-Agent
Capstone Project for Generative and Agentic AI Traning
# Agentic AI DBA Troubleshooting Assistant

## 1. Project Title & Description

**Agentic AI DBA Troubleshooting Assistant**

This project aims to build an AI-powered assistant that helps Database Administrators (DBAs) investigate and troubleshoot common PostgreSQL database incidents.

When a user reports an issue, such as slow database performance or connection timeouts, the agent investigates the problem by selecting and executing appropriate diagnostic tools. It analyses the results, checks the relevant Standard Operating Procedures (SOPs) and provides a possible diagnosis along with recommended actions.

The system uses **LangChain and LangGraph** to demonstrate agentic AI concepts such as tool calling, decision-making, workflow orchestration, memory management and human-in-the-loop approval.

The project uses simulated PostgreSQL data, so no actual database connection is required. Any potentially disruptive action is paused for human approval before execution.

## 2. Scope

### Within Scope
- Accept database incidents through an interactive command-line interface.
- Analyse user-reported issues using an LLM.
- Select and execute relevant diagnostic tools.
- Check database health, active connections and blocking locks.
- Retrieve troubleshooting procedures from predefined SOP files.
- Maintain investigation history and conversation context.
- Generate a diagnosis and recommend corrective actions.
- Include human approval before executing high-impact actions.
- Maintain logs of tool calls, decisions and results.
- Evaluate the agent using predefined test scenarios.

### Out of Scope
- Connecting to or modifying an actual PostgreSQL database.
- Executing real SQL queries or database administration commands.
- Automatic execution of destructive or high-impact operations.
- Building a web-based frontend or dashboard.
- Implementing a vector database or RAG pipeline.
- Managing multiple production databases.

## 3. Dataset

The project uses simulated PostgreSQL diagnostic data and predefined troubleshooting procedures stored in JSON files.

The sample data includes database health metrics, connection information, blocking lock details and corresponding SOPs. These inputs allow the agent to investigate different database incidents and recommend appropriate actions.

**Dataset / Reference URL:**

[Insert Dataset URL Here]

### Sample Input

**Incident reported by the user:**

"Database is running slowly and application users are experiencing connection timeouts."

### Expected Agent Output

The agent should:
1. Check the database health status.
2. Inspect the active and available connections.
3. Identify any blocking locks or long-running transactions.
4. Retrieve the relevant troubleshooting SOP.
5. Analyse the findings and identify the likely cause.

**Expected Diagnosis:**

A long-running transaction is blocking multiple sessions, contributing to high connection usage and application timeouts.

**Recommended Action:**

Review the blocking session and follow the approved troubleshooting procedure. Any simulated termination of the blocking session requires human approval.

## 4. Dependencies & Implementation

### Technology Stack
- **Python** – Core programming language.
- **LangChain** – LLM integration and tool definition.
- **LangGraph** – Agent workflow, state management and conditional execution.
- **OpenAI API / Approved LLM** – Reasoning and decision-making.
- **JSON** – Storage of simulated database metrics and SOPs.
- **Python CLI** – User interaction.

### Dependencies
[Add the final dependencies and package versions from requirements.txt here.]

### Code Implementation & Best Practices

The project will focus on the following implementation aspects:

- **Functional Correctness:** Ensure diagnostic tools, agent workflows and outputs work as expected.
- **System Prompt:** Define clear instructions, responsibilities, decision-making rules and limitations for the agent.
- **Guardrails:** Restrict tool access, validate inputs and prevent unauthorised or unsafe actions.
- **Human-in-the-Loop:** Require explicit approval before executing high-impact actions.
- **State Management & Memory:** Maintain incident details, tool results and previous conversation messages.
- **Middleware & Error Handling:** Implement suitable validation, error handling and execution controls.
- **Observability:** Record tool executions, agent decisions and investigation results.
- **Evaluation:** Test the agent against different incident scenarios and verify its diagnostic decisions.

**Additional implementation details:**

[Add details about system prompts, guardrails, middleware and other best practices implemented in the project.]

## 5. Steps to Run

[Add the installation, environment setup, API key configuration and execution instructions after completing the project.]
