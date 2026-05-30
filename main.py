import json
from core.dialogue_tree import DialogueNode, DialogueTree
from core.dialogue_tree import load_dialogue_from_json

def print_dialogue_tree(tree: DialogueTree):
    """Print the dialogue tree in a readable format."""
    print(f"\n=== {tree.title} ===")
    print(f"Starting node: {tree.start_node_id}\n")

    for node_id, node in tree.nodes.items():
        print(f"[{node.speaker}] — {node.text}")
        if node.choices:
            for i, choice in enumerate(node.choices, 1):
                print(f"  {i}. {choice['text']} → {choice['next_node_id']}")
        else:
            print("  (End of dialogue)")
        print()


if __name__ == "__main__":
    tree = load_dialogue_from_json("data/example_dialogue.json")
    print_dialogue_tree(tree)
