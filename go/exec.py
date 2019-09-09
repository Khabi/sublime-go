
from subprocess import Popen
from subprocess import PIPE
from os import (environ, path)
from . import decorators
from . import buffer
from . import log

class Command():
  """
  Command represents an external command
  with a default timeout of 5s and stdin.
  """
  def __init__(self, cmd, args=[], stdin=None, cwd=None):
    """
    Initialize a new command with timeout
    and optional stdin.
    """
    self.cmd = cmd
    self.args = args
    self.stdin = stdin
    self.cwd = cwd

  def run(self, timeout=5):
    """
    Run runs the command with args.

    If stderr is not empty, or exit code is non-zero
    a new Error is returned with the exit .code and
    stderr.

    If no error occurs, stdout is returned.
    """
    stdin = self.stdin
    args = [self.cmd] + self.args
    env = goenv(self.cwd)

    proc = Popen(
      args,
      stdin=PIPE,
      stdout=PIPE,
      stderr=PIPE,
      cwd=self.cwd,
      env=env,
    )

    stdout, stderr = proc.communicate(input=stdin, timeout=timeout)
    log.debug("$ {} {} => {}", self.cmd, ' '.join(self.args), proc.returncode)

    return Result(
      code=proc.returncode,
      stdout=stdout.decode("UTF-8"),
      stderr=stderr.decode("UTF-8"),
    )


class Result():
  def __init__(self, code, stderr, stdout):
    """
    Result represents a command's result.
    """
    self.code = code
    self.stderr = stderr
    self.stdout = stdout

@decorators.memoized
def goenv(cwd, timeout=2):
  """
  goenv returns the go environment based on cwd.
  """
  log.debug("exec: getting go env")
  proc = Popen(["go", "env"], stdout=PIPE, cwd=cwd)
  out, _ = proc.communicate(timeout=timeout)
  out = out.decode('UTF-8')
  env = {}

  for pair in out.splitlines():
    parts = pair.split('=')
    if len(parts) == 2 and parts[1] != '""':
      env[parts[0]] = parts[1][1:-1]

  env.update(environ)

  if 'GOPATH' in env and 'PATH' in env:
    paths = env['PATH'].split(':')
    if env['GOPATH'] not in paths:
      paths.append(path.join(env['GOPATH'], 'bin'))
      env['PATH'] = ':'.join(paths)

  return env
