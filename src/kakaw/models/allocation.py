class Allocation:
    """Waktu dan ruangan tempat satu kelas dijadwalkan."""

    def __init__(self, day: str, start: int, room_id: str):
        """
        Args:
            day: Nama hari, misalnya "Senin".
            start: Menit mulai dihitung sejak pukul 00:00.
            room_id: Kode ruangan tempat kelas berlangsung.
        """
        self.day = day  # hari pelaksanaan kelas
        self.start = start  # menit mulai, bukan jam
        self.room_id = room_id  # kode ruangan, bukan objek Room

    def __eq__(self, other: object) -> bool:
        """
        Bandingkan dua penempatan berdasarkan hari, jam mulai, dan ruangan.

        Args:
            other: Objek yang akan dibandingkan.

        Returns:
            True jika ketiga nilainya sama, False jika berbeda.
        """
        if not isinstance(other, Allocation):
            return NotImplemented
        return (self.day, self.start, self.room_id) == (
            other.day,
            other.start,
            other.room_id,
        )
