from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from graph import SecurityAgent

llm = SecurityAgent()

class ChatBot:
		def process(self, user_input: str) -> str:
			return llm.ask(user_input)

def main():
	bot = ChatBot()
	console = Console()
	console.print(Panel("Bem-vindo ao [bold cyan]Chat CLI[/bold cyan]! ([green]digite 'sair' para encerrar[/green])", style="bold magenta"))
	while True:
		user_input = Prompt.ask("[bold blue]Você[/bold blue]", console=console)
		if user_input.strip().lower() == 'sair':
			console.print("[yellow]Encerrando o chat. Até logo![/yellow]")
			break
		resposta = bot.process(user_input)
		console.print(Panel(f"[bold white]{resposta}[/bold white]", title="[bold green]Bot[/bold green]", style="green"))

if __name__ == "__main__":
	main()