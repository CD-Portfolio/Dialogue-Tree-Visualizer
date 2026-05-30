import json

class DialogueNode:
    """Represents a single node in a dialogue tree."""
    
    def __init__(self, node_id: str, speaker: str, text: str):
        self.node_id = node_id
        self.speaker = speaker
        self.text = text
        self.choices: list = []

    def add_choice(self, choice_text: str, next_node_id: str):
        """Add a dialogue choice leading to another node."""
        self.choices.append({
            "text": choice_text,
            "next_node_id": next_node_id
        })

    def to_dict(self) -> dict:
        """Convert node to dictionary for JSON export."""
        return {
            "node_id": self.node_id,
            "speaker": self.speaker,
            "text": self.text,
            "choices": self.choices
        }


class DialogueTree:
    """Represents a complete dialogue tree."""

    def __init__(self, title: str):
        self.title = title
        self.nodes: dict = {}
        self.start_node_id: str = None

    def add_node(self, node: DialogueNode):
        """Add a node to the tree."""
        self.nodes[node.node_id] = node

    def set_start(self, node_id: str):
        """Set the starting node of the dialogue."""
        self.start_node_id = node_id

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