from ai.graph import VendaSegurosAssistant

# DEBUG
# class AgentStub:
#     def ask(self, question: str) -> str:
#         return f"Mocked Response, question: {question}"


class QAService:
    def __init__(self):
        self.agent = VendaSegurosAssistant()

    def handle_question(self, user_input: str) -> str:
        response = self.agent.ask(user_input)
        return response