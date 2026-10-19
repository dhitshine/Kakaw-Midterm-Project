import json
from pathlib import Path

from kakaw.models import Allocation, CourseClass, Enrollment, Instance, Room, Student


class Parser:
    """Baca file JSON instance menjadi `Instance`."""

    def __init__(self, json_file_path: str | Path) -> None:
        self.json_file_path = Path(json_file_path)
        self.data: dict = self.load_json()

    def load_json(self) -> dict:
        try:
            with self.json_file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Error: File {self.json_file_path} not found"
            ) from None
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Error: Invalid JSON in {self.json_file_path} "
                f"({error.msg} at line {error.lineno})"
            ) from error
        return data

    def parse(self) -> Instance:
        rooms = [
            Room(id=entry["kode"], capacity=entry["kapasitas"])
            for entry in self.data["ruangan"]
        ]
        classes = [
            CourseClass(
                id=entry["kode"],
                sks=entry["sks"],
                initial=Allocation(
                    day=entry["jadwal_awal"]["hari"],
                    start=self._to_minutes(entry["jadwal_awal"]["mulai"]),
                    room_id=entry["jadwal_awal"]["kode_ruangan"],
                ),
            )
            for entry in self.data["kelas"]
        ]
        students = [
            Student(
                id=entry["nrp"],
                enrollments=tuple(
                    Enrollment(class_id=class_id, priority=priority)
                    for class_id, priority in zip(entry["kelas"], entry["prioritas"])
                ),
            )
            for entry in self.data["mahasiswa"]
        ]
        return Instance(rooms=rooms, classes=classes, students=students)

    @staticmethod
    def _to_minutes(value: str) -> int:
        hours, minutes = value.split(":")
        return int(hours) * 60 + int(minutes)
