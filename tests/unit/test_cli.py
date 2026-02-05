"""Tests for CLI argument parsing."""
from unittest import mock

import pytest

from dirq.cli import create_parser, main


class TestArgumentParsing:
    """Test CLI argument parsing and subcommand routing."""

    def test_top_level_help(self) -> None:
        """Top-level --help should work."""
        parser = create_parser()
        with mock.patch("sys.argv", ["dirq", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                parser.parse_args(["--help"])
            assert exc_info.value.code == 0

    def test_navigate_subcommand(self) -> None:
        """Navigate subcommand parses correctly."""
        parser = create_parser()
        args = parser.parse_args(["navigate"])
        assert args.command == "navigate"
        assert not hasattr(args, "only") or args.only is None
        assert not hasattr(args, "except_names") or args.except_names is None

    def test_navigate_with_only_flag(self) -> None:
        """Navigate --only flag parses."""
        parser = create_parser()
        args = parser.parse_args(["navigate", "--only", "name1,name2"])
        assert args.command == "navigate"
        assert args.only == "name1,name2"

    def test_navigate_with_except_flag(self) -> None:
        """Navigate --except flag parses."""
        parser = create_parser()
        args = parser.parse_args(["navigate", "--except", "name1,name2"])
        assert args.command == "navigate"
        assert args.except_names == "name1,name2"

    def test_save_subcommand_defaults(self) -> None:
        """Save subcommand with defaults."""
        parser = create_parser()
        args = parser.parse_args(["save"])
        assert args.command == "save"
        assert args.path is None  # Will default to cwd in handler
        assert args.depth == 0
        assert args.name is None  # Will default to basename in handler

    def test_save_with_path_only(self) -> None:
        """Save with explicit path."""
        parser = create_parser()
        args = parser.parse_args(["save", "/opt/repos"])
        assert args.command == "save"
        assert args.path == "/opt/repos"

    def test_save_with_path_and_depth(self) -> None:
        """Save with path and depth."""
        parser = create_parser()
        args = parser.parse_args(["save", "/opt/repos", "2"])
        assert args.command == "save"
        assert args.path == "/opt/repos"
        assert args.depth == 2

    def test_save_with_all_args(self) -> None:
        """Save with path, depth, and name."""
        parser = create_parser()
        args = parser.parse_args(["save", "/opt/repos", "2", "myrepos"])
        assert args.command == "save"
        assert args.path == "/opt/repos"
        assert args.depth == 2
        assert args.name == "myrepos"

    def test_delete_requires_argument(self) -> None:
        """Delete requires name-or-path argument."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["delete"])

    def test_delete_with_argument(self) -> None:
        """Delete with name-or-path."""
        parser = create_parser()
        args = parser.parse_args(["delete", "repos"])
        assert args.command == "delete"
        assert args.name_or_path == "repos"

    def test_init_config_subcommand(self) -> None:
        """Init config subcommand parses."""
        parser = create_parser()
        args = parser.parse_args(["init", "config"])
        assert args.command == "init"
        assert args.init_type == "config"

    def test_init_shell_requires_argument(self) -> None:
        """Init shell requires shell-type argument."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["init", "shell"])

    def test_init_shell_with_argument(self) -> None:
        """Init shell with shell-type."""
        parser = create_parser()
        args = parser.parse_args(["init", "shell", "fish"])
        assert args.command == "init"
        assert args.init_type == "shell"
        assert args.shell_type == "fish"


class TestSubcommandRouting:
    """Test that subcommands route to appropriate handlers."""

    def test_navigate_handler_stub(self) -> None:
        """Navigate subcommand routes (stub test)."""
        with mock.patch("sys.argv", ["dirq", "navigate"]):
            with mock.patch("dirq.cli.handle_navigate", return_value=0) as mock_handler:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_handler.assert_called_once()

    def test_save_handler_stub(self) -> None:
        """Save subcommand routes (stub test)."""
        with mock.patch("sys.argv", ["dirq", "save"]):
            with mock.patch("dirq.cli.handle_save", return_value=0) as mock_handler:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_handler.assert_called_once()

    def test_delete_handler_stub(self) -> None:
        """Delete subcommand routes (stub test)."""
        with mock.patch("sys.argv", ["dirq", "delete", "repos"]):
            with mock.patch("dirq.cli.handle_delete", return_value=0) as mock_handler:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_handler.assert_called_once()

    def test_init_config_handler_stub(self) -> None:
        """Init config subcommand routes (stub test)."""
        with mock.patch("sys.argv", ["dirq", "init", "config"]):
            with mock.patch("dirq.cli.handle_init_config", return_value=0) as mock_handler:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_handler.assert_called_once()

    def test_init_shell_handler_stub(self) -> None:
        """Init shell subcommand routes (stub test)."""
        with mock.patch("sys.argv", ["dirq", "init", "shell", "fish"]):
            with mock.patch("dirq.cli.handle_init_shell", return_value=0) as mock_handler:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_handler.assert_called_once()
