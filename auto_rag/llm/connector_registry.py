from auto_rag.llm.llama_connector import Llama3Connector

LLM_CONNECTORS = {
    "llama3": Llama3Connector,
}
"""A registry mapping language model names to their concrete connector classes.

This dictionary enables dynamic selection and instantiation of LLM connectors
based on user input or configuration. Add new models and their connector classes
here to extend support for additional LLMs.
"""