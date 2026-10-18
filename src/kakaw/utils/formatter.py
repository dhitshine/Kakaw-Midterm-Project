"""Pembuat tabel teks untuk output CLI."""

from collections.abc import Iterable, Sequence

from prettytable import PrettyTable

from kakaw.models import Instance
from kakaw.models.constants import DAYS, minutes_to_hhmm
from kakaw.problems import State


def format_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    """
    Susun data menjadi tabel teks dengan kolom yang sejajar.

    Args:
        headers: Nama kolom, berurutan dari kiri ke kanan.
        rows: Baris data. Setiap baris harus memiliki jumlah kolom yang
            sama dengan jumlah header.

    Returns:
        Tabel siap cetak sebagai string.
    """
    table = PrettyTable()
    table.field_names = list(headers)
    table.align = "l"

    for row in rows:
        table.add_row(list(row))

    return table.get_string()


def format_schedule(instance: Instance, state: State) -> str:
    """
    Susun jadwal menjadi satu tabel untuk setiap ruangan.

    Judul tabel adalah kode ruangan. Kolom berisi hari, baris berisi rentang
    waktu, dan setiap sel berisi kelas yang dijadwalkan pada slot tersebut.

    Args:
        instance: Data kasus yang berisi daftar kelas dan ruangan.
        state: Jadwal yang akan ditampilkan.

    Returns:
        Semua tabel ruangan siap cetak, dipisahkan baris kosong.
    """
    classes = {course_class.id: course_class for course_class in instance.classes}
    tables: list[str] = []

    for room in instance.rooms:
        slots: dict[tuple[int, int], dict[str, list[str]]] = {}

        for class_id, assignment in state.assignments.items():
            if assignment.room_id != room.id:
                continue
            course_class = classes[class_id]
            end = assignment.start + course_class.duration
            key = (assignment.start, end)
            slots.setdefault(key, {day: [] for day in DAYS})
            slots[key][assignment.day].append(class_id)

        table = PrettyTable()
        table.field_names = ["Waktu", *DAYS]
        table.align = "l"
        table.title = f"{room.id}:"

        for start, end in sorted(slots):
            row = [f"{minutes_to_hhmm(start)} - {minutes_to_hhmm(end)}"]
            for day in DAYS:
                entries = sorted(slots[(start, end)][day])
                row.append(", ".join(entries) if entries else "-")
            table.add_row(row)

        tables.append(table.get_string())

    return "\n\n".join(tables)
