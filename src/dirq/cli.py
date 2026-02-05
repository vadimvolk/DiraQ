"""CLI argument parsing and subcommand dispatch."""
import argparse
import sys
from pathlib import Path
from typing import Any

from dirq.config import delete_bookmark, init_config, read_config, save_bookmark
from dirq.navigator import build_navigation_list, run_fzf
from dirq.platform import get_config_path
from dirq.shell import (
    generate_shell_script,
    get_installation_instructions,
    install_completion,
    install_wrapper,
)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="dirq",
        description="Fast folder navigation with fzf integration",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Navigate subcommand
    navigate_parser = subparsers.add_parser(
        "navigate", help="Navigate to a bookmarked folder via fzf"
    )
    navigate_parser.add_argument(
        "--only", type=str, help="Comma-separated list of bookmark names to include"
    )
    navigate_parser.add_argument(
        "--except",
        dest="except_names",
        type=str,
        help="Comma-separated list of bookmark names to exclude",
    )

    # Save subcommand
    save_parser = subparsers.add_parser("save", help="Save a folder bookmark")
    save_parser.add_argument(
        "path", nargs="?", default=None, help="Path to bookmark (default: current directory)"
    )
    save_parser.add_argument(
        "depth", nargs="?", type=int, default=0, help="Subfolder scan depth 0-10 (default: 0)"
    )
    save_parser.add_argument(
        "name", nargs="?", default=None, help="Unique bookmark name (default: basename of path)"
    )

    # Delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Remove a bookmark from config")
    delete_parser.add_argument("name_or_path", help="Bookmark name or absolute path")

    # Init subcommand with config/shell sub-subcommands
    init_parser = subparsers.add_parser(
        "init", help="Initialize configuration or shell integration"
    )
    init_subparsers = init_parser.add_subparsers(dest="init_type", help="What to initialize")

    # Init config
    init_subparsers.add_parser("config", help="Create the default config file")

    # Init shell
    shell_parser = init_subparsers.add_parser("shell", help="Generate shell integration script")
    shell_parser.add_argument("shell_type", help="Shell type (fish, bash, zsh)")

    return parser


def handle_navigate(args: Any) -> int:
    """Handle navigate subcommand."""
    try:
        # Read config
        config_path = get_config_path()
        entries = read_config(config_path)

        # Parse --only and --except flags
        only = None
        if args.only:
            only = [name.strip() for name in args.only.split(",")]

        except_names = None
        if args.except_names:
            except_names = [name.strip() for name in args.except_names.split(",")]

        # Build navigation list
        nav_entries, warnings = build_navigation_list(entries, only, except_names)

        # Print warnings to stderr
        for warning in warnings:
            print(warning, file=sys.stderr)

        # Run fzf
        selected_path = run_fzf(nav_entries)

        if selected_path is None:
            # User cancelled (Ctrl+C or no match)
            return 1

        # Print selected path to stdout
        print(selected_path)
        return 0

    except FileNotFoundError as e:
        if "fzf" in str(e):
            print("error: fzf not found. Please install fzf.", file=sys.stderr)
        else:
            print("error: config file not found. Run 'dirq init config' first.", file=sys.stderr)
        return 2
    except ValueError as e:
        # Error messages from navigation already start with "error:"
        error_msg = str(e)
        if not error_msg.startswith("error:"):
            error_msg = f"error: {error_msg}"
        print(error_msg, file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def handle_save(args: Any) -> int:
    """Handle save subcommand."""
    try:
        config_path = get_config_path()

        # Convert path to Path object if provided
        path = Path(args.path) if args.path else None

        # Call save_bookmark with appropriate arguments
        message = save_bookmark(
            config_path=config_path,
            path=path,
            depth=args.depth,
            name=args.name,
        )

        print(message)
        return 0

    except FileNotFoundError:
        print("error: config file not found. Run 'dirq init config' first.", file=sys.stderr)
        return 2
    except ValueError as e:
        # Error messages from save_bookmark already start with "error:"
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def handle_delete(args: Any) -> int:
    """Handle delete subcommand."""
    try:
        config_path = get_config_path()
        message = delete_bookmark(config_path, args.name_or_path)

        print(message)
        return 0

    except FileNotFoundError:
        print("error: config file not found. Run 'dirq init config' first.", file=sys.stderr)
        return 2
    except ValueError as e:
        # Error messages from delete_bookmark already start with "error:"
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def handle_init_config(args: Any) -> int:
    """Handle init config subcommand."""
    try:
        config_path = get_config_path()
        message = init_config(config_path)

        # If already exists, message goes to stderr (informational)
        if "already exists" in message:
            print(message, file=sys.stderr)
        else:
            print(message)

        return 0
    except OSError as e:
        print(f"error: failed to create config: {e}", file=sys.stderr)
        return 2


def handle_init_shell(args: Any) -> int:
    """Handle init shell subcommand."""
    try:
        shell = args.shell_type

        # Validate shell
        valid_shells = {"bash", "zsh", "fish"}
        if shell not in valid_shells:
            print(
                f"error: Invalid shell '{shell}'. Must be one of: {', '.join(sorted(valid_shells))}",
                file=sys.stderr,
            )
            return 2

        # Install completion
        try:
            completion_path = install_completion(shell)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        except OSError as e:
            print(f"error: installing completion: {e}", file=sys.stderr)
            return 2

        # Install wrapper
        try:
            wrapper_path = install_wrapper(shell)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        except OSError as e:
            print(f"error: installing wrapper: {e}", file=sys.stderr)
            return 2

        # Print instructions
        instructions = get_installation_instructions(shell, completion_path, wrapper_path)
        print(instructions)

        return 0

    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to appropriate handler
    if args.command == "navigate":
        exit_code = handle_navigate(args)
    elif args.command == "save":
        exit_code = handle_save(args)
    elif args.command == "delete":
        exit_code = handle_delete(args)
    elif args.command == "init":
        if args.init_type == "config":
            exit_code = handle_init_config(args)
        elif args.init_type == "shell":
            exit_code = handle_init_shell(args)
        else:
            parser.print_help()
            exit_code = 2
    else:
        parser.print_help()
        exit_code = 2

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
