from typing import Type, Dict, Protocol
from llama_index.core import Document
from llama_index.readers.google import GoogleDriveReader
from llama_index.core import SimpleDirectoryReader

GOOGLE_AUTH_JSON = "service_account.json"

class LoaderStrategy(Protocol):
    def load(self, source: str) -> list[Document]:
        ...


class LoaderRegistry:
    _registry: Dict[str, Type[LoaderStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(loader_cls: Type[LoaderStrategy]):
            cls._registry[name] = loader_cls
            return loader_cls
        return decorator

    @classmethod
    def create(cls, name: str) -> LoaderStrategy:
        if name not in cls._registry:
            raise ValueError(f"Loader '{name}' not registered")
        return cls._registry[name]()

@LoaderRegistry.register("google-drive")
class GoogleDriveLoader:
    def load(self, source: str):
        loader = GoogleDriveReader(
            credentials_path=GOOGLE_AUTH_JSON
        )
        return loader.load_data(
            folder_id=source,
            recursive=True
        )

@LoaderRegistry.register("dir")
class DirectoryLoader:
    def load(self, source: str):
        loader = SimpleDirectoryReader(
            input_dir=source,
            encoding="iso-8859-1",
            recursive=True
        )
        return loader.load_data()

@LoaderRegistry.register("md")
class MarkdownLoader:
    def load(self, source: str):
        loader = SimpleDirectoryReader(
            input_dir=source,
            encoding="UTF-8",
            required_exts=[".md"],
            recursive=True
        )

        return loader.load_data()
