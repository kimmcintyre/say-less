import argparse
from collector import Collector
from exporter import Exporter
from settings import DEFAULT_LOGGING_LEVEL
import logging
from project_types.types import Table

logging.basicConfig(
    level=DEFAULT_LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def gather_command(args):
    config_path: str = args.configPath
    service_account_path: str = args.serviceAccountPath
    max_results: int = args.maxResults
    collector: Collector = Collector(config_path, service_account_path)
    table: Table = collector.get_youtube_videos(max_results)
    exporter: Exporter = Exporter(config_path, service_account_path)
    exporter.export_table(table)
    logging.info("YouTube links collected successfully")

if __name__ == "__main__":
    # Prepare CLI arguments
    # Create the top-level "say-less" parser
    parser = argparse.ArgumentParser(
        prog='say-less',
        description="Capture the YouTube zeitgeist by automatically collecting links to videos that can be fed into NotebookLM",
        epilog="""\
        Examples:
        uv run say-less.py gather --configPath "./local/configs.json" --serviceAccountPath "./local/secrets/service-account.json"
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(help='subcommand help')
    # create the parser for the "transcribe" sub-command
    parser_gather = subparsers.add_parser('gather', help='Gather YouTube links from the specified channel handles and saves them to a specified google sheet')
    parser_gather.add_argument("--configPath", type=str, help='Path to config file. Defaults to "./local/configs.json"')
    parser_gather.add_argument("--serviceAccountPath", type=str, help='Path to service account file. Defaults to "./local/secrets/service-account.json"')
    parser_gather.add_argument("--maxResults", type=int, help="Returns the lastest N videos to return per channel. Default value is the lastest 50 videos") 
    parser_gather.set_defaults(func=gather_command)

    # Call function for corresponding sub-command based on the args provided 
    args = parser.parse_args()
    args.func(args)