# Generate Command Documentation

## Overview
The `generate` command is a powerful tool in TextNexus that implements Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses to your questions. It combines document retrieval with language model generation to create responses grounded in your indexed documents.

## Supported Models

TextNexus currently supports Llama models through Ollama integration. The following model is registered and available:
- `llama3` (default)

To use the generate command, ensure you have Ollama installed and configured (see [Local Setup Guide](../LOCAL_SETUP.md#2-install-and-configure-ollama) for installation instructions).

> **Note:** The `--model` parameter only accepts registered models. Using an unregistered model will result in an error message listing the available models. For example:
> ```
> Error: Unsupported model 'llama2'. Available models: ['llama3']
> ```

## Usage
```bash
python -m textnexus.cli generate "Your question here" [OPTIONS]
```

### Arguments
- `QUERY_TEXT`: The question or prompt you want to ask (required)

### Options
- `--model, -m`: The language model to use for generation [default: llama3]
- `--top-k, -k`: Number of relevant document chunks to retrieve [default: 3]

## Examples

### Basic Usage
```bash
python -m textnexus.cli generate "What is deep learning?"
```

### Specifying the Model Explicitly
```bash
python -m textnexus.cli generate "Explain neural networks" --model llama3
```

### Adjusting Context Size
```bash
python -m textnexus.cli generate "Describe transformer architecture" --top-k 5
```

## How It Works
1. **Document Retrieval**: The command first retrieves the most relevant document chunks based on your query using semantic search.
2. **Context Assembly**: Retrieved chunks are combined to form the context for the language model.
3. **Generation**: The selected language model generates a response using both your query and the retrieved context.

## Error Handling
- If no relevant documents are found, the command will warn you and generate a response without context.
- If an unsupported model is specified, the command will list available models.
- Any errors during execution are clearly displayed with helpful messages.

## Tips
- Use more context (higher `--top-k`) for complex questions that might need broader context
- Try different models if you're not satisfied with the responses
- Ensure documents are properly indexed before using the generate command

## Related Documentation
- [Query Command](QUERY_COMMAND.md) - For understanding the underlying retrieval system
- [Local Setup](LOCAL_SETUP.md) - For setting up the required environment