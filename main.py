import time


def main():
    with open('text.txt', 'a', encoding='utf-8') as f:
        f.write('Hello world!\n')


if __name__ == '__main__':
    time.sleep(6 * 60)
    main()
