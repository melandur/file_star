import re


def tokenize_filter_string(text):
    """Tokenize a string into a filter string"""

    if isinstance(text, type(None)) or all(char.isspace() for char in text):
        return None

    text = re.sub(r'^[&|]+|[&|]+$', '', text)  # remove special characters at the beginning and end of the string
    text = text.strip()  # remove empty spaces at the beginning and end of the string

    text = re.sub(r'\s*&\s*', '&', text)  # remove empty spaces around the & symbol
    text = re.sub(r'\s*\|\s*', '|', text)  # remove empty spaces around the | symbol
    text = re.sub(r'\s*~\s*', '~', text)  # remove empty spaces around the ~ symbol
    text = re.sub(r'\s*\[\s*', '[', text)  # remove empty spaces around the [ symbol
    text = re.sub(r'\s*\]\s*', ']', text)  # remove empty spaces around the ] symbol
    text = re.sub(r'([&|~])\1+', r'\1', text)  # remove multiple consecutive special characters

    if bool(re.search(r'[&|][&|]', text)):  # & and | can not be neighbors
        return None

    if text.count('[') != text.count(']'):  # [ and ] must be in pairs
        return None

    if '~' in text:
        if not bool(re.search(r'(^~)|[&|]~', text)):  # ~ at start and after & or |
            return ''

    if '&' in text or '|' in text or '[' in text or ']' in text:  # split the string into tokens
        tokens = re.findall(r'(&|\||\[|\]|[^&\|\[\]]+)', text)
    else:
        tokens = [text]

    return tokens


def create_filter_logic(tokens, search_type):
    """Create a filter string from a list of tokens"""

    if tokens is None:
        return None

    result = ''
    for token in tokens:  # create a filter string from the tokens
        if token == '[':
            result += ' ('
        elif token == ']':
            result += ' )'
        elif token in ('&', '|'):
            result += f' {token}'
        elif '~' in token:
            result += f' ~{search_type}("{token[1:]}")'
        else:
            result += f' {search_type}("{token}")'

    if result != '':
        result = f'({result.lstrip()})'
    return result


def create_search_statements(searches: dict):
    """Create a filter statement from a list of filters"""

    store = {}
    for search_name in searches:
        store[search_name] = []
        for tag, search_class in zip(
            ['file_name', 'extension_name', 'folder_name'], ['FileName', 'Extension', 'FolderNames']
        ):
            search_tag = searches[search_name][tag]
            search_tokens = tokenize_filter_string(search_tag)
            search_filter = create_filter_logic(search_tokens, search_class)
            if search_filter is not None:
                store[search_name].append(search_filter)

        if store[search_name]:
            store[search_name] = ' & '.join(store[search_name])
        else:
            return None
    if store:
        return store
    return None
