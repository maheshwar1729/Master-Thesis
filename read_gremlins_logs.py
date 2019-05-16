import os
import json
import numpy as np
from chomsky import chomsky


class Ind:
    event = None
    input = None
    locx = None
    locy = None
    duration = None
    distancex = None
    distancey = None
    scale = None
    rotation = None
    radius = None
    dom = None

    def __init__(self, _e, _i=None, _lx=None, _ly=None, _du=None, _dx=None, _dy=None,
                 _scale=None, _rotation=None, _radius=None,
                 _dom=None):
        self.event = _e
        self.input = _i
        self.locx = _lx
        self.locy = _ly
        self.duration = _du
        self.distancex = _dx
        self.distancey = _dy
        self.scale = _scale
        self.rotation = _rotation
        self.radius = _radius
        self.dom = _dom

    def __str__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
            self.event, self.input, self.locx, self.locy,
            self.duration, self.distancex, self.distancey,
            self.scale, self.rotation, self.radius,
            self.dom
        )

    def fuzzy_location(self):
        if self.locx is not None and self.locx < 500:
            self.locx += np.random.randint(0, 100)
        elif self.locx is not None:
            self.locx -= np.random.randint(0, 100)
        else:
            self.locx = np.random.randint(0, 500)

        if self.locy is not None and self.locy < 500:
            self.locy += np.random.randint(0, 100)
        elif self.locy is not None:
            self.locy -= np.random.randint(0, 100)
        else:
            self.locy = np.random.randint(0, 500)

    def fuzzy_input(self):
        self.input = chomsky(np.random.randint(3, 20))
        self.dom = "input"

    def fuzzy(self):
        if self.event == "type" or self.event == "input":
            self.fuzzy_input()
        else:
            self.fuzzy_location()

    def normalize_dimensions(self, max_width, max_height):
        if self.locx is not None and int(self.locx) >= max_width:
            self.locx = max_width - 50
        if self.locy is not None and int(self.locy) >= max_height:
            self.locy = max_height - 50


def parse_line(l):
    parts = l.split()

    e = parts[1]
    o = None
    if e == "type":
        o = Ind(_e=e, _i=chomsky(np.random.randint(3, 5)), _dom='input')
    elif e == "click" or e == "scroll" \
            or e == "mousedown" or e == "mouseout" \
            or e == "mouseover" or e == "dblclick" \
            or e == "mousemove" or e == "mouseup":
        o = Ind(_e=e, _lx=parts[3], _ly=parts[4])
    elif e == "gesture":
        params = json.loads(parts[5])
        o = Ind(_e=e, _lx=parts[3], _ly=parts[4],
                _dx=params['distanceX'],
                _dy=params['distanceY'],
                _du=params['duration'])
    elif e == "tap" or e == "doubletap":
        params = json.loads(parts[5])

        o = Ind(_e=e, _lx=parts[3], _ly=parts[4],
                _du=params['duration'])
    elif e == "multitouch":
        params = json.loads(parts[5])

        o = Ind(_e=e, _lx=parts[3], _ly=parts[4],
                _dx=params['distanceX'],
                _dy=params['distanceY'],
                _du=params['duration'],
                _scale=params['scale'],
                _rotation=params['rotation'],
                _radius=params['radius']
                )
    elif e == "input":
        o = Ind(_e=e, _i=chomsky(np.random.randint(3, 7)), _dom='input')

    return o

# {
# 'multitouch',
# 'input',
# 'mousemove', 'mouseup',
# 'type', 'doubletap',
# 'mousedown', 'tap', 'click',
# 'mouseout', 'gesture', 'dblclick',
# 'scroll', 'mouseover'
# }
def read_log(path):
    if not os.path.exists(path):
        return None

    events = set()
    atomic_sequences = []

    with open(path, "r") as f:
        lines = f.readlines()
        for l in lines:
            if l.find("VM26 gremlinsClient.js:") == -1:
                continue
            parts = l.split()
            if parts[2] == "gremlin":
                # print(parts[5:])
                events.add(parts[4])
                e = parts[4]
                o = None
                if e == "type":
                    o = Ind(_e=e, _i=parts[5], _lx=parts[7], _ly=parts[8])
                elif e == "click" or e == "scroll"\
                        or e == "mousedown" or e == "mouseout"\
                        or e == "mouseover" or e == "dblclick"\
                        or e == "mousemove" or e == "mouseup":
                    o = Ind(_e=e, _lx=parts[6], _ly=parts[7])
                elif e == "gesture":
                    o = Ind(_e=e, _lx=parts[6], _ly=parts[7], _dx=int(parts[9].replace(",", "")),
                            _dy=int(parts[11].replace(",", "")),
                            _du=int(parts[13].replace("}", "")))
                elif e == "tap" or e == "doubletap":
                    o = Ind(_e=e, _lx=parts[6], _ly=parts[7], _du=int(parts[9].replace("}", "")))
                elif e == "multitouch":
                    o = Ind(_e=e, _lx=parts[6], _ly=parts[7], _dx=int(parts[15].replace(",", "")),
                            _dy=int(parts[17].replace(",", "")),
                            _scale=float(parts[9].replace(",", "")),
                            _rotation=int(parts[11].replace(",", "")),
                            _radius=int(parts[13].replace(",", ""))
                            )
                elif e == "input":
                    o = Ind(_e=e, _i=parts[5], _dom=''.join(str(e) for e in parts[7:]))

                if o is not None:
                    print(o)
                    atomic_sequences.append(o)





