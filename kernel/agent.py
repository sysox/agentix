from kernel.spec import AgentSpec
from kernel.llm import LLM

class Agent:
    def __init__(self, spec: AgentSpec):
        self.spec = spec
        self.llm = LLM()

    def call_llm(self, task: str, context: dict):
        # Construct prompt from spec + task + context
        prompt = f"""
Role: {self.spec.role}
Description: {self.spec.description}

Task: {task}

Context:
{context}
"""
        # In a real implementation, we would format context better
        # and possibly use spec.prompt as a system prompt template.
        
        # For now, just pass to LLM
        text = self.llm.complete(prompt)
        
        # Mock response object to match Runner expectation
        class Response:
            def __init__(self, text):
                self.text = text
                self.input_tokens = len(prompt) // 4  # rough estimate
                self.output_tokens = len(text) // 4
                self.model_name = "stub-model"

        return Response(text)
