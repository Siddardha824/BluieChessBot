class UCIParser:
    """
    Pure functional parser to translate Universal Chess Interface (UCI) string
    responses into structured Python dictionaries.
    Has no external dependencies, making it simple to unit test.
    """
    @staticmethod
    def parse_line(line: str) -> dict | None:
        """
        Parses a single line of output from a UCI Chess Engine.
        Returns a structured dictionary representing the message, or None.
        """
        if not line:
            return None
            
        tokens = line.strip().split()
        if not tokens:
            return None

        command = tokens[0]
        
        if command == "info":
            return UCIParser._parse_info(tokens)
        elif command == "bestmove":
            return UCIParser._parse_bestmove(tokens)
        
        return {"type": command, "raw": line}

    @staticmethod
    def _parse_info(tokens: list[str]) -> dict:
        info_dict = {"type": "info"}
        i = 1
        while i < len(tokens):
            key = tokens[i]
            if key in ["depth", "seldepth", "nodes", "nps", "hashfull", "time"]:
                if i + 1 < len(tokens):
                    info_dict[key] = tokens[i+1]
                    i += 2
                else:
                    i += 1
            elif key == "score":
                # Format: "score cp 34" or "score mate -3"
                if i + 2 < len(tokens):
                    info_dict["score_type"] = tokens[i+1] # "cp" or "mate"
                    info_dict["score_val"] = tokens[i+2]
                    i += 3
                else:
                    i += 1
            elif key == "pv":
                info_dict["pv"] = " ".join(tokens[i+1:])
                break  # The PV sequence occupies all remaining elements in the line
            else:
                i += 1
        return info_dict

    @staticmethod
    def _parse_bestmove(tokens: list[str]) -> dict:
        bestmove_dict = {"type": "bestmove", "bestmove": None, "ponder": None}
        if len(tokens) > 1:
            bestmove_dict["bestmove"] = tokens[1]
        if len(tokens) > 3 and tokens[2] == "ponder":
            bestmove_dict["ponder"] = tokens[3]
        return bestmove_dict
