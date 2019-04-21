# -*- coding: utf-8 -*-

class InputTracker:
    def __init__(self):
        self.state = ""
        self.last_input = "NOTHING"
        self.last_timestamp = 0
    
    def update(self, input, timestamp):
        if input != "":
            if input != self.last_input:
                self.last_input = input
                self.last_timestamp = timestamp
            
            timediff = timestamp - self.last_timestamp
            # print(str(timediff) + " " + self.state + " " + input)
            
            if input == "ROCK" and self.state != "NOACTION":
                self.state = "NOACTION"
            
            if timediff > 0.1:
                if input == "PAPER" and self.state == "NOACTION":
                    self.state = "ACTION"
                    return "MOVE"
                elif input == "SCISSOR" and self.state == "NOACTION":
                    self.state = "ACTION"
                    return "FLIP"
                elif input == "NOTHING" and self.state == "NOACTION":
                    self.state = "ACTION"
                    return "DOWN"
        return ""