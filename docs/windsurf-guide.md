# Using Archway with Windsurf

Archway is designed to work seamlessly with Windsurf, providing an AI-enhanced development experience. This guide explains how to leverage Windsurf's AI capabilities with Archway's features.

## Getting Started

1. **Open Your Project in Windsurf**
   - Launch Windsurf
   - Open your project directory
   - Ensure Archway is properly installed and configured

2. **Environment Setup**
   ```bash
   # Create a .env file if you haven't already
   OPENAI_API_KEY=your_key_here
   SOURCEGRAPH_ENDPOINT=your_endpoint_here
   SOURCEGRAPH_TOKEN=your_token_here
   ```

## AI-Assisted Code Analysis

### Analyzing Code
When you want to analyze code, you can:
1. Open the file you want to analyze in Windsurf
2. Ask the AI to "analyze this code" or "explain what this code does"
3. The AI will automatically use Archway's `analyze code` command to provide insights
4. Analysis results are automatically saved for future reference

Example conversation:
```
You: Can you analyze this code for potential improvements?
AI: I'll analyze the code using Archway's analysis features...
    [AI provides detailed analysis and saves it for future reference]
    Analysis saved with ID: abc123
```

### Managing Analysis History
To review past analyses:
1. Ask about previous analyses of a file
2. Request specific analysis details by ID
3. Filter analyses by date or file
4. Remove outdated analyses

Example conversation:
```
You: Show me previous analyses of this file
AI: I'll list the analyses...
    [AI shows list of analyses with their IDs and dates]

You: Can you show me the details of analysis abc123?
AI: Here's the detailed analysis from that session...
    [AI shows the full analysis results]

You: Show me all analyses from last week
AI: I'll filter the analyses by date...
    [AI shows filtered list of analyses]
```

### Getting Refactoring Suggestions
To get AI-powered refactoring suggestions:
1. Open the file you want to refactor
2. Describe your refactoring goal to the AI
3. The AI will use Archway's `analyze refactor` command

Example conversation:
```
You: How can I make this code more maintainable?
AI: I'll analyze potential refactoring options...
    [AI provides refactoring suggestions using the refactor command]
```

### Architecture Analysis
For multi-file architecture analysis:
1. Have the relevant files open in Windsurf
2. Ask the AI about architectural patterns or improvements
3. The AI will use Archway's `analyze architecture` command

Example conversation:
```
You: How can we improve the architecture of these components?
AI: I'll analyze the architecture of the related files...
    [AI provides architectural insights]
```

## AI-Assisted Code Search

### Semantic Code Search
To search code semantically:
1. Describe what you're looking for to the AI
2. The AI will use Archway's `search search-code` command
3. Results will be displayed with relevant context

Example conversation:
```
You: Find all implementations of user authentication
AI: I'll search for authentication-related code...
    [AI provides search results with context]
```

### Symbol Navigation
For finding definitions and references:
1. Place your cursor on a symbol
2. Ask the AI about the symbol's definition or usage
3. The AI will use Archway's definition/references commands

Example conversation:
```
You: Where is this function defined?
AI: I'll find the definition...
    [AI shows the symbol's definition location]
```

## Best Practices

1. **Be Specific**
   - When asking for analysis, be clear about what aspects you want to focus on
   - Provide context when requesting refactoring suggestions

2. **Use Natural Language**
   - You don't need to know the exact commands
   - The AI will translate your natural language requests into appropriate Archway commands

3. **Leverage Context**
   - The AI is aware of your currently open files
   - Reference specific lines or functions for more targeted analysis

4. **Iterative Refinement**
   - Start with broad analysis
   - Ask follow-up questions for deeper insights
   - Request specific examples or clarifications

## Common Workflows

### Code Review Workflow
1. Open the files to review
2. Ask the AI to analyze the code
3. Request specific improvements or clarifications
4. Get refactoring suggestions
5. Implement changes with AI assistance
6. Review past analyses for context

### Architecture Evolution Workflow
1. Open related components
2. Request architecture analysis
3. Discuss potential improvements
4. Get specific refactoring suggestions
5. Implement changes incrementally
6. Track architectural decisions in history

### Bug Investigation Workflow
1. Describe the issue
2. Ask AI to search for related code
3. Request analysis of suspicious areas
4. Review past analyses for context
5. Get suggestions for fixes
6. Verify solutions with AI

## Troubleshooting

If you encounter issues:
1. Verify your environment variables are set correctly
2. Ensure you're in the correct directory
3. Check that Archway is properly installed
4. Ask the AI for help with specific error messages

## Tips for Effective Communication

1. **Provide Context**
   - Mention specific files or functions you're interested in
   - Reference past analyses when relevant
   - Explain your goals clearly

2. **Ask Follow-up Questions**
   - Request details from previous analyses
   - Ask for comparisons with past versions
   - Seek clarification on historical decisions

3. **Use Incremental Steps**
   - Break down complex tasks
   - Track progress through saved analyses
   - Build on previous insights

4. **Leverage History**
   - Reference previous analyses for context
   - Track changes over time
   - Use historical insights for decision-making

Remember, the AI can help you:
- Run analyses and save results automatically
- Find and show relevant past analyses
- Compare current code with previous analyses
- Track the evolution of your codebase

Remember, the AI is here to help you leverage Archway's capabilities effectively. Don't hesitate to ask for clarification or more detailed explanations of any aspect of the system.
