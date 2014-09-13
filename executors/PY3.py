from .resource_proxy import ResourceProxy
from ptbox import sandbox
from ptbox.chroot import CHROOTProcessDebugger

PYTHON_FS = ["\xb8", "\xff", "/dev/urandom", "/bin/python", ".*\.[so|py]", ".*/lib(?:32|64)?/python[\d.]+/.*",
             ".*/lib/locale/.*"]


class Executor(ResourceProxy):
    def __init__(self, env, problem_id, source_code):
        super(ResourceProxy, self).__init__()
        self.env = env
        source_code_file = str(problem_id) + ".py"
        customize = '''__import__("sys").stdout = __import__("os").fdopen(1, 'w', 65536)
    __import__("sys").stdin = __import__("os").fdopen(0, 'r', 65536)
    '''
        with open(source_code_file, "wb") as fo:
            fo.write(customize)
            fo.write(source_code)
        self._files = [source_code_file]

    def launch(self, *args, **kwargs):
        return sandbox.execute([self.env["python3"], "-B", self._files[0]] + list(args),
                               debugger=CHROOTProcessDebugger(
                                   filesystem=PYTHON_FS + [str(self.env['python3dir']) + '.*']),
                               time=kwargs.get("time"),
                               memory=kwargs.get("memory"))