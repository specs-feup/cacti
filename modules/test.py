import os
import json


class Test:
    def __init__(self, source_path: str, output_path: str, out: str, err: str) -> None:
        self.source_path = source_path
        self.output_path = output_path
        self.results = dict()
        self.out = out
        self.err = err

    def process(self) -> None:
        _, _, after = self.out.partition('CACTI_OUTPUT_BEGIN')
        json_data, _, after = after.partition('CACTI_OUTPUT_END')

        self.results = json.loads(json_data)

        # if the parsing failed, modify the json object to contain information about the error
        if not self.results['test_parsing']['success']:
            self.results['test_parsing']['success'] = self.err

        # if the code generation failed, modify the json object to contain information about the error
        elif not self.results['test_code_generation']['success']:
            self.results['test_code_generation']['log'] = self.err

    def contains(self, test_kind: str) -> bool:
        return test_kind in self.results.keys()

    def success(self, test_kind: str) -> bool:
        return self.contains(test_kind) and self.results[test_kind]['success']

    def save(self) -> None:
        results_path = os.path.join(self.output_path, 'results.json')

        with open(results_path, 'w+') as f:
            json.dump(self.results, f)
