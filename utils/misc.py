def split_str(string, lang=""):
    output = []
    if len(string) > 0:
        splitted = [string[i:i + 1994-len(lang)] for i in range(0, len(string), 1994-len(lang))]
        for i in splitted:
            output.append(f"```{lang}\n{''.join(i)}```")
    return output


def cleanup_code(content):
    'Automatically removes code blocks from the code.'
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')


def get_syntax_error(e):
    if e.text is None:
        return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
    return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)