import random

from kakaw.models import Allocation, Instance
from kakaw.models.constants import (
    DAY_END_MINUTES,
    DAY_START_MINUTES,
    DAYS,
    MINUTES_PER_SKS,
    START_GRID_MINUTES,
)
from kakaw.problems.objective import ObjectiveFunction
from kakaw.problems.state import State


class Problem:

    def __init__(self, instance: Instance) -> None:
        """
        Args:
            instance: Data yang berisi ruangan, kelas, dan mahasiswa.
        """
        self.instance = instance
        self.objective = ObjectiveFunction(instance)
        self._classes = {
            course_class.id: course_class for course_class in instance.classes
        }
        self._rooms = {room.id: room for room in instance.rooms}

    def initial_state(self) -> State:
        """
        Ambil jadwal awal dari instance.

        Returns:
            State yang berisi jadwal awal setiap kelas.
        """
        return State.from_instance(self.instance)

    def start_domain(self, sks: int) -> tuple[int, ...]:
        """
        Daftar jam mulai yang mungkin untuk kelas dengan jumlah SKS tertentu.

        Semua pilihan berjarak tetap dan dijamin selesai sebelum jam tutup.

        Args:
            sks: Jumlah SKS kelas.

        Returns:
            Tuple jam mulai dalam menit (start, end, grid).
        """
        last_start = DAY_END_MINUTES - MINUTES_PER_SKS * sks
        return tuple(range(DAY_START_MINUTES, last_start + 1, START_GRID_MINUTES))

    def relocate_candidates(self, state: State, class_id: str) -> list[State]:
        """
        Hasilkan semua kemungkinan pemindahan satu kelas.

        Setiap kandidat memakai hari, jam mulai, dan ruangan lain yang valid.
        Urutan kandidat selalu sama agar pemilihan saat nilai seri konsisten.

        Args:
            state: Jadwal saat ini.
            class_id: Kode kelas yang akan dipindahkan.

        Returns:
            Daftar jadwal baru dengan posisi kelas tersebut diganti.
        """
        candidates: list[State] = []
        current = state.allocations[class_id]
        for day in DAYS:
            for start in self.start_domain(self._classes[class_id].sks):
                for room_id in self._rooms:
                    if (day, start, room_id) == (
                        current.day,
                        current.start,
                        current.room_id,
                    ):
                        continue
                    candidates.append(
                        state.replace({class_id: Allocation(day, start, room_id)})
                    )
        return candidates

    def swap_candidates(self, state: State) -> list[State]:
        """
        Hasilkan semua kemungkinan pertukaran waktu antara dua kelas.

        Yang bertukar hanya hari dan jam mulai; setiap kelas tetap memakai
        ruangannya sendiri. Pertukaran yang melewati jam tutup dilewati.

        Args:
            state: Jadwal saat ini.

        Returns:
            Daftar jadwal baru dengan waktu dua kelas bertukar.
        """
        candidates: list[State] = []
        class_ids = sorted(self._classes)
        for i in range(len(class_ids)):
            for j in range(i + 1, len(class_ids)):
                swapped = self._swapped_state(state, class_ids[i], class_ids[j])
                if swapped is not None:
                    candidates.append(swapped)
        return candidates

    def get_all_successors(self, state: State) -> list[State]:
        """
        Hasilkan semua jadwal yang berbeda satu gerakan.

        Urutan tetap: relocate per kelas (kode kelas, hari, jam, ruangan),
        lalu swap antar pasangan kelas.

        Args:
            state: Jadwal saat ini.

        Returns:
            Daftar semua jadwal tetangga yang valid.
        """
        neighbors: list[State] = []
        for class_id in state.allocations:
            for neighbor in self.relocate_candidates(state, class_id):
                neighbors.append(neighbor)
        for neighbor in self.swap_candidates(state):
            neighbors.append(neighbor)
        return neighbors

    def random_relocate(self, state: State, class_id: str, rng: random.Random) -> State:
        """
        Pindahkan satu kelas ke hari, jam, dan ruangan acak yang berbeda.

        Args:
            state: Jadwal saat ini.
            class_id: Kode kelas yang akan dipindahkan.
            rng: Sumber angka acak.

        Returns:
            Jadwal baru dengan posisi kelas tersebut diganti.
        """
        current = state.allocations[class_id]
        domain = self.start_domain(self._classes[class_id].sks)
        while True:
            candidate = Allocation(
                rng.choice(DAYS), rng.choice(domain), rng.choice(tuple(self._rooms))
            )
            if candidate != current:
                return state.replace({class_id: candidate})

    def random_swap(self, state: State, rng: random.Random) -> State | None:
        """
        Tukar hari dan jam dua kelas yang dipilih acak.

        Ruangan setiap kelas tidak ikut bertukar.

        Args:
            state: Jadwal saat ini.
            rng: Sumber angka acak.

        Returns:
            Jadwal baru jika pertukaran valid, atau None jika jumlah kelas
            kurang dari dua atau pertukaran melewati jam tutup.
        """
        class_ids = tuple(self._classes)
        if len(class_ids) < 2:
            return None
        first, second = rng.sample(class_ids, 2)
        return self._swapped_state(state, first, second)

    def random_successor(self, state: State, rng: random.Random) -> State:
        """
        Buat satu jadwal tetangga secara acak.

        Algoritma mencoba menukar waktu dua kelas. Jika tidak memungkinkan,
        satu kelas dipindahkan ke hari, jam, dan ruangan acak.

        Args:
            state: Jadwal saat ini.
            rng: Sumber angka acak.

        Returns:
            Jadwal baru hasil satu perubahan acak.
        """
        class_ids = tuple(self._classes.keys())
        if not class_ids:
            return state

        # Coba swap lebih dulu; jika tidak valid, lanjut ke relocate.
        if len(class_ids) >= 2 and rng.random() < 0.3:
            swapped = self.random_swap(state, rng)
            if swapped is not None:
                return swapped

        class_id = rng.choice(class_ids)
        return self.random_relocate(state, class_id, rng)

    def _swapped_state(self, state: State, first: str, second: str) -> State | None:
        """
        Tukar hari dan jam dua kelas tanpa mengubah ruangannya.

        Args:
            state: Jadwal saat ini.
            first: Kode kelas pertama.
            second: Kode kelas kedua.

        Returns:
            Jadwal baru jika pertukaran valid, atau None jika kedua kelas
            berada pada waktu yang sama atau hasilnya melewati jam tutup.
        """
        a = state.allocations[first]
        b = state.allocations[second]
        if (a.day, a.start) == (b.day, b.start):
            return None
        if b.start + self._classes[first].duration > DAY_END_MINUTES:
            return None
        if a.start + self._classes[second].duration > DAY_END_MINUTES:
            return None
        return state.replace(
            {
                first: Allocation(b.day, b.start, a.room_id),
                second: Allocation(a.day, a.start, b.room_id),
            }
        )
