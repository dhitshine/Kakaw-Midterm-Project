from itertools import pairwise

from kakaw.models import Instance
from kakaw.models.constants import (
    BUFFER_MINUTES,
    DAY_END_MINUTES,
    DAY_START_MINUTES,
    GAP_DIVISOR,
    PRIORITY_WEIGHT,
)
from kakaw.problems.state import State


class ObjectiveFunction:
    """
    Menilai kualitas jadwal dengan satu angka skalar yang semakin kecil semakin baik.

    Nilai akhir terdiri dari pelanggaran keras yang diberi bobot besar
    (bentrok waktu atau ruangan) dan penalti ringan (kekurangan kapasitas,
    perpindahan dari jadwal awal, serta jeda yang terlalu panjang).
    """

    def __init__(self, instance: Instance) -> None:
        """
        Args:
            instance: Data yang berisi ruangan, kelas, dan mahasiswa.
        """
        self.evaluations = 0
        self._rooms = {room.id: room for room in instance.rooms}
        self._classes = {
            course_class.id: course_class for course_class in instance.classes
        }
        self._class_student_ids: dict[str, set[str]] = {
            class_id: set() for class_id in self._classes
        }
        self._class_move_weight: dict[str, float] = {
            class_id: 0.0 for class_id in self._classes
        }
        self._student_class_ids: dict[str, list[str]] = {}
        for student in instance.students:
            self._student_class_ids[student.id] = list(student.class_ids)
            for enrollment in student.enrollments:
                self._class_student_ids[enrollment.class_id].add(student.id)
                self._class_move_weight[enrollment.class_id] += PRIORITY_WEIGHT[
                    enrollment.priority
                ]
        self.weight: float = self._compute_weight()

    def _compute_weight(self) -> float:
        """
        Hitung bobot pelanggaran keras.

        Bobot dibuat lebih besar daripada total kemungkinan penalti ringan,
        sehingga menghilangkan satu bentrok selalu lebih berharga daripada
        memperbaiki semua penalti ringan sekaligus.

        Returns:
            Bobot untuk pelanggaran keras.
        """
        min_capacity = min(room.capacity for room in self._rooms.values())
        capacity_bound = sum(
            max(0, len(student_ids) - min_capacity) * self._classes[class_id].sks
            for class_id, student_ids in self._class_student_ids.items()
        )
        change_bound = sum(self._class_move_weight.values())
        gap_bound = (
            sum(
                max(0, len(class_ids) - 1)
                for class_ids in self._student_class_ids.values()
            )
            * (DAY_END_MINUTES - DAY_START_MINUTES)
            / GAP_DIVISOR
        )
        return capacity_bound + change_bound + gap_bound + 1

    def hard_violations(self, state: State) -> int:
        """
        Hitung bentrok antar kelas yang waktunya berdekatan pada hari sama.

        Satu bentrok dihitung untuk setiap pasangan kelas yang memakai
        ruangan sama, ditambah satu bentrok untuk setiap mahasiswa yang
        mengambil kedua kelas tersebut.

        Args:
            state: Jadwal yang akan diperiksa.

        Returns:
            Jumlah pelanggaran keras. Nilai 0 berarti jadwal tidak bentrok.
        """
        class_ids = list(self._classes)
        total = 0
        for i in range(len(class_ids)):
            for j in range(i + 1, len(class_ids)):
                first, second = class_ids[i], class_ids[j]
                if not self._is_near(state, first, second):
                    continue
                if (
                    state.allocations[first].room_id
                    == state.allocations[second].room_id
                ):
                    total += 1
                total += len(
                    self._class_student_ids[first] & self._class_student_ids[second]
                )
        return total

    def capacity_penalty(self, state: State) -> float:
        """
        Hitung penalti kekurangan kursi.

        Setiap kelas yang jumlah mahasiswanya melebihi kapasitas ruangan
        memberi penalti sebesar kekurangan kursi dikali jumlah SKS.

        Args:
            state: Jadwal yang akan dinilai.

        Returns:
            Total penalti kapasitas.
        """
        total = 0.0
        for class_id, course_class in self._classes.items():
            room = self._rooms[state.allocations[class_id].room_id]
            shortfall = len(self._class_student_ids[class_id]) - room.capacity
            total += max(0, shortfall) * course_class.sks
        return total

    def change_penalty(self, state: State) -> float:
        """
        Hitung penalti kelas yang hari atau jam mulainya berubah.

        Perpindahan ruangan saja tidak dihitung. Besar penalti mengikuti
        prioritas mahasiswa yang mengambil kelas tersebut.

        Args:
            state: Jadwal yang akan dinilai.

        Returns:
            Total penalti perpindahan.
        """
        total = 0.0
        for class_id, course_class in self._classes.items():
            allocation = state.allocations[class_id]
            if (allocation.day, allocation.start) != (
                course_class.initial.day,
                course_class.initial.start,
            ):
                total += self._class_move_weight[class_id]
        return total

    def gap_penalty(self, state: State) -> float:
        """
        Hitung penalti jeda yang terlalu panjang.

        Untuk setiap mahasiswa, kelas-kelasnya pada hari yang sama diurutkan.
        Jeda antar dua kelas yang melebihi buffer menambah penalti.

        Args:
            state: Jadwal yang akan dinilai.

        Returns:
            Total penalti jeda.
        """
        total = 0.0
        for class_ids in self._student_class_ids.values():
            per_day: dict[str, list[tuple[int, int]]] = {}
            for class_id in class_ids:
                allocation = state.allocations[class_id]
                if allocation.day not in per_day:
                    per_day[allocation.day] = []
                per_day[allocation.day].append(
                    (
                        allocation.start,
                        allocation.start + self._classes[class_id].duration,
                    )
                )
            for meetings in per_day.values():
                meetings.sort()
                for (_, end_a), (start_b, _) in pairwise(meetings):
                    gap = start_b - end_a
                    if gap >= BUFFER_MINUTES:
                        total += (gap - BUFFER_MINUTES) / GAP_DIVISOR
        return total

    def soft_penalty(self, state: State) -> float:
        """
        Jumlahkan semua penalti ringan.

        Args:
            state: Jadwal yang akan dinilai.

        Returns:
            Total penalti kapasitas, perpindahan, dan jeda.
        """
        return (
            self.capacity_penalty(state)
            + self.change_penalty(state)
            + self.gap_penalty(state)
        )

    def evaluate(self, state: State) -> float:
        """
        Hitung nilai akhir jadwal dan tambah jumlah evaluasi.

        Args:
            state: Jadwal yang akan dinilai.

        Returns:
            Nilai jadwal, yaitu penalti ringan ditambah pelanggaran keras
            yang dikalikan bobot.
        """
        self.evaluations += 1
        return self.weight * self.hard_violations(state) + self.soft_penalty(state)

    def _is_near(self, state: State, first: str, second: str) -> bool:
        """
        Periksa apakah dua kelas pada hari yang sama waktunya terlalu dekat.

        Args:
            state: Jadwal yang berisi kedua kelas.
            first: Kode kelas pertama.
            second: Kode kelas kedua.

        Returns:
            True jika keduanya berada pada hari sama dan jaraknya kurang dari
            buffer, False jika tidak.
        """
        a = state.allocations[first]
        b = state.allocations[second]
        if a.day != b.day:
            return False
        end_a = a.start + self._classes[first].duration
        end_b = b.start + self._classes[second].duration
        return a.start < end_b + BUFFER_MINUTES and b.start < end_a + BUFFER_MINUTES
