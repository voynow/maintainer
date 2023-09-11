import json
import logging
from pathlib import Path
from pprint import pprint
from typing import List

from llm_blocks import block_factory, blocks
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

logging.basicConfig(level=logging.INFO)


def read_text(path: Path) -> str:
    """
    Read the content of a file

    :param path: The path to the file.
    :return: The content of the file.
    """
    try:
        with open(path, "r") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading file {path}: {e}")
        raise e


def get_ignored_patterns(gitignore_path: Path) -> PathSpec:
    """
    Get a list of patterns to ignore from a .gitignore file

    :param gitignore_path: The path to the .gitignore file
    :return: A compiled list of patterns to ignore
    """
    try:
        gitignore_content = read_text(gitignore_path)
        return PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    except FileNotFoundError:
        logging.warning(".gitignore not found. No files will be ignored based on it.")
        return PathSpec.from_lines(GitWildMatchPattern, [])


def collect_text_from_files(
    dir_path: Path, pathspec: PathSpec, extensions: List[str]
) -> dict[str, str]:
    """
    Recursively collect text from files in a directory.

    :param dir_path: The root directory path.
    :param pathspec: The compiled list of patterns to ignore.
    :return: A dictionary mapping file paths to their content.
    """
    result = {}
    for path in dir_path.iterdir():
        if pathspec.match_file(str(path)):
            continue
        if path.is_file():
            if path.suffix in extensions:
                result[path.name] = read_text(path)
        elif path.is_dir():
            result.update(collect_text_from_files(path, pathspec))
    return result


def analyze_maintainability(
    block: blocks.TemplateBlock, repo: dict[Path, str]
) -> dict[Path, str]:
    """
    Analyze the maintainability of the code in a repository.

    :param block: The template block for llm_blocks.
    :param repo: A dictionary mapping file paths to their content.
    :return: A dictionary mapping file paths to maintainability metrics.
    """
    result = {}
    for path, text in repo.items():
        logging.info(f"Evaluating {path}")
        result[path] = block(filename=path, code=text)
    return result


def generate_output(maintainability_metrics: dict) -> None:
    """
    Generate an output file containing maintainability metrics.

    :param maintainability_metrics: The calculated metrics.
    :return: None
    """
    with open("output.txt", "w") as file:
        file.write(str(maintainability_metrics))


def main() -> None:
    """
    High-level function to run the maintainability analysis

    1. Get a list of patterns to ignore from .gitignore
    2. Collect text from files in the repository
    3. Analyze the maintainability of the code
    4. Generate an output file containing maintainability metrics
    """
    logging.info("Starting maintainability analysis")

    config = json.load(open("config.json", "r"))

    pathspec = get_ignored_patterns(Path(".gitignore"))
    repo = collect_text_from_files(Path("."), pathspec, config["extensions"])
    print(config["prompt"])
    block = block_factory.get(
        "template", template=config["prompt"], model_name="gpt-4", temperature=0.0
    )
    maintainability_metrics = analyze_maintainability(block, repo)
    pprint(maintainability_metrics)

    generate_output(maintainability_metrics)
    logging.info("Completed maintainability analysis")


if __name__ == "__main__":
    main()
