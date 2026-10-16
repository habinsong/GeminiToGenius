"""별도 프로세스에서 unittest를 실행하고 실제 성공한 시험 ID를 반환합니다."""

import contextlib
import json
import os
import sys
import unittest


class ObservedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successful_tests = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successful_tests.append(test.id())


def observe(request):
    sys.path.insert(0, request["workspace"])
    try:
        with contextlib.redirect_stdout(sys.stderr):
            suite = unittest.TestLoader().discover(request["start_directory"], pattern=request["pattern"])
            result = unittest.TextTestRunner(stream=sys.stderr, resultclass=ObservedResult).run(suite)
        report = {"kind": "unittest_observation", "tests_run": result.testsRun,
                  "successful_tests": result.successful_tests, "successful": result.wasSuccessful(),
                  "skipped": [test.id() for test, _ in result.skipped],
                  "failures": len(result.failures), "errors": len(result.errors)}
    except (Exception, SystemExit) as error:
        report = {"kind": "unittest_observation", "error": type(error).__name__}
    return report


def main():
    request = json.load(sys.stdin)
    # 하위 프로세스의 원시 stdout도 로그로 보내고 결과 채널은 별도로 보존합니다.
    with os.fdopen(os.dup(sys.stdout.fileno()), "w", encoding="utf-8") as output:
        os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
        print(json.dumps(observe(request), ensure_ascii=False), file=output)


if __name__ == "__main__":
    main()
