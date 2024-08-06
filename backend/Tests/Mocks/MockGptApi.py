from typing import List

# Mocks for returned completion object
class MockGptMessage:
    def __init__(self, content: str, role: str = "assistant", function_call = None, tool_calls = None):
        self.content = content
        self.role = role
        self.function_call = function_call
        self.tool_calls = tool_calls

class MockGptCompletionUsage:
    def __init__(self, completion_tokens: int, prompt_tokens: int, total_tokens: int):
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens

class MockGptChoice:
    def __init__(self, finish_reason: str, index: int, message: MockGptMessage, logprobs):
        self.finish_reason = finish_reason
        self.index = index
        self.message = message
        self.logprobs = logprobs

class MockGptChatCompletion:
    def __init__(self, choices: List[MockGptChoice], created: int, id: str, model: str, object: str, system_fingerprint: str, usage: MockGptCompletionUsage):
        self.choices = choices
        self.created = created
        self.id = id
        self.model = model
        self.object = object
        self.system_fingerprint = system_fingerprint
        self.usage = usage

def completion_response_builder(choices: List[MockGptChoice], created: int, id: str, model: str, object: str, system_fingerprint: str, completion_tokens: int, prompt_tokens: int, total_tokens: int) -> MockGptChatCompletion:
    usage = MockGptCompletionUsage(completion_tokens, prompt_tokens, total_tokens)
    return MockGptChatCompletion(choices, created, id, model, object, system_fingerprint, usage)

def completion_choice_builder(finish_reason: str, index: int, content: str, role: str = "assistant", function_call = None, tool_calls = None, logprobs = None) -> MockGptChoice:
    message = MockGptMessage(content, role, function_call, tool_calls)
    return MockGptChoice(finish_reason, index, message, logprobs)