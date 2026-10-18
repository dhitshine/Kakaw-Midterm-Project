import argparse

from kakaw.algorithms import GeneticAlgorithm, SimulatedAnnealing, SteepestHillClimbing
from kakaw.models.constants import DAYS, minutes_to_hhmm
from kakaw.problems import Problem
from kakaw.utils.parser import Parser


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a student-course timetable.",
        epilog="""examples:
  # Run Steepest Ascent Hill-Climbing
  uv run kakaw --test tests/sample.json --algorithm steepest-hc --plot output.png

  # Run Simulated Annealing
  uv run kakaw --test tests/sample.json --algorithm simulated --plot output.png --seed 42

  # Run Genetic Algorithm
  uv run kakaw --test tests/sample.json --algorithm genetic --plot output.png""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-t", "--test", required=True, help="path to test file")

    parser.add_argument(
        "-a",
        "--algorithm",
        required=True,
        choices=["simple-hc", "steepest-hc", "simulated", "genetic"],
        help="algorithm to use",
    )

    parser.add_argument("-p", "--plot", help="path to output plot")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show detailed output"
    )

    parser.add_argument(
        "-s", "--seed", type=int, default=42, help="random seed for stochastic algorithms"
    )

    return parser


def main() -> None:
    args = create_parser().parse_args()

    instance = Parser(args.test).parse()
    problem = Problem(instance)

    if args.algorithm == "steepest-hc":
        solver = SteepestHillClimbing(problem, seed=args.seed)
    elif args.algorithm == "genetic":
        solver = GeneticAlgorithm(problem, seed=args.seed)
    elif args.algorithm == "simulated":
        solver = SimulatedAnnealing(problem, seed=args.seed)
    else:
        raise NotImplementedError(f"Algoritma '{args.algorithm}' belum diimplementasikan")

    goal_state = solver.search()

    # Kontrak Keluaran (§7.4)
    # 1. Baris ringkasan
    h_violations = problem.objective.hard_violations(goal_state)
    p_penalty = problem.objective.soft_penalty(goal_state)
    f_score = problem.objective.weight * h_violations + p_penalty
    feasible = "true" if h_violations == 0 else "false"
    iterations = solver.iteration
    evaluations = problem.objective.evaluations

    print(
        f"algorithm={args.algorithm} F={f_score} H={h_violations} P={p_penalty} "
        f"feasible={feasible} iterations={iterations} evaluations={evaluations}"
    )

    # 2. Tabel jadwal akhir, satu baris per kelas, urut kode kelas menaik
    for class_id in sorted(goal_state.assignments.keys()):
        assignment = goal_state.assignments[class_id]
        print(f"{class_id} {assignment.day} {minutes_to_hhmm(assignment.start)} {assignment.room_id}")

    # Flag --verbose
    if args.verbose:
        p_cap = problem.objective.capacity_penalty(goal_state)
        p_change = problem.objective.change_penalty(goal_state)
        p_gap = problem.objective.gap_penalty(goal_state)
        verbose_str = f"P_kapasitas={p_cap} P_perubahan={p_change} P_jeda={p_gap}"
        if args.algorithm == "simulated" and hasattr(solver, "accepted_moves"):
            verbose_str += f" accepted_moves={solver.accepted_moves}"
        print(verbose_str)
        if args.algorithm == "steepest-hc":
            print(f"riwayat_F={solver.history}")

    # Flag --plot
    if args.plot:
        solver.plot(args.plot)
