"""AI Assistant Context Manager for GitHub Interactions."""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class AIContextManager:
    def __init__(self):
        self.context_file = '.ai_context.json'
        self.context = self.load_context()

    def load_context(self) -> Dict:
        """Load existing context or create new."""
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r') as f:
                return json.load(f)
        return {
            'conversations': {},
            'code_changes': {},
            'decisions': [],
            'learning_points': []
        }

    def store_conversation(self, issue_number: int, content: str):
        """Store conversation context."""
        if str(issue_number) not in self.context['conversations']:
            self.context['conversations'][str(issue_number)] = []
        
        self.context['conversations'][str(issue_number)].append({
            'timestamp': datetime.now().isoformat(),
            'content': content
        })
        self.save_context()

    def store_code_change(self, pr_number: int, files: List[str], description: str):
        """Store code change context."""
        if str(pr_number) not in self.context['code_changes']:
            self.context['code_changes'][str(pr_number)] = []
        
        self.context['code_changes'][str(pr_number)].append({
            'timestamp': datetime.now().isoformat(),
            'files': files,
            'description': description
        })
        self.save_context()

    def store_decision(self, description: str, reasoning: str):
        """Store AI decision and reasoning."""
        self.context['decisions'].append({
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'reasoning': reasoning
        })
        self.save_context()

    def store_learning(self, topic: str, insight: str):
        """Store learning points from interactions."""
        self.context['learning_points'].append({
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'insight': insight
        })
        self.save_context()

    def get_relevant_context(self, issue_number: Optional[int] = None, 
                           pr_number: Optional[int] = None) -> Dict:
        """Get relevant context for current interaction."""
        context = {
            'conversations': [],
            'code_changes': [],
            'related_decisions': [],
            'relevant_learnings': []
        }

        if issue_number:
            context['conversations'] = self.context['conversations'].get(str(issue_number), [])
        
        if pr_number:
            context['code_changes'] = self.context['code_changes'].get(str(pr_number), [])

        # Include recent decisions and learnings
        context['related_decisions'] = self.context['decisions'][-5:]
        context['relevant_learnings'] = self.context['learning_points'][-5:]

        return context

    def save_context(self):
        """Save context to file."""
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)

    def summarize_interaction(self, number: int, type_: str = 'issue') -> str:
        """Generate summary of an interaction."""
        context = self.get_relevant_context(
            issue_number=number if type_ == 'issue' else None,
            pr_number=number if type_ == 'pr' else None
        )
        
        summary = []
        if context['conversations']:
            summary.append("## Conversation Summary")
            summary.append("Key points discussed:")
            for conv in context['conversations'][-3:]:  # Last 3 conversations
                summary.append(f"- {conv['content'][:100]}...")

        if context['code_changes']:
            summary.append("\n## Code Changes")
            for change in context['code_changes']:
                summary.append(f"- Modified: {', '.join(change['files'])}")
                summary.append(f"  {change['description']}")

        return '\n'.join(summary)

def main():
    # Example usage
    manager = AIContextManager()
    
    # Store some context
    manager.store_conversation(1, "Discussing implementation of feature X")
    manager.store_code_change(1, ["file1.py", "file2.py"], "Implemented feature X")
    manager.store_decision("Used approach A over B", "Better performance characteristics")
    
    # Get context for current interaction
    context = manager.get_relevant_context(issue_number=1)
    print(json.dumps(context, indent=2))

if __name__ == '__main__':
    main()
