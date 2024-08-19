import argparse
from pathlib import Path

from re_pygments.data.io_parser import JsonObject, ScriptObject
from re_pygments.utils.regex_engine import RegexEngine


class Controller:
    default_output_path = Path.home().joinpath('./tmp/output.json')

    def __init__(self, input_path: str, output_path: str = ''):
        json_ = JsonObject().read(input_path)

        self.id = json_.get('id', '')

        self.patterns_and = json_.get('patterns', dict())
        self.patterns_or = json_.get('pattern-either', dict())
        self.patterns_not = json_.get('pattern-not', dict())

        self.script_path = json_.get('script_path', '')
        self.language = json_.get('language', '')
        self.script = ScriptObject().read(self.script_path)

        self.raw_res = list()
        self.raw_res_not = list()
        self.location_cash = list()
        self.output_res = {
            'id': self.id,
            'result': list(),
        }
        self.output_path = output_path or self.default_output_path

    def check_regex(self):
        # TODO add checker
        # TODO check consistency of brackets
        # TODO add logic check
        return True

    @staticmethod
    def _parse_regex(regex: dict, input_expr: str, pattern: str, comparison: str, pattern_inside: str, language: str):
        regex_res, token = RegexEngine(input_expr=input_expr,
                                       re_expr_raw=regex,
                                       pattern=pattern,
                                       pattern_inside=pattern_inside,
                                       comparison=comparison,
                                       language=language).main()
        return regex_res, token

    @staticmethod
    def _extract_not_location(rule, regex_res, cache_res):
        if rule != "NOT":
            return

        for match in regex_res:
            cache_res.append(match["location"][0])

    def _fill_cache_res(self, regex_res, token):
        for match in regex_res:
            if self._check_duplicate(match):
                self.location_cash.append(match["location"])
                match["location"] = str(match["location"])
                self.raw_res.append((match, token))

    def _parse_regexes(self, patterns: list, rule: str):
        for pattern_ in patterns:
            if not self.check_regex():
                continue

            pattern = pattern_.get("pattern", '')
            pattern_inside = pattern_.get("pattern-inside", '')
            regex = pattern_.get("regex", '')
            comparison = pattern_.get("comparison", '')
            regex_res, token = self._parse_regex(regex=regex, input_expr=self.script, pattern_inside=pattern_inside,
                                                 comparison=comparison, pattern=pattern, language=self.language)
            self._extract_not_location(rule, regex_res, self.raw_res_not)

            if rule == 'AND' and not regex_res:
                self.raw_res = list()
                break
            elif regex_res:
                self._fill_cache_res(regex_res, token)

    def _parse_logic(self):
        if self.patterns_not:
            self._parse_regexes(self.patterns_not, rule='NOT')
        if self.patterns_and:
            self._parse_regexes(self.patterns_and, rule='AND')
        if self.patterns_or:
            self._parse_regexes(self.patterns_or, rule='OR')

    def _parse_result(self):
        for match_res, token in self.raw_res:
            tmp_dict = {"token": token, "search_info": match_res}
            self.output_res["result"].append(tmp_dict)

    def _check_duplicate(self, match):
        loc = match["location"]
        if (loc[0] not in self.raw_res_not) and (loc not in self.location_cash):
            return True
        return False

    @staticmethod
    def _write_json(output_path: Path, output_res: dict):
        JsonObject().write(output_path, output_res)

    def pipeline(self):
        self._parse_logic()
        self._parse_result()
        self._write_json(output_path=self.output_path, output_res=self.output_res)


def main():
    parser = argparse.ArgumentParser(description='Search engine for project')
    parser.add_argument('--indir', type=str, help='Input dir for file with rules in JSON format')
    parser.add_argument(
        '--outdir',
        type=str,
        default=Controller.default_output_path,
        help=f'Provide output dir (default: {Controller.default_output_path})')
    args = parser.parse_args()

    Controller(input_path=args.indir,
               output_path=args.outdir).pipeline()


if __name__ == "__main__":
    main()
