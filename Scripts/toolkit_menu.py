#! python3

# Import the modules needed to run the script.
import sys, os

current_stack = []
current_data = {}

def TransitionToMenu(menu):
	current_stack.append(menu)
	EnterMenu()

def EnterMenu():
	PrintMenu()
	choice = input(" >> ")
	ExecuteMenuChoice(choice)

def PrintMenu():
	current = current_stack[-1]
	os.system('CLS')
	print(current['Title'])
	options = []
	optionHash = current['Options']
	for key in optionHash:
		options.append(key)
	options.sort()
	
	for optionId in options:
		optionInfo = optionHash[optionId]
		if "Title" in optionInfo:
			print("{}: {}".format(optionId, optionInfo['Title']))
		elif 'Transition' in optionInfo:
			print("{}: {}".format(optionId, optionInfo['Transition']['Title']))
		
# Execute menu
def ExecuteMenuChoice(choice):
	ch = choice.lower().rstrip()
	current = current_stack[-1]
	
	if ch == '':
		EnterMenu()
		return
	else:
		optionHash = current['Options']
		try:
			option = optionHash[ch]
			if "Function" in option:
				option["Function"]()
				return
			if "FunctionParam" in option:
				funcData = option["FunctionParam"]
				func = funcData[0]
				params = funcData[1]
				func(*params)
				return
			if "Transition" in option:
				TransitionToMenu(option["Transition"])
		except KeyError:
			print("Invalid option <{}>, options are <{}>".format(ch, str(optionHash)))
			EnterMenu()

def GoBack():
	current_stack.pop()
	EnterMenu()
	
# =======================
#          MENUS FUNCTIONS
# =======================
	
def ConvertMod():
	print("Convert MOD NOW!")
	exit()

def UnpackMod():
	print("Unpack MOD NOW!")
	exit()
	
def SetData(key, name):
	os.system("CLS")
	data = "Not Set"
	if key in current_data:
		data = current_data[key]
	print("Current {} is <{}>".format(name, data))
	choice = input("Press ENTER if this is correct, or enter new value:")
	choice = choice.rstrip()
	current_data[key] = choice
	if choice != "":
		SetData(key, name)
	EnterMenu()
	
# Exit program
def exit():
	sys.exit()
 
# =======================
#    MENUS DEFINITIONS
# =======================
 
convert_mod = {
	"Title":"Convert Mod",
	"Show":["OriginFolder"],
	"Options": {
		'1': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, ["Origin", "Origin Folder"])},
		'2': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, ["Target", "Target Folder"])},
		'3': {'Title':"Convert Now", 'Function':ConvertMod},
		'9': {'Title':"Back", 'Function':GoBack},
		},
}

unpack_mod = {
	"Title":"Unpack Mod",
	"Show":["OriginFolder"],
	"Options": {
		'1': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, ["Origin", "Origin Folder"])},
		'2': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, ["Target", "Target Folder"])},
		'3': {'Title':"Unpack Now", 'Function':UnpackMod},
		'9': {'Title':"Back", 'Function':GoBack},
		},
}

main_menu = {
	"Title":"Main Menu",
	"Options": {
		'1': {'Transition':convert_mod},
		'2': {'Transition':unpack_mod},
		'9': {'Title':"Exit", 'Function':exit},
		}
}
 
# =======================
#      MAIN PROGRAM
# =======================
 
# Main Program
if __name__ == "__main__":
	# Launch main menu
	TransitionToMenu(main_menu)