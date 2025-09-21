import argparse
import re
import sys
import os
import shutil
from pathlib import Path,PosixPath
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SeriesDirectory:
    dir_owner = None
    series_destination_directory = None
    tv_show_file_patterns = [r'.*\.mkv$', r'.*\.mp4$', r'.*\.avi$']

    def __init__(self, path:PosixPath):
        self.posix_path = path
        self.directory = str(path)
        self.dir_name = path.name
        self.show_name = self.get_show_name()
        self.season_number = self.get_season_number()
        self.disc_number = self.get_disc_number()
        self.episode_files = self.get_episodes()

    def __lt__(self, other):
        return (self.name, self.season, self.disc) < (other.show_name, other.season_number, other.disc_number)

    def __eq__(self, other):
        return (self.name, self.season, self.disc) == (other.show_name, other.season_number, other.disc_number)

    def __repr__(self):
        return f"SeriesDirectory(dirname='{self.directory}', name='{self.show_name}', season={self.season_number}, disc={self.disc_number})"

    @property
    def name(self) -> str:
        return self.show_name if self.show_name else "Unknown"
    @property
    def disc(self) -> str:
        return int(self.disc_number) if self.disc_number else "Unknown"
    @property
    def season(self) -> str:
        return int(self.season_number) if self.season_number else "Unknown"
    @property
    def iterable(self) -> bool:
        return all([self.season_number, self.disc_number, self.show_name])

    def get_season_number(self) -> int:
        match = re.search(r'[Ss](\d{1,2})', self.dir_name)
        if match:
            return int(match.group(1))
        return None

    def get_disc_number(self) -> int:
        match = re.search(r'[Dd]isc(\d{1,2})', self.dir_name)
        if match:
            return int(match.group(1))
        return None

    def get_show_name(self) -> str:
        match = re.search(r"^(?P<series>.+?)\s[Ss]\d{1,2}[- ]Disc\d+\s\(\d{4}.*\)", self.dir_name)
        if match:
            return match.group('series').strip()
        logger.warning(f"Could not parse show name from '{self.dir_name}'")
        return None

    def get_episodes(self) -> list:
        """
        Checks if the specified directory contains TV show files.
        :return: a list of tv show episodes found in the directory, sorted by disc folder alphabetically
        """
        dir_path = self.posix_path
        if not dir_path.is_dir():
            raise ValueError(f"The path {self.dir_name} is not a valid directory.")
        
        tv_show_files = [item for item in dir_path.iterdir() if item.is_file() and any(re.match(pattern, item.name, re.IGNORECASE) for pattern in self.tv_show_file_patterns)]
        logger.debug(f"Found {len(tv_show_files)} TV show files in directory '{self.dir_name}'.")
        if tv_show_files:
            # Sorts by file name expecting this input: (B1_t00.mkv, C1_t01.mkv, ...)
            sorted_files = sorted(tv_show_files, key=lambda x: x.name)
            logger.debug(f"Sorted files: {[f.name for f in sorted_files]}")
            return sorted_files
        else:
            logger.debug(f"Found no files under: {self.dir_name}")
            return []

    def generate_show_folder_name(self) -> str:
        """
        Generates a folder name for the season.
        :return: A formatted season folder name string.
        """
        if not self.show_name:
            raise ValueError("Show name must be set to generate a season folder name.")
        return f"{self.show_name}"

    def generate_season_folder_name(self) -> str:
        """
        Generates a folder name for the season.
        :return: A formatted season folder name string.
        """
        if not self.show_name or not self.season_number:
            raise ValueError("Show name and season number must be set to generate a season folder name.")
        return f"{self.show_name} - Season {self.season_number:02d}"

    def generate_plex_file_name(self, episode_index:int, file_extension:str) -> str:
        """
        Generates a Plex-compatible file name for an episode.
        :param episode_index: The episode index (1-based).
        :param file_extension: The file extension (e.g., '.mkv').
        :return: A formatted file name string.
        """
        if not self.show_name or not self.season_number:
            raise ValueError("Show name and season number must be set to generate a Plex file name.")
        return f"{self.show_name} - S{self.season_number:02d} E{episode_index:02d}{file_extension}"

def get_directory_content(directory:str):
    """
    Returns a list of files and directories in the specified directory.
    
    :param directory: The path to the directory to list.
    :return: A list of file and directory names.
    """
    from pathlib import Path

    posix_path = Path(directory)
    if not posix_path.is_dir():
        raise ValueError(f"The path {directory} is not a valid directory.")
    
    return [item for item in posix_path.iterdir() if item.is_dir()]
    

