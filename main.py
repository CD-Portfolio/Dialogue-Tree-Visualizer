import json
from core.dialogue_tree import DialogueNode, DialogueTree



def load_dialogue_from_json(filepath: str) -> DialogueTree:
    """Load a dialogue tree from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    tree = DialogueTree(title=data["title"])
    tree.set_start(data["start_node_id"])

    for node_data in data["nodes"]:
        node = DialogueNode(
            node_id=node_data["node_id"],
            speaker=node_data["speaker"],
            text=node_data["text"]
        )
        for choice in node_data["choices"]:
            node.add_choice(choice["text"], choice["next_node_id"])

        tree.add_node(node)

    return tree


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
