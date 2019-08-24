
import go.exec as exec

def test_goenv():
  exec.environ = { 'PATH': '/usr/local/bin' }
  v = exec.goenv('/')
  assert v.get('PATH') == ':'.join([
    '/usr/local/bin',
    v.get('GOPATH'),
  ])