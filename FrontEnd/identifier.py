class  IdGen:
    def __init__(self):
        self._names = set()
        self._labels = set()

    def NewCommon(self, prefix, seen) -> str:
        token = prefix.split("$")
        assert len(token) <= 2
        prefix = token[0]
        name = prefix
        if name not in seen:
            seen.add(name)
            return name
        for i in range(1, 100):
            name = f"{prefix}${i}"
            if name not in seen:
                seen.add(name)
                return name
        assert False

    def NewName(self, prefix) -> str:
        return self.NewCommon(prefix, self._names)

    def NewLabel(self, prefix) -> str:
        return self.NewCommon(prefix, self._labels)