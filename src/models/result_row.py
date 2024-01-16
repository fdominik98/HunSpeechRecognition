class ResultRow():
    def __init__(self, chunk_id : int, chunk_file : str,
                  relative_timestamp : tuple[float, float], absolute_timestamp : tuple[float, float], sentence : str) -> None:
        self.chunk_id : int = int(chunk_id)
        self.chunk_file : str = chunk_file
        self.relative_timestamp : tuple[float, float]  = self.__format_timestamp(str(relative_timestamp))
        self.absolute_timestamp : tuple[float, float] = self.__format_timestamp(str(absolute_timestamp))
        self.sentence : str = sentence

    def to_dict(self) -> dict:
        return {'chunk_id' : self.chunk_id, 
        'chunk_file' : self.chunk_file,
        'relative_timestamp' : self.relative_timestamp,
        'absolute_timestamp' : self.absolute_timestamp,

        'sentence' : self.sentence}
    def from_dict(row : dict):
        return ResultRow(row['chunk_id'], row['chunk_file'], row['relative_timestamp'], row['absolute_timestamp'], row['sentence'],)
    
    def __format_timestamp(self, timestamp : str):
        timestamp_str = timestamp.strip("()")
        return tuple(map(float, timestamp_str.split(', ')))