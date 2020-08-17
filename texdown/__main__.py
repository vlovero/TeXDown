import os
from argparse import ArgumentParser
from .string2texImg import run


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('source', help='Input file')
    parser.add_argument('-o', '--out', default=None, help='Outout file')
    parser.add_argument('-i', '--image-dir', default='tmp',
                        help='Outout directory for LaTeX images')
    parser.add_argument('-q', '--quiet', default=False,
                        action='store_true', help='Turn off verbose')
    parser.add_argument('-s', '--add-symbols', default=[], nargs='+',
                        help='add more recognizable symbols for inline formatting.')
    args = parser.parse_args()

    if not os.path.isdir(args.image_dir):
        try:
            os.mkdir(args.image_dir)
        except OSError as e:
            raise IOError(
                "'{}' is not a valid directory.".format(os.path.abspath(args.image_dir))
            ) from e

    if args.out is None:
        name, ext = os.path.splitext(args.source)
        args.out = name + '-out' + ext

    run(args.source, args.out,
        verbose=not args.quiet,
        o_dir=args.image_dir,
        extra_symbols=args.add_symbols)
