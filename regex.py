from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        self.next_states: list[State] = []

    def check_self(self, char):
        return False


class TerminationState(State):
    def __init__(self):
        self.next_states = []

    def check_self(self, char):
        return char == ""

class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str):
        return char != ''


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.curr_sym = symbol
        self.next_states = []

    def check_self(self, curr_char: str) -> State | Exception:
        return curr_char == self.curr_sym


class StarState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)

    def check_next(self, next_char: str) -> State | Exception:
        for state in reversed(self.next_states):
            if state.check_self(next_char):
                return state
        if self.checking_state.check_self(next_char):
            return self
        raise NotImplementedError("rejected string")


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.checking_state = checking_state
        self.next_states = []

    def check_self(self, char):
        return self.checking_state.check_self(char)

    def check_next(self, next_char: str) -> State | Exception:
        for state in reversed(self.next_states):
            if state.check_self(next_char):
                return state
        if self.checking_state.check_self(next_char):
            return self
        raise NotImplementedError("rejected string")


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        nodes = [self.curr_state]

        for char in regex_expr:
            last_node = nodes[-1]
            new_state = self.__init_next_state(char, None, last_node)

            if char in ("*", "+"):
                parent = nodes[-2]
                parent.next_states.remove(last_node)
                parent.next_states.append(new_state)

                nodes[-1] = new_state
            else:
                nodes[-1].next_states.append(new_state)
                if isinstance(nodes[-1], StarState):
                    nodes[-2].next_states.append(new_state)

                nodes.append(new_state)

        nodes[-1].next_states.append(TerminationState())
        if isinstance(nodes[-1], StarState):
            nodes[-2].next_states.append(TerminationState())

    def __init_next_state(
            self, next_token: str, prev_state: State,
            tmp_next_state: State) -> State:

        new_state = None
        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self: RegexFSM, string: str) -> bool:
        current_state = self.curr_state

        for char in string:
            try:
                current_state = current_state.check_next(char)
            except NotImplementedError:
                return False

        try:
            current_state.check_next("")
            return True
        except NotImplementedError:
            return False


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("4hi"))  # False
    print(regex_compiled.check_string("meow"))  # False
