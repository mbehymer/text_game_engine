from pynput import keyboard
import time, threading

def main():
    #get the name of the code to be used.
    code_file_name = 'textengine/example_code.txt'
    print(many_line)

    #read code line by line.
    lines = store_code(code_file_name)

    #compile code and return a map_array for printing.
    map_array = compile(lines)

    #Start up key listener.
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Begin the printing loop.
    # For now, game will be running within a terminal.
    class printThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
        def run(self):
            while(True):
                # This while loop loops through 3 key items: framerate, map_printing, and map_updating
                map_array.print_all()
                time.sleep(.5)
                # update_map() here

    p_thread = printThread()
    p_thread.start()

#helpful in debugging information
many_space = ' ' * 50
many_line = '\n' * 50

def grid_patcher(array:list):
    """
    TO BE USED ON MAP ARRAYS AND SPRITE ARRAYS.
    adds spaces until the array is rectangular, then returns the list
    patched with spaces.
    This function is called by functions in the MapObject class.
    """
    #find longest y:
    longest_y = 0
    #the length of map_array is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > longest_y:
            longest_y = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,longest_y - len(row)):
            row.append(" ")
    return array

class MapObject():
    def __init__(self):
        self.map_path = ''
        self.map_array = []

    def set_path(self,map_path):
        self.map_path = map_path
        self.store_map()
        #calls an array OUTSIDE the class
        self.map_array = grid_patcher(self.map_array)

    def store_map(self):
        #stores text from file as 2D array or list: [[x1,x2,x3],[x1,x2,x3]]
        with open(self.map_path,'r') as file:
            currentline = file.readline() #a string
            while currentline:
                xlist = []
                #remove any newline calls
                currentline = currentline[:-1]
                for char in currentline:
                    xlist.append(char)
                self.map_array.append(xlist)
                currentline = file.readline()
            
    def print_all(self):
        for i in range(0,len(self.map_array)):
            print('\033[A\033[F')
        for yrow in self.map_array:
            for yitem in yrow:
                print(yitem,end="")
            print()
            
    def set_x_y(self,x,y,character):
        try:
            self.map_array[y][x] = character
        except:
            pass
            # For when this point would not print within the map.

    def draw_sprites(self,spritedict:dict):
        #looks at map, replaces characters with sprites
        for item in spritedict.items():
            for y in range(len(self.map_array)):
                for x in range(len(self.map_array[y])):
                    if item.get_map_char() == self.map_array[x][y]:
                        self.add_array(item)

class VarObject():
    def __init__(self,variable, value):
        """
        stores a variable and what it equals
        """
        self.variable = variable
        self.value = value
        #This is for any variable that is NOT a class
        # i.e. var1 = 4, var3 = "hello"

class ClassObject():
    #iterations of this are to be stored in a regular dictionary
    """
    functions: set_xy(x,y), set_origin(x,y), set_array(array), set_map_char(char), set_movement(boolean),
    originx(), originy(), topleft(), bottomright()
    """
    #class type: map, sprite, sprites
    #origin, movement FOR SPRITE ONLY
    def __init__(self,array):
        self.array = array
        #the values below will simply not be called if the Classobject is a map or spritesheet
        self.originx = 0
        self.originy = 0
        #self.geometry = "default"
        self.movement = False
        self.on_map = ""

    def get_array(self):
        return self.array
    def set_array(self,array:list):
        self.array = array

    def get_map_char(self):
        return self.on_map
    def set_map_char(self,char):
        self.on_map = char

    def set_movement(self,can_move:bool):
        self.movement = can_move

    def get_originx(self):
        return int(self.originx)
    def get_originy(self):
        return int(self.originy)
    def set_origin(self,x,y):
        self.originx = x
        self.originy = y

    def set_xy_char(self,x,y,newchar):
        """
        Change a character at a given coordinate
        """
        try:
            self.array[y,x] = newchar
        except:
            pass
    def get_x_y(self,x:int,y:int):
        """
        Returns the character stored here in a sprite array.
        Not normally used on map array.
        """
        try:
            return self.array[y][x]
        except:
            return " "

    def topleft(self):
        """
        Return coordinate values [x,y] of topleft character in sprite.
        NOT in reference to map coordinates.
        """
        return [0,0]
    def bottomright(self):
        """
        Return coordinate values [x,y] of bottomright character in sprite.
        NOT in reference to map coordinates.
        """
        return [len(self.array)-1,len(self.array[len(self.array)-1])-1]

