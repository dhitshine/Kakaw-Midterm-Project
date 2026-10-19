from .course_class import CourseClass
from .room import Room
from .student import Student


class Instance:
    """Seluruh data tetap untuk satu kasus: ruangan, kelas, dan mahasiswa."""

    def __init__(
        self,
        rooms: list[Room],
        classes: list[CourseClass],
        students: list[Student],
    ):
        """
        Args:
            rooms: Daftar ruangan yang tersedia.
            classes: Daftar kelas yang harus dijadwalkan.
            students: Daftar mahasiswa beserta kelas yang mereka ambil.
        """
        self.rooms = rooms
        self.classes = classes
        self.students = students
