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

def IsRestricted(optionInfo):
	restricted = False
	if "DataRestriction" in optionInfo:
			for data in optionInfo["DataRestriction"]:
				restricted = restricted or GetData(data) == "Not Set"
	return restricted
	
def PrintMenu():
	current = current_stack[-1]
	os.system('CLS')
	print(current['Title'])
	if "Show" in current:
		for show in current["Show"]:
			data = GetData(show)
			name = Data[show]
			print("Current {} is <{}>".format(name, data))
			
	options = []
	optionHash = current['Options']
	for key in optionHash:
		options.append(key)
	options.sort()
	
	for optionId in options:
		optionInfo = optionHash[optionId]
		optionString = "{}:".format(optionId)

		if IsRestricted(optionInfo):
			optionString += "[X] "
		else:
			optionString += "    "
			
		
		if "Title" in optionInfo:
			optionString += "{}".format(optionInfo['Title'])
		elif 'Transition' in optionInfo:
			optionString += "{}".format(optionInfo['Transition']['Title'])
		print(optionString)
		
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
			if IsRestricted(option):
				EnterMenu()
				return
			if "Function" in option:
				option["Function"]()
				return
			if "FunctionParam" in option:
				funcData = option["FunctionParam"]
				func = funcData[0]
				param = funcData[1]
				func(param)
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
	
def GetData(key):
	data = "Not Set"
	if key in current_data:
		data = current_data[key]
	return data
	
def SetData(key):
	name = Data[key]
	os.system("CLS")
	data = GetData(key)
	print("Current {} is <{}>".format(name, data))
	choice = input("Press ENTER if this is correct, or enter new value:")
	choice = choice.rstrip()

	if choice != "":
		current_data[key] = choice

	EnterMenu()
	
# Exit program
def exit():
	sys.exit()

# =======================
#    MENUS DEFINITIONS
# =======================

Data = {
	"Origin":"Origin Folder",
	"Target":"Target Folder",
}
 
convert_mod = {
	"Title":"Convert Mod",
	"Show":["Origin", "Target"],
	"Options": {
		'1': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, "Origin")},
		'2': {'Title':"Set Target Folder", 'FunctionParam':(SetData, "Target")},
		'3': {'Title':"Convert Now", 'Function':ConvertMod, "DataRestriction":["Origin", "Target"]},
		'9': {'Title':"Back", 'Function':GoBack},
		},
}

unpack_mod = {
	"Title":"Unpack Mod",
	"Show":["Origin", "Target"],
	"Options": {
		'1': {'Title':"Set Origin Folder", 'FunctionParam':(SetData, "Origin")},
		'2': {'Title':"Set Target Folder", 'FunctionParam':(SetData, "Target")},
		'3': {'Title':"Unpack Now", 'Function':UnpackMod, "DataRestriction":["Origin", "Target"]},
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