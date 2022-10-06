from subprocess import check_call, PIPE, run
from behave import given, then, when  # pylint: disable=no-name-in-module


@given('I installed flake8-newspaper-style')
def install(_):
    check_call(['./bin/install'], stdout=PIPE, stderr=PIPE)


@given('I have a file with')
def create_file(context):
    with open('file', 'w', encoding='utf-8') as file:
        file.write(context.text)


@when('I flake8 this file')
def lint(context):
    context.result = run(
        ['flake8', '--select=NEW', 'file'], stdout=PIPE, stderr=PIPE, check=False
    )


@then('it fails with')
def expect_fail(context):
    assert context.result.returncode != 0
    text = context.result.stdout.decode('utf-8').strip()
    assert text == context.text, f'expected {context.text}, but got {text}'


@then('it succeeds')
def expect_success(context):
    assert context.result.returncode == 0
