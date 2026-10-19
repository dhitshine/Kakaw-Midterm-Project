class Enrollment:
    """Pendaftaran satu mahasiswa pada satu kelas beserta prioritasnya."""

    def __init__(self, class_id: str, priority: int):
        """
        Args:
            class_id: Kode kelas yang diambil.
            priority: Tingkat prioritas pendaftaran, dari 1 (paling tinggi)
                sampai 4 (paling rendah).
        """
        self.class_id = class_id  # kelas yang diambil mahasiswa
        self.priority = priority  # memengaruhi bobot penalti perpindahan


class Student:
    """Mahasiswa dan kelas-kelas yang diambilnya."""

    def __init__(self, id: str, enrollments: tuple[Enrollment, ...]):
        """
        Args:
            id: Kode unik mahasiswa.
            enrollments: Semua kelas yang diambil mahasiswa ini.
        """
        self.id = id                      # kode unik mahasiswa
        self.enrollments = enrollments    # daftar kelas yang diambil

    @property
    def class_ids(self) -> tuple[str, ...]:
        """
        Ambil kode semua kelas yang diambil mahasiswa.

        Returns:
            Tuple kode kelas, sesuai urutan pendaftaran.
        """
        return tuple(enrollment.class_id for enrollment in self.enrollments)
