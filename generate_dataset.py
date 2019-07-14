import os
import sys
import graph
import generate_instance


def generate_dataset(output_dir):
    for iteration in range(1, 11, 1):
        n1, n2, k, cap = 2000, 20, 5, 10
        file_path = os.path.join(output_dir, '{}_{}_{}_{}_{}.txt'.format(n1, n2, k, cap, iteration))
        G = generate_instance.mahadian_model_generator(n1, n2, k, cap)
        with open(os.path.join(output_dir, file_path), encoding='utf-8', mode='w') as out:
            out.write(graph.graph_to_UTF8_string(G))


def main():
    if len(sys.argv) < 2:
        print('usage: {} <output-dir>'. format(sys.argv[0]))
    else:
        output_dir = sys.argv[1]
        generate_dataset(output_dir)


if __name__ == '__main__':
    main()
