from .allocation import Allocation
from .constants import MINUTES_PER_SKS


class CourseClass:
    """Mata kuliah yang memiliki kode, jumlah SKS, dan jadwal awal."""

    def __init__(self, id: str, sks: int, initial: Allocation):
        """
        Args:
            id: Kode unik kelas, misalnya "IF101_A".
            sks: Jumlah SKS kelas.
            initial: Hari, jam mulai, dan ruangan pada jadwal awal.
        """
        self.id = id  # kode unik, dipakai sebagai key jadwal
        self.sks = sks  # menentukan lama kelas
        self.initial = initial  # posisi sebelum diubah algoritma

    @property
    def duration(self) -> int:
        """
        Hitung lama kelas dalam menit.

        Returns:
            Durasi kelas, yaitu 50 menit dikali jumlah SKS.
        """
        return MINUTES_PER_SKS * self.sks
