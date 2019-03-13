__version__ = '0.1.0'


class ValidationError(Exception):
    pass


class Empty(ValidationError):
    '''
    A given value was empty.
    '''

    def __str__(self):
        return 'Empty'


class NotANumber(ValidationError):
    '''
    A given value was not a number.
    '''

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return f"'{self._value}' is not a number"


class NotInRange(ValidationError):
    '''
    A given value was not within the interval.
    '''

    def __init__(self, min, max):
        self._min = min
        self._max = max

    def __str__(self):
        return f'Please provide a value between {self._min} and {self._max}'


class NotAnOption(ValidationError):
    '''
    A given value was not an option available
    '''

    def __init__(self, options):
        self._options = options

    def __str__(self):
        return f'Please select one of {self._options}'


class Requirement(object):
    '''
    Base class for requirements.

    Values obtained from the console must meet one or many
    ```Requirements``` before being processed.

    Requirements implement ```Requirement.meet```, which may
    both test and convert values.

    In case a value does not meet a requirement, ```.meet``` should
    should raise a ```ValidationError``` which contains the
    an error message to display.
    '''

    def hint(self):
        '''
        Returns a string with a hint to use on the prompt,
        e.g.,

            (1-2) >
        '''
        return ''

    def meet(self, value):
        '''
        Tests whether ```value``` meets the requirement.
        Raises ```ValidationError``` if not.
        '''
        return value

    def __str__(self):
        '''
        Returns a string that informs the user about the requirement.
        '''
        return ''


class Chain(Requirement):

    def __init__(self, *requirements):
        self._requirements = requirements

    def hint(self):
        '''
        Returns hints for all requirements in the chain.
        '''
        return ', '.join([
            requirement.hint()
            for requirement
            in self._requirements
            if requirement.hint()
        ])

    def meet(self, value: str):
        '''
        Meets all requirements in the chain.
        '''
        for requirement in self._requirements:
            value = requirement.meet(value)
        return value

    def __str__(self):
        '''
        Returns a string with information about all requirements in the chain.
        '''
        return '\n'.join([
            requirement.__str__()
            for requirement
            in self._requirements
            if requirement.__str__()
        ])


class NotEmpty(Requirement):
    '''
    A non-empty string is expected.
    '''

    def meet(self, string):
        if not string:
            raise Empty()
        return string


class Number(Requirement):
    '''
    A number is expected.
    '''

    def meet(self, string):
        try:
            return int(string)
        except ValueError:
            raise NotANumber(string)


class Between(Requirement):
    '''
    A value within a closed interval is expected.
    '''

    def __init__(self, min, max):
        self._min = min
        self._max = max

    def hint(self):
        if self._min == self._max:
            return f'{self._min}'
        return f'{self._min} - {self._max}'

    def meet(self, value: int):
        if not self._min <= value <= self._max:
            raise NotInRange(self._min, self._max)
        return value


class Choice(Requirement):
    '''
    A one of several discrete values is expected.
    '''

    def __init__(self, options_dict):
        self._options_dict = options_dict

    def hint(self):
        return '/'.join(self._options_dict.keys())

    def meet(self, value):
        if not value in self._options_dict.keys():
            raise NotAnOption(self.hint())
        return self._options_dict[value]


class Menu(Requirement):

    def __init__(self, options):
        self._options = options

    def meet(self, value: int):
        assert 1 <= value <= len(self._options)
        return self._options[value - 1]

    def __str__(self):
        return '\n'.join([
            f'{i}. {v}' for i, v
            in enumerate(self._options, start=1)
        ])


class Exit(Exception):
    '''
    Program execution was canceled.
    '''
    pass


class Prompt(object):
    '''
    A prompt that asks for user input from the console.
    '''

    # Keywords to cancel execution
    EXIT = ('exit', 'quit')

    def __init__(self, character='> ', input_=input, print_=print):
        '''
            ```character```: The character to indicate that the user should input something. Conventionally set to '>'.
        '''
        self._character = character
        self._input = input_
        self._print = print_

    def _test_exit(self, string):
        '''
        Test whether the user asked to cancel during input
        '''
        string = string.lower()
        should_exit = any(
            command in string for command in self.EXIT
        )
        if should_exit:
            raise Exit()

    def _print_hint(self, requirement):
        '''
        Hints input expectations.
        '''
        hint = requirement.hint()
        if not hint:
            return
        self._print(f'({hint})', end=' ')

    def _print_requirement(self, requirement):
        '''
        Display
        '''
        display = str(requirement)
        if not display:
            return
        self._print(f'{display}')

    def _prompt(self, requirement):
        '''
        Asks for input until ```requirement``` is met.
        '''

        self._print_requirement(requirement)

        while True:

            self._print_hint(requirement)

            input_ = self._input(self._character)
            input_ = input_.strip()

            # In case of an exit request,
            # break as soon as possible
            self._test_exit(input_)

            try:
                return requirement.meet(input_)
            except ValidationError as e:
                # If the requirement was not met
                # print a validation error and try again
                self._print(e)

    def between(self, min, max, hint=''):
        '''
        Gets a number from the console between min and max.

        Min and max are also valid responses, i.e.:

            min <= number <= max.
        '''
        return self._prompt(
            Chain(
                Number(),
                Between(min, max)
            )
        )

    # Todo: Rename
    # Todo: Move to Args / Kwargs
    def choose(self, **options):
        '''
        Asks the user to choose from a domain.

        The keys of ```options``` are interpreted  as available options
        (the 'domain' to chose from and the values provided are
        the returned selections. For example,

            {'yes': True, 'no': False, 'maybe': False}

        expects one of 'yes', 'no', or 'maybe' and returns the equivalent
        value.
        '''
        return self._prompt(Choice(options))

    def menu(self, *options):
        return self._prompt(
            Chain(
                Number(),
                Between(1, len(options)),
                Menu(options)
            )
        )

    def name(self):
        '''
        Gets a name from the console
        '''
        return self._prompt(NotEmpty())

    def number(self, hint=''):
        '''
        Gets a number from the console
        '''
        return self._prompt(Number())
