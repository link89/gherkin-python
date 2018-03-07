from __future__ import print_function, unicode_literals

from .parser import Parser
from .ast_builder import AstBuilder
from .token_matcher import MyTokenMatcher
import codecs


# TODO: write comments, docstring, data table
class GherkinWriter(object):
    def __init__(self, ast, indent=2):
        self._ast = ast
        self._indent = indent

    def dump_to_path(self, path):
        with codecs.open(path, 'w', encoding='utf8') as f:
            self.dump(f)

    def dump(self, fp):
        # type: (BinaryIO) -> None
        self.write_feature(fp, self._ast['feature'])

    def write_feature(self, f, feature, level=0):
        # type: (BinaryIO, dict, int) -> None
        self.may_write_comment(f, feature, level)
        tags = feature.get('tags')
        if tags:
            self.write_tags(f, tags, level)

        line = "{keyword}: {name}".format(**feature)
        self.write_line_with_indent(f, line, level)

        description = feature.get('description')
        if description:
            self.write_line(f, description)
        f.writelines('\n')

        for scenario in feature.get('children', []):
            self.write_scenario(f, scenario, level+1)

    def write_tags(self, f, tags, level):
        # type: (BinaryIO, List[dict], int) -> None
        line = ' '.join(tag['name'] for tag in tags)
        self.write_line_with_indent(f, line, level)

    def write_scenario(self, f, scenario, level):
        # type: (BinaryIO, dict, int) -> None
        self.may_write_comment(f, scenario, level)
        tags = scenario.get('tags')
        if tags:
            self.write_tags(f, tags, level)

        line = "{keyword}: {name}".format(**scenario)
        self.write_line_with_indent(f, line, level)

        description = scenario.get('description')
        if description:
            self.write_line(f, description)

        for step in scenario.get('steps', []):
            self.write_step(f, step, level+1)
        f.writelines('\n')

        for example in scenario.get('examples', []):
            self.write_example(f, example, level)
            f.writelines('\n')

    def write_step(self, f, step, level):
        # type: (BinaryIO, dict, int) -> None
        line = "{keyword}{text}".format(**step)
        self.write_line_with_indent(f, line, level)

    def write_example(self, f, example, level):
        # type: (BinaryIO, dict, int) -> None
        tags = example.get('tags')
        if tags:
            self.write_tags(f, tags, level)

        line = "{keyword}: {name}".format(**example)
        self.write_line_with_indent(f, line, level)

        description = example.get('description')
        if description:
            self.write_line(f, description)

        header = example.get('tableHeader')
        if header:
            rows = example.get('tableBody', [])
            self.write_table(f, header, rows, level+1)

    def write_table(self, f, header, rows, level):
        def format_row(row):
            return [format_cell(cell['value']) for cell in row['cells']]

        table = [format_row(header)]
        table.extend(format_row(row) for row in rows)
        padding = column_max_len(table)

        def build_line(row):
            return "|{}|".format('|'.join(cell.ljust(padding[i] or 0) for i, cell in enumerate(row)))

        for row in table:
            line = build_line(row)
            self.write_line_with_indent(f, line, level)

    def may_write_comment(self, f, ast_object, level):
        comment = ast_object.get('comment')
        if comment is not None:
            self.write_line_with_indent(f, comment, level)

    @staticmethod
    def write_line(f, line):
        f.writelines(line + '\n')

    def write_line_with_indent(self, f, line, level):
        self.write_line(f, self.padding(line, level))

    def padding(self, content, level):
        return ' ' * (level * self._indent) + content.lstrip()


def format_cell(cell):
    return cell\
        .replace('\\', '\\\\')\
        .replace('\n', '\\n')\
        .replace('|', '\\|')  # order care!!!


def column_max_len(table):
    size = lambda x: len(unicode(x))
    # x is the accumulated value
    return reduce(lambda x, y: map(lambda a, b: max(a, b), x, map(size, y)), table, map(size, table[0]))


def parse_gherkin(path):
    return Parser(AstBuilder()).parse(path, MyTokenMatcher())


def write_gherkin(ast, fp_or_path, ident=2):
    writer = GherkinWriter(ast, ident)
    if isinstance(fp_or_path, basestring):
        writer.dump_to_path(fp_or_path)
    else:
        writer.dump(fp_or_path)
