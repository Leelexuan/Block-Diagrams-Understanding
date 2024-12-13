from grapher import Grapher
from lib import verify_entity_code, verify_label
import time


def _graph(entity_code):
    try:
        start = time.time()
        graph = Grapher(entity_code)
        graph.randomize_graph()
        graph.export()
        end = time.time()
        print(f"Graph exported successfully! Time taken: {end - start:.2f} seconds")
    except Exception as e:
        print(f"Error generating graph: {e}")


def main():
    while True:
        print("Input a label or entity code (type 'exit' to quit):")
        input_value = input().strip()

        if input_value.lower() in ["exit", "exit()", "quit", "q"]:
            print("Exiting program. Goodbye!")
            break

        # Check if input is a valid label or entity code
        entity_code = verify_label(input_value) or (
            verify_entity_code(input_value) and input_value
        )

        if entity_code:
            print(f"Processing input: {input_value}")
            _graph(entity_code)
        else:
            print(
                f"Could not find a valid label or entity code for: {input_value}. Please try again."
            )


if __name__ == "__main__":
    main()
