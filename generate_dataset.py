import os
import sys
import subprocess

PYCODE_DIR='/home/amitrawt/Dropbox/projects/matching'


def generate_dataset(output_dir):
    for iteration in range(1, 11, 1):
        n1, n2, k, cap = 100, 10, 5, 10
        file_path = os.path.join(output_dir, '{}_{}_{}_{}_{}.txt'.format(n1, n2, k, cap, iteration))
        subprocess.run(['python3', os.path.join(PYCODE_DIR, 'generate_instance.py'),
                        str(n1), str(n2), str(k), str(cap), file_path], check=True)


def main():
    if len(sys.argv) < 2:
        print('usage: {} <output-dir>'. format(sys.argv[0]))
    else:
        output_dir = sys.argv[1]
        generate_dataset(output_dir)

if __name__ == '__main__':
    main()
