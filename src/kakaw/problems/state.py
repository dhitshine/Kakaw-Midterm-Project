from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from kakaw.models import Allocation, Instance


class State:
    """Susunan lengkap jadwal: setiap kode kelas dipetakan ke satu penempatan."""

    def __init__(self, allocations: dict[str, Allocation] | None = None):
        """
        Args:
            allocations: Pemetaan kode kelas ke penempatannya. Jika None,
                state dibuat kosong.
        """
        self.allocations: dict[str, Allocation] = (
            {} if allocations is None else allocations
        )

    @classmethod
    def from_instance(cls, instance: Instance) -> State:
        return cls(
            {course_class.id: course_class.initial for course_class in instance.classes}
        )

    def copy(self) -> State:
        new_state = deepcopy(State(dict(self.allocations)))
        return new_state

    def replace(self, updates: Mapping[str, Allocation]) -> State:
        allocations = dict(self.allocations)
        allocations.update(updates)
        return State(allocations)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return NotImplemented
        return self.allocations == other.allocations
