"""
Combines questions from Part A and Part B to form the complete Section 25.
"""
from .questions_data_partA import get_part_a
from .questions_data_partB import get_part_b

def get_all_questions_markdown() -> str:
    part_a = get_part_a()
    part_b = get_part_b()
    return f"{part_a}\n\n---\n\n{part_b}\n"
