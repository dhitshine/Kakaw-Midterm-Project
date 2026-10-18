import argparse

from kakaw.algorithms import GeneticAlgorithm, SimulatedAnnealing, SteepestHillClimbing
from kakaw.problems import Problem
from kakaw.utils.formatter import format_schedule
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
        choices=["steepest-hc", "simulated", "genetic"],
        help="algorithm to use",
    )

    parser.add_argument("-p", "--plot", help="path to output plot")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show detailed output"
    )

    parser.add_argument(
        "-s", "--seed", type=int, default=42, help="random seed for stochastic algorithms"
    )

    limits = parser.add_argument_group("steepest-hc / simulated annealing")
    limits.add_argument(
        "--max-iteration",
        type=int,
        default=None,
        help="maximum iterations (default: 1000 for steepest-hc, 20000 for simulated)",
    )

    simulated = parser.add_argument_group("simulated annealing")
    simulated.add_argument(
        "--initial-temp",
        type=float,
        default=None,
        help="initial temperature (default: 5 x objective weight)",
    )
    simulated.add_argument(
        "--rate",
        type=float,
        default=0.995,
        help="cooling rate, 0 < rate < 1 (default: 0.995)",
    )

    genetic = parser.add_argument_group("genetic algorithm")
    genetic.add_argument(
        "--populations",
        type=int,
        default=50,
        help="number of individuals per generation (default: 50)",
    )
    genetic.add_argument(
        "--generations",
        type=int,
        default=200,
        help="number of generations (default: 200)",
    )

    return parser


def main() -> None:
    args = create_parser().parse_args()

    instance = Parser(args.test).parse()
    problem = Problem(instance)

    if args.algorithm == "steepest-hc":
        solver = SteepestHillClimbing(
            problem,
            max_iterations=(
                args.max_iteration if args.max_iteration is not None else 1000
            ),
        )
    elif args.algorithm == "genetic":
        solver = GeneticAlgorithm(
            problem,
            N=args.populations,
            G=args.generations,
            seed=args.seed,
        )
    elif args.algorithm == "simulated":
        solver = SimulatedAnnealing(
            problem,
            max_iterations=(
                args.max_iteration if args.max_iteration is not None else 20000
            ),
            T0=args.initial_temp,
            rho=args.rate,
            seed=args.seed,
        )
    else:
        raise NotImplementedError(f"Algoritma '{args.algorithm}' belum diimplementasikan")

    goal_state = solver.search()

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

    # 2. Tabel jadwal akhir: waktu versus hari, sel berisi ruangan:kelas
    print(format_schedule(instance, goal_state))

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
