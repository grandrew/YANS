import subprocess

yapf = "yapf", "-dr", "--style={based_on_style: chromium, indent_width: 4}", "."
try:
    assert not subprocess.call(yapf)
except AssertionError:
    print "Failed code style check"
    assert False
