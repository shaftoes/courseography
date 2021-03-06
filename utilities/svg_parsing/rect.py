AREAS = {
    'theory': ['CSC165', 'CSC236', 'CSC240', 'CSC263', 'CSC265',
               'CSC310', 'CSC324', 'CSC373', 'CSC438', 'CSC448',
               'CSC463'],
    'core': ['CSC108', 'CSC148', 'CSC104', 'CSC120', 'CSC490',
             'CSC491', 'CSC494', 'CSC495'],
    'se': ['CSC207', 'CSC301', 'CSC302', 'CSC410', 'CSC465'],
    'systems': ['CSC209', 'CSC258', 'CSC358', 'CSC369', 'CSC372',
                'CSC458', 'CSC469', 'CSC488', 'ECE385', 'ECE489'],
    'hci': ['CSC200', 'CSC300',  'CSC318', 'CSC404', 'CSC428',
            'CSC454'],
    'graphics': ['CSC320', 'CSC418', 'CSC420'],
    'num': ['CSC336', 'CSC436', 'CSC446', 'CSC456'],
    'ai': ['CSC321', 'CSC384', 'CSC401', 'CSC411', 'CSC412',
           'CSC485', 'CSC486'],
    'dbweb': ['CSC309', 'CSC343', 'CSC443']
}

hybrid_id_counter = 0

class Rect:

    def __init__(self, width, height, x, y, transform, hybrid):
        self.width = width
        self.height = height
        self.x = float(x) + float(transform[transform.find('(') + 1: transform.find(',')])
        self.y = float(y) + float(transform[transform.find(',') + 1: transform.find(')')])
        self.text_x = float(self.x) + (float(width)/2)
        self.text_y = float(self.y) + (float(height)/2)
        self.parent_transform_x = float(transform[transform.find('(') + 1: transform.find(',')])
        self.parent_transform_y = float(transform[transform.find(',') + 1: transform.find(')')])
        self.text = {} # This is a dictionary whose keys are y coordinates and values are strings.
                       # (text element text).
                       # Some hybrids require two lines of text, and SVG text elements do not
                       # wrap around, nor do they respect the newline character.
                       # The y value of the first text value seen by the parser.
                       # When a second text value for a node is seen, we want
                       # to be able to identify which text element goes above,
                       # and which goes below.
        self.hybrid = hybrid
        self.colour = '#fff'
        self.class_ = 'hybrid' if self.hybrid else 'node'

    def output_haskell(self):
        global hybrid_id_counter
        
        if self.hybrid:
            self.colour = '#bbb'
        prefix = ''
        sorted_text = sorted(self.text.items()) 

        if self.hybrid:
            prefix = 'hCSC'
        elif not sorted_text[0][1][0].isalpha():
            prefix = 'CSC'

        # Figure out the research area
        code = (prefix + sorted_text[0][1] +
               (sorted_text[1][1] if len(self.text) > 1 else ""))

        if prefix == "CSC":
            code = code[:6]
        elif self.hybrid:
            code = 'h' + str(hybrid_id_counter)
            hybrid_id_counter += 1

        self.area = 'core'
        for area, courses in AREAS.items():
            if code in courses:
                self.area = area
                break

        # Certain nodes have multiple lines of text. SVG text elements do not support
        # line wrapping or newlines, so two text elements need to be created.
        # Since there are now two text elements fitting into the node, the y positions
        # of the text elements need to be recalculated to account for this.
        if len(self.text) == 1:
            text = ('             S.text_ '
                   ' ! A.x "' + str(self.text_x) +
                   '" ! A.y "' + str(self.text_y) +
                   '" $ "' +
                   sorted_text[0][1] +
                   '"')
        else:
            text = list(map(self.create_output_text, sorted_text))
            text = ''.join(text)

        # Some hybrids may have identical IDs. 
        # This may cause problems when building the graph.
        print('S.g ! A.class_ "' + self.class_ + '" '
              ' ! A.id_ "' + code + '"'
              ' ! S.dataAttribute "group" "' + self.area + '"'
              ' ! A.style "" $ do \n'
              '             S.rect ! A.width "' + self.width +
              '" ! A.height "' + self.height +
              '" ! A.rx "4'
              '" ! A.ry "4'
              '" ! A.x "' + str(self.x) +
              '" ! A.y "' + str(self.y) +
              '" ! A.fill "' + self.colour +
              '" \n' + text
              )

    def __contains__(self, coords):
        dx = float(coords[0]) - float(self.x) + (float(self.parent_transform_x) * coords[2]) # Coords[2] is 0 if translation should not be applied, 1 if it should. Very hacky.
        dy = float(coords[1]) - float(self.y) + (float(self.parent_transform_y) * coords[2]) # Coords[2] is 0 if translation should not be applied, 1 if it should. Very hacky. Text elements are the only elements that require this.
        offset = 9
        return (-1 * offset <= dx <= float(self.width) + offset and
			    -1 * offset <= dy <= float(self.height) + offset)

    def create_output_text(self, dict_entry):

        # The Y coordinate of the text is identical to the input graph,
        # but for some reason the 4 position needs an offest of 4 to display
        # correctly with their parent rects.
        y_pos = str(float(dict_entry[0]) + self.parent_transform_y - 4)
        text_fragment = dict_entry[1]

        return ('             S.text_ '
                ' ! A.x "' + str(self.text_x) +
                '" ! A.y "' + 
                y_pos +
                '" $ "' +
                text_fragment +
                '"\n')