def compile(lines:list):
    #Store variables in dictionaries
    map_array = MapObject()
    var_container = {}
    #\/ This CAN contain copies of sprites that are named by the user 
    example_instance = ClassObject([['h','o'],['o','h']])
    sprite_dict = {'test':example_instance}
    sprites_file = ''
    for i in range(0,len(lines)):
        words = lines[i].split()
        if len(words) > 1:
            #FOR VARIABLE DECLARATIONS
            if words[1] == '=':
                #FOR CLASSES
                if words[2].find(")") == len(words[2])-1:
                    #map, sprites, sprite
                    classtype = words[2][:words[2].find("(")]
                    if classtype == "sprite":
                        #Most common occurrence probably
                        #only do this if sprite sheet is declared
                        if len(sprite_dict) > 0:
                            is_in_sprites = False
                            # i.e. tree = sprite($tree$)
                            var_value = dollar_word(words[2])
                            for key in sprite_dict.items():
                                if var_value == key[0]:
                                    is_in_sprites = True
                            if is_in_sprites:
                                #add duplicate sprite into dictionary under user-made
                                #variable name = words[0]
                                sprite_dict[words[0]] = sprite_dict[var_value]

                    elif classtype == "map":
                        #locate map file
                        mapname = dollar_word(words[2])
                        #create Map Object of file
                        map_array.set_path(mapname)

                    elif classtype == "sprites":
                        #take path, try to read
                        sprites_path = dollar_word(words[2])
                        #if it can be read, iterate through, save everything to sprite_dict
                        sprites_file = store_code(sprites_path)
                        #i would put a function call here from the spriteobject class                        
                        key = ""
                        one_sprite_array = []
                        for line in sprites_file:
                            if line[0] == "$":
                                #turn off sprite-line-reading:
                                if len(one_sprite_array) != 0:
                                
                                    sprite_dict[key] = ClassObject(one_sprite_array)
                                    #reset sprite array for reuse
                                    one_sprite_array = []
                                key = dollar_word(line)
                            else:
                                one_sprite_array.append([char for char in line if char != "\n"])
                        #this same function will store information in $DATA$ 
                    else: print(f'{many_space}Error: Class type not recognized: Line {lines[i]}')
                #ADDING CLASS DATA
                #search for a period. This implies changing class data
                elif words[0].find('.') != -1:
                    #look at word before '.'
                    varname = words[0][:words[0].find('.')]
                    attr = words[0][words[0].find('.')+1:]
                    att_value = words[2]
                    for key in sprite_dict.items():
                        # If the key is the same as the variable name, affect that key
                        if varname == key[0]:
                            if attr == 'xy' and att_value.find(',') != -1:
                                # i.e. player.xy = 3,4
                                attx = int(att_value[:att_value.find(',')])  # 3
                                atty = int(att_value[att_value.find(',')+1:])# 4
                                # place character on map
                                key[1].set_origin(attx,atty)
                            elif attr == 'movement':
                                # i.e. player.movement = true
                                key[1].set_movement(att_value == 'true')
                            elif attr == 'on_map':
                                # i.e. tree.on_map = $t$
                                key[1].set_map_char(dollar_word(att_value))

                #BASIC VARIABLE ASSIGNMENT
                else:
                    var_container[words[0]] = words[2]
            else: print(f'{many_space}Error: All lines of code should include an "=" assignment')
    
    #map_array.read_sprites(sprite_dict)
    #filter out any sprites that don't have a mapping character
    mappable_sprites = []
    for value in sprite_dict.values():
        # Check to see if this sprite has a map character
        if len(value.get_map_char())>0:
            mappable_sprites.append(value)
    for sprite in mappable_sprites:
    #goes through each character in the map
        for mapx in range(0,len(map_array.map_array)):
            for mapy in range(0,len(map_array.map_array[mapx])):
                #check if a sprite's map character is present on the map
                if map_array.map_array[mapx][mapy] == sprite.get_map_char():
                    # If it is, replace an area around that point with the sprite array
                    for spritey in range(sprite.topleft()[0],sprite.bottomright()[0] + 1):
                        for spritex in range(sprite.topleft()[1],sprite.bottomright()[1] + 1):
                            map_array.set_x_y(mapy + spritex,mapx + spritey, sprite.get_x_y(spritex,spritey))
    
                    
    return map_array

def dollar_word(word):
    """Takes a word and returns what is between dollar signs ($)"""
    word = word[(word.find('$') + 1):]
    return word[:(word.find('$'))]

#KEY LISTENING
def on_press(key):
    #must be called AFTER keyboard is 
    if key == keyboard.Key.esc:
        return False
    try: k = key.char
    except: k = key.name #for buttons like "left" or "space"
    if k in ['a','left']:
        pass
    elif k in ['w','up']:
        pass
    elif k in ['s','down']:
        pass
    elif k in ['d','right']:
        pass

#FILE READING
def can_be_read(filename:str):
    """Boolean function, check if file can be opened"""
    try:
        file = open(filename,'r')
        file.close()
        return True
    except: return False

def store_code(code_file_name:str):
    """
    Stores the code line by line from a file.
    Empty lines and comment lines are skipped.
    (read-only)
    """
    lines = []
    with open(code_file_name, 'r') as code:
        currentline = code.readline()
        while(currentline):
            if len(currentline) > 0:
                if currentline[0] != '#':
                    lines.append(currentline)
            currentline = code.readline()
    return lines
    #returns a list of strings

main()