from abc import ABC, abstractmethod
from kakaw.models import Jadwal

class LocalSearch(ABC):
  """
  Deskripsi: 
    Abstract class untuk algoritma local search.
  """

  def __init__(self, state) -> None:
    self.initial_state = state

  @abstractmethod
  def search(self):
    """Method wajib untuk menjalankan algoritma."""
    pass
