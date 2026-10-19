from collections.abc import Iterable, Sequence

from prettytable import PrettyTable

from kakaw.models import Instance
from kakaw.models.constants import DAYS, minutes_to_hhmm
from kakaw.problems import State


def format_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    table = PrettyTable()
    table.field_names = list(headers)
    table.align = "l"

    for row in rows:
        table.add_row(list(row))

    return table.get_string()


def format_schedule(instance: Instance, state: State) -> str:
    classes = {course_class.id: course_class for course_class in instance.classes}
    tables: list[str] = []

    for room in instance.rooms:
        slots: dict[tuple[int, int], dict[str, list[str]]] = {}

        for class_id, allocation in state.allocations.items():
            if allocation.room_id != room.id:
                continue
            course_class = classes[class_id]
            end = allocation.start + course_class.duration
            key = (allocation.start, end)
            if key not in slots:
                slots[key] = {day: [] for day in DAYS}
            slots[key][allocation.day].append(class_id)

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
