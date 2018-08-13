# Load Order

The Load Order scripts (LOAD_ORDER.BAT & PACKED_LOAD_ORDER.BAT) are scripts that take a list of mod folders and puts together a package that can be copied across to the SD card ready for playing.

### Usage
Both scripts take 3 parameters:
- The origin folder
- The target folder
- the name of the load order to use

## Origin Folder
The Origin folder should contain a list of folders, one per mod.  Each mod folder should contain everything from that mod that you would put in your Data folder on the SD card, so esp, bsas, and ini files.

It should also contain all of your load order files, named <YourLoadOrderName>.txt

## Target Folder
The target folder is where the script will put your package.  Everything in that folder (if it already exists) will be erased before the packing occurs.

## Load Order Name
The script will look for your load order text file in the Origin folder, and use it to make your package.
The text file should start with a number on the first line, this is the number of the first sTestFile that is availble for the script to put esps in.
As an examle, I use 4, because I do not use the Hyrule.esp.  The script will explicitly remove the Hyrule.bsa if you select 4 or less.  I have no idea what would happen if you used 3 or less, since you'd then be not loading the original esms, and I'm sure there's data in the bsas that might not work if the corresponding esm is not present.

After the StartingESP number is set, then list the name of each mod in the order you want them loaded, with the name matching the name of the folder containing that mod.

### Output
The output folder will end up containing ```
Skyrim.ini
Skyrim_de.ini
Skyrim_en.ini
Skyrim_es.ini
Skyrim_fr.ini
Skyrim_it.ini
Skyrim_ja.ini
Skyrim_ru.ini```

They will all be modified to correctly load the esps and main, mesh, and texture bsas of every mod in your list.  If a mod contained an INI file, then the contents of that file should be included in the ini files as well.
The Data folder will then contain all the esps and bsas that are required.
This folder can be copied directly to your SD card as is.
