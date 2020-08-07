class JPathError(Exception):
    SPACE = " "

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.SPACE.join(self.args))


class JPathLexerError(JPathError):
    pass


class JPathParseError(JPathError):
    pass


class JPathNodeError(JPathError):
    TYPE = "Invalid Path"

    def __init__(self, path, data):
        self._message = "{0}: {1} {2} for {3}".format(
            self.__class__.__name__, self.TYPE, path, data
        )

    def __str__(self):
        return self._message


class JPathIndexError(JPathNodeError):
    TYPE = "Invalid Index"
