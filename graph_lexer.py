import ply.lex as lex


# the reserved keywords in the graph file format
reserved = {
    '@End': 'END',
    '@PartitionA': 'PARTITION_A',
    '@PartitionB': 'PARTITION_B',
    '@PreferenceListsA': 'PREFERENCE_LISTS_A',
    '@PreferenceListsB': 'PREFERENCE_LISTS_B'
}

tokens = ['INT', 'ID'] + list(reserved.values())

# colon, comma and semicolon
literals = ':,;()'


def t_INT(t):
    r'[0-9]+'
    t.type = 'INT'
    t.value = int(t.value)
    return t


# identifiers
def t_ID(t):
    r'[@a-zA-Z0-9][a-zA-Z0-9+]*'
    t.type = reserved.get(t.value, 'ID')  # check for reserved words
    return t


# handle newline
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# ignore spaces and tabs
t_ignore = ' \t\r'

t_ignore_COMMENT = r'\#.*'


# Error handling rule
def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

# build the lexer
lexer = lex.lex(debug=0)


def main():
    import sys
    if len(sys.argv) < 2:
        print('usage: {} <graph file path>'.format(sys.argv[0]), file=sys.stderr)
    else:
        file_path = sys.argv[1]
        with open(file_path, encoding='utf-8', mode='r') as fin:
            lexer.input(fin.read())
            for token in lexer:
                print(token)

if __name__ == '__main__':
    main()
