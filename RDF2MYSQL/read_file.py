def readFile(path, split = "}", token = None):
    try:
        replacement = ""
        with open(path, "r") as f:
            for line in f:
                changes = ""
                if not (token and token in line and line[0] == token):
                    changes = line.strip().replace("\n", "").replace("\t","")
                replacement = replacement + changes
            f.close()
        return [x + "}" for x in replacement.split(split)[:len(replacement.split(split))-1]]
    except Exception as error: return error
