import argparse
import os
from jobpilot.utils.config import load_configs

def cli():
    p = argparse.ArgumentParser(prog="jobpilot")
    p.add_argument("cmd", choices=["run", "check"])
    p.add_argument("--provider", default="dice")
    p.add_argument("--profile", default="configs/profile.yaml")
    p.add_argument("--search", default="configs/searches.yaml")
    args = p.parse_args()

    cfg = load_configs(args.profile, args.search)
    if args.cmd == "check":
        print("Loaded config OK for provider:", args.provider)
        print(cfg.keys())
    elif args.cmd == "run":
        # placeholder – wired in Step 8/Runner
        print(f"Runner not wired yet. Provider={args.provider}")
        print("Next: implement DiceProvider and Orchestrator.")

if __name__ == "__main__":
    cli()
