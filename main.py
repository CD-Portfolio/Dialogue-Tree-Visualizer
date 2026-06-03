import os

from core.dialogue_tree import (
    DialogueTree,
    load_dialogue_from_json
)


def print_dialogue_tree(tree: DialogueTree):
    """Print the dialogue tree in readable format."""

    print(f"\n=== {tree.title} ===")
    print(f"Starting node: {tree.start_node_id}\n")

    for node_id, node in tree.nodes.items():

        print(f"[{node.speaker}] — {node.text}")

        if node.choices:

            for i, choice in enumerate(
                node.choices,
                1
            ):

                print(
                    f"  {i}. "
                    f"{choice['text']} "
                    f"→ "
                    f"{choice['next_node_id']}"
                )

        else:

            print(
                "  (End of dialogue)"
            )

        print()


DEFAULT_FILE = (
    "data/example_dialogue.json"
)


if __name__ == "__main__":

    if os.path.exists(
        DEFAULT_FILE
    ):

        tree = load_dialogue_from_json(
            DEFAULT_FILE
        )

    else:

        print(
            "Example file not found."
        )

        tree = DialogueTree(
            "Empty Dialogue"
        )

    print_dialogue_tree(
        tree
    )