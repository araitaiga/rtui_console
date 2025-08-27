#!/usr/bin/env python3
"""
ROS2 Console Viewer - TUI version of rqt_console using Textual
Entry point for the application
"""
from .app import ConsoleApp


def main():
    """Main entry point"""
    app = ConsoleApp()
    app.run()


if __name__ == "__main__":
    main()
