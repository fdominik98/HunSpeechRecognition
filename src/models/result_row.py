class ResultRow():
    def __init__(self, id : int, chunk_id : int, chunk_file : str,
                  relative_timestamp : tuple[float, float], absolute_timestamp : tuple[float, float], sentence : str, 
                  sentence_pos : tuple[int, int]) -> None:
        self.id : int = int(id)
        self.chunk_id : int = int(chunk_id)
        self.chunk_file : str = chunk_file
        self.relative_timestamp : tuple[float, float]  = self.__format_timestamp(relative_timestamp)
        self.absolute_timestamp : tuple[float, float] = self.__format_timestamp(absolute_timestamp)
        self.sentence : str = sentence
        self.sentence_pos : tuple[int, int] = self.__format_position(sentence_pos)

    def to_dict(self) -> dict:
        return {'id' : self.id,
        'chunk_id' : self.chunk_id, 
        'chunk_file' : self.chunk_file,
        'relative_timestamp' : self.relative_timestamp,
        'absolute_timestamp' : self.absolute_timestamp,
        'sentence' : self.sentence,
        'sentence_pos' : self.sentence_pos}
    
    def from_dict(row : dict):
        return ResultRow(row['id'], row['chunk_id'], row['chunk_file'], row['relative_timestamp'], row['absolute_timestamp'], row['sentence'], row['sentence_pos'])
    
    def __format_timestamp(self, timestamp):
        timestamp_str = str(timestamp).strip("()")
        return tuple(map(float, timestamp_str.split(', ')))

    def __format_position(self, position):
        position_str = str(position).strip("()")
        return tuple(map(int, position_str.split(', ')))