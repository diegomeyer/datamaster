from abc import ABC, abstractmethod

class DataGeneratorInterface(ABC):
    """Interface para geradores de dados fake."""
    
    @abstractmethod
    def generate_post(self):
        """Gera um post fake."""
        pass