class Room:
    """Ruangan yang dapat dipakai untuk kelas."""

    def __init__(self, id: str, capacity: int):
        """
        Args:
            id: Kode unik ruangan.
            capacity: Jumlah maksimal mahasiswa yang muat di ruangan.
        """
        self.id = id  # kode ruangan, dipakai di Allocation
        self.capacity = capacity  # dipakai untuk menghitung penalti kapasitas
