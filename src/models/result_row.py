class ResultRow():
    def __init__(self, id: int, chunk_id: int, chunk_file: str,
                 relative_timestamp: tuple[int, int], absolute_timestamp: tuple[int, int], sentence: str) -> None:
        self.id: int = int(id)
        self.chunk_id: int = int(chunk_id)
        self.chunk_file: str = chunk_file
        self.relative_timestamp: tuple[int, int] = self.__format_timestamp(
            relative_timestamp)
        self.absolute_timestamp: tuple[int, int] = self.__format_timestamp(
            absolute_timestamp)
        self.sentence: str = sentence
        self.length : int = self.relative_timestamp[1] - self.relative_timestamp[0]

    def to_dict(self) -> dict:
        return {'id': self.id,
                'chunk_id': self.chunk_id,
                'chunk_file': self.chunk_file,
                'relative_timestamp': self.relative_timestamp,
                'absolute_timestamp': self.absolute_timestamp,
                'sentence': self.sentence}

    @staticmethod
    def from_dict(row: dict):
        return ResultRow(row['id'], row['chunk_id'], row['chunk_file'], row['relative_timestamp'], row['absolute_timestamp'], row['sentence'])

    def __format_timestamp(self, timestamp) -> tuple[int, int]:
        timestamp_str = str(timestamp).strip("()")
        return tuple(map(int, timestamp_str.split(', ')))
