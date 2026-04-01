from src.processor import save_chapters_advanced
import argparse


parser = argparse.ArgumentParser(description="Demo script")
parser.add_argument("--book_id", type=int, help="the id of the project gutenberg book", default=5200)
args = parser.parse_args()



if __name__ == "__main__":

    save_chapters_advanced(args.book_id)