def parse_tv_shows(list_of_dirs:list):
    assert all(isinstance(x, SeriesDirectory) for x in list_of_dirs), "All elements must be SeriesDirectory instances."
    all_shows = set((x.name for x in list_of_dirs if x.iterable))
    logger.debug(f"Found {len(all_shows)} unique shows: {', '.join(all_shows)}")
    show_episodes = {}
    # Iterate
    if not SeriesDirectory.series_destination_directory:
        raise ValueError("Destination directory for TV shows is not set.")
    for show in all_shows:
        show_episodes[show] = []
        parsed_discs = []
        logger.debug((len(show) + 17) * "*")
        logger.info(f"Processing show: {show}")
        show_discs = [x for x in list_of_dirs if x.name == show and x.iterable]
        logger.debug(f"Show '{show}' year has {len(show_discs)} discs.")
        for disc in show_discs:
            episodes = disc.episode_files
            if episodes:
                logger.info(f"Found {len(episodes)} episodes in disc '{disc.dir_name}'")
                show_episodes[show] += episodes # combine both lists
        logger.info(f"Total episodes found for show '{show}': {len(show_episodes[show])}")
        # Validate that we have all discs and that they are consecutive
        if parsed_discs:
            sorted_discs = sorted(parsed_discs)
            consecutive = all((b - a) == 1 for a, b in zip(sorted_discs, sorted_discs[1:]))
            expected_discs = set(range(sorted_discs[0], sorted_discs[-1] + 1))
            missing_discs = expected_discs - set(sorted_discs)
            if missing_discs:
                logger.warning(f"Missing discs for show '{show}': {sorted(missing_discs)}")
            elif not consecutive:
                logger.warning(f"Discs for show '{show}' are not consecutive: {sorted_discs}")
            else:
                for season in set((x.season for x in show_discs)):
                    destination_dir_name = f"{SeriesDirectory.series_destination_directory}/{show}/Season {season}"
                    create_directory(Path(destination_dir_name))
                    
                logger.info(f"All discs present and consecutive for show '{show}'.")
                logger.info("Preparing to move and rename episodes... ")
                # Calculer l'index de départ en fonction des fichiers déjà présents
                dest_dir = os.path.join(SeriesDirectory.series_destination_directory, show, f"Season {season}")
                existing_files = [f for f in os.listdir(dest_dir) if os.path.isfile(os.path.join(dest_dir, f))]
                existing_indices = []
                import re
                for f in existing_files:
                    m = re.search(r"S\d{2}E(\d{2})", f)
                    if m:
                        existing_indices.append(int(m.group(1)))
                start_idx = max(existing_indices) + 1 if existing_indices else 1
                logger.info(f"Starting episode index for renaming: {start_idx}")
                for offset, episode in enumerate(show_episodes[show]):
                    idx = start_idx + offset
                    file_extension = episode.suffix
                    new_file_name = disc.generate_plex_file_name(idx, file_extension)
                    source_path = episode.absolute()
                    destination_path = os.path.join(dest_dir, new_file_name)
                    if os.path.exists(destination_path):
                        logger.warning(f"File already exists, skipping: {destination_path}")
                        continue
                    logger.info(f"Moving '{episode.name}' to '{new_file_name}' in destination directory")
                    shutil.move(source_path, destination_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Parse and sort TV series directories.")
    parser.add_argument('--dir_to_parse', type=str, default="/qbittorrent-staging/automatic_ripping_machine/media/completed/tv", help='Path to the directory to parse')
    parser.add_argument('--destination_tv_shows', type=str, default="/micropool/Videos/TV/", help='Path to the directory to parse')
    return parser.parse_args()

def create_directory(path:PosixPath):
    """
    Creates a directory if it does not exist.
    
    :param path: The path to the directory to create.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path}")
    else:
        logger.info(f"Directory already exists: {path}")

def main():
    # Ensure the script is run with Python 3.6 or higher
    if sys.version_info < (3, 6):
        print("This script requires Python 3.6 or higher.")
        sys.exit(1)

    args = parse_args()
    SeriesDirectory.series_destination_directory = args.destination_tv_shows
    dir_to_parse = args.dir_to_parse

    # Récupère la liste des dossiers à parser

    if dir_to_parse:
        try:
            directory_list = get_directory_content(dir_to_parse)
        except PermissionError as e:
            if hasattr(e, 'errno') and e.errno == 13:
                print(f"Permission denied when reading directory '{dir_to_parse}'. Try running as a user with access rights.")
            else:
                print(f"Permission error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading directory '{dir_to_parse}': {e}")
            sys.exit(1)
    else:
        print("No directory specified to parse.")
        sys.exit(1)
    
    parsed_directories = []
    for dir_name in directory_list:
        series_dir = SeriesDirectory(dir_name.absolute())
        if series_dir.iterable:
            logger.debug(f"Parsed '{dir_name}': Show='{series_dir.show_name}', Season='{series_dir.season_number}', Disc='{series_dir.disc_number}'")
            parsed_directories.append(series_dir)
        else:
            print(f"Failed to parse '{dir_name}': Incomplete information.")
    sorted_values = sorted(parsed_directories)
    print(sorted_values, sep="\n")
    parse_tv_shows(sorted_values)

if __name__ == "__main__":
    main()