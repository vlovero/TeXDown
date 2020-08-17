import re
import os
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm


PATTERN_INLINE = r'<tex (?:.*?)>'
PATTERN_INLINE_RAW = r'<ignore-tex (?:.*?)>'
PATTERN_BLOCK = re.compile(r'```latex(.*?)\n((.*?)+)\n```', re.DOTALL)
PATTERN_DISPLAY = re.compile(r'\$\$(.*?)\n((.*?)+)\n\$\$', re.DOTALL)

TEMPLATE_INLINE = r'<img src="{}" height="25">'
TEMPLATE_BLOCK = r'''<p align="center">
  <img src="{}"
       {}>
</p>'''
TEMPLATE_DISPLAY = r'''<p align="center">
  <img src="{}"
       {}>
</p>'''

SHORTEN_SYMBOLS = ['langle', 'rangle', '_']


matplotlib.rc('text', usetex=True)
matplotlib.rcParams['text.latex.preamble'] = r"\usepackage{amsmath}"
depth = 0


def get_frac_matches(string):
    ptrn = r'\\frac\{(?:{[^{}]*}|[^{}])*}\{(?:{[^{}]*}|[^{}])*}'
    return re.findall(ptrn, string)


def clean_and_count(string, matches):
    _s = string
    for match in matches:
        _s = _s.replace(match)
    return len(_s) - list(_s).count('\\')


def count_frac(string, count=0):
    global depth
    depth += 1
    matches = get_frac_matches(string)

    if not matches:
        return len(string)
    if len(matches) == 1:
        i = string.rfind('}{')
        s = [string[:i], string[i + 2:]]
        s[0], s[1] = s[0][6:], s[1][:-1]

        mml = get_frac_matches(s[0])
        mmr = get_frac_matches(s[1])

        lc = sum(count_frac(m, count) for m in mml) if mml else len(s[0])
        rc = sum(count_frac(m, count) for m in mmr) if mmr else len(s[1])

        if mml:
            count += clean_and_count(s[0], mml)
        if mmr:
            count += clean_and_count(s[1], mmr)

        count += max(lc, rc)
    else:
        _s = string
        for match in matches:
            _s = _s.replace(match, '')
            count += count_frac(match)
        count += len(_s) - list(_s).count('\\')

    return count


def get_inline_size(lines):
    global depth
    string = r''.join(lines)
    w_factor, h_factor = 0.05, 0.2
    width, height = len(max(lines, key=lambda x: len(x))), len(lines)
    if 'frac' in string:
        depth = 0
        width = count_frac(string)
        for m in get_frac_matches(string):
            string = string.replace(m, '')

        width += len(string) - list(string).count('\\') - 2
        height += h_factor

    for symbol in SHORTEN_SYMBOLS:
        if symbol in string:
            width += -len(symbol) if len(symbol) > 1 else -1

    width -= 0.5
    width *= w_factor
    height *= h_factor

    return width, height


def str2TeX(tex_string, out, mode='block', _show=False):
    lines = [line.strip() for line in tex_string.split('\n')]

    if mode == 'block':
        _figsize = 3, 2
        string = r'\[' + r''.join(lines) + r'\]'
    elif mode == 'display':
        _figsize = [*get_inline_size(lines)]
        _figsize[0] *= 1.5
        _figsize[1] *= 1.5
        string = r''.join(tex_string.split('\n'))
    elif mode == 'inline':
        _figsize = get_inline_size(lines)
        string = tex_string
    else:
        raise RuntimeError

    plt_kwargs = dict(dpi=500) if not _show else {}
    fig, ax = plt.subplots(figsize=_figsize, **plt_kwargs)
    plt.axis('off')

    ax.text(0.5, 0.5, string,
            horizontalalignment='center', verticalalignment='center')

    if _show:
        plt.show()
    else:
        plt.savefig(out)


def run(fname, output_fname, verbose=1, o_dir='tmp', extra_symbols=[]):
    global SHORTEN_SYMBOLS
    SHORTEN_SYMBOLS.extend(extra_symbols)
    
    ftag = os.path.splitext(os.path.basename(output_fname))[0]
    with open(fname) as f:
        text = r'{}'.format(f.read())

    inline_matches = re.findall(PATTERN_INLINE, text)
    inlineR_matches = re.findall(PATTERN_INLINE_RAW, text)
    block_matches = re.findall(PATTERN_BLOCK, text)
    display_matches = re.findall(PATTERN_DISPLAY, text)

    total = len(inline_matches) + len(block_matches) + len(display_matches)
    if verbose:
        pbar = tqdm(total=total, ncols=50)

    for i, match in enumerate(inline_matches):
        src = r'${}$'.format(re.findall(r'src="(.*?)"', match)[0])
        img_path = os.path.join(o_dir, '{}-img-inline{}.png'.format(ftag, i))
        text = text.replace(match, TEMPLATE_INLINE.format(img_path, ''), 1)
        str2TeX(src, out=img_path, mode='inline')
        if verbose:
            pbar.update(1)

    for i, match in enumerate(block_matches):
        opt, src, _ = match

        if 'ignore' in opt:
            text = text.replace('```latex{}\n'.format(opt) + '\n'.join(match[1:]) + '```',
                                '```latex{}\n'.format(opt.replace('ignore', '')) + '\n'.join(match[1:]) + '```')
            if verbose:
                pbar.update(1)
            continue

        img_path = os.path.join(o_dir, '{}-img-block{}.png'.format(ftag, i))
        text = text.replace('```latex{}\n'.format(opt) + '\n'.join(match[1:]) + '```',
                            TEMPLATE_BLOCK.format(img_path, opt if opt else 'height="250"'),
                            1)
        str2TeX(src, out=img_path, mode='block')
        if verbose:
            pbar.update(1)

    for i, match in enumerate(display_matches):
        opt, src, _ = match

        if 'ignore' in opt:
            text = text.replace('$${}\n'.format(opt) + '\n'.join(match[1:]) + '$$',
                                '$${}\n'.format(opt.replace('ignore', '')) + '\n'.join(match[1:]) + '$$')
            if verbose:
                pbar.update(1)
            continue

        img_path = os.path.join(o_dir, '{}-img-display{}.png'.format(ftag, i))
        text = text.replace('$${}\n'.format(opt) + '\n'.join(match[1:]) + '$$',
                            TEMPLATE_DISPLAY.format(img_path,
                                                    opt if opt.strip() else 'height="36"'),
                            1)
        str2TeX('$${}$$'.format(src), out=img_path, mode='display')
        if verbose:
            pbar.update(1)

    for raw_inline in inlineR_matches:
        text = text.replace(raw_inline, raw_inline.replace('ignore-', ''), 1)

    with open(output_fname, 'w') as f:
        f.write(text)
