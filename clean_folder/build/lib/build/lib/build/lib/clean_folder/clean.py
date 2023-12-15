import sys
import re
import os
from pathlib import Path
import shutil
IMAGE_EXTENSIONS = ("jpeg", "png", "jpg", "svg")
VIDEO_EXTENSIONS = ("avi", "mp4", "mov", "mkv")
DOC_EXTENSIONS = ("doc", "docx", "txt", "pdf", "xlsx", "pptx")
AUDIO_EXTENSIONS = ("mp3", "ogg", "wav", "amr")
ARCHIVE_EXTENSIONS = ("zip", "gz", "tar")
UNKNOWN_EXTENSIONS = ()
KNOWN_EXTENSIONS = (IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + DOC_EXTENSIONS + AUDIO_EXTENSIONS + ARCHIVE_EXTENSIONS + UNKNOWN_EXTENSIONS)
DESIGNATED_FOLDERS = {"Images": IMAGE_EXTENSIONS, "Video": VIDEO_EXTENSIONS, "Documents": DOC_EXTENSIONS, "Audio": AUDIO_EXTENSIONS, "Archives": ARCHIVE_EXTENSIONS, "Unknown": UNKNOWN_EXTENSIONS}
POLISH_CHARACTERS = {"Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z", "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z"}
known_extensions_found = set()
unknown_extensions_found = set()
folder_to_clean = None

def check_argument():
    """Takes no arguments.
    Checks if script was run with correct argument (path to folder to clean)
    If not, asks user if wants to run a script in current directory
    """
    if len(sys.argv) < 2: #if script was run without an argument, suggest running script for current directory
        print("You didnt run script with argument (path to folder to clean)")
        while True:         
            decision = input(f"Do you want to run script for the current directory? Current directory: {os.getcwd()} y/n: ")
            if decision.lower() == "y":
                return Path(os.getcwd())
            elif decision.lower() == "n":
                print("Whatever. Have a nice day. Bye")
                exit()
            else:
                print("You need to type y/n. Try again.")
                continue
    elif not Path(sys.argv[1]).is_dir(): #checks if argument is a valid directory
        print("Argument is not a correct directiory")
        exit()
    else: # script was run with correct argument (path to folder to clean)
        print(f'Folder to clean: {sys.argv[1]}')
        return Path(sys.argv[1])

def normalize(string_to_normalize):
    """This method takes string as an input and returns altered string.
    Replaces characters "ę" "ą" "ż" etc for "e" "a "z"
    Charactes other then letters and digits are replaced with "_" 
    returns full name, separeted file name and separeted extension"""
    modified_full_name = ""
    file_name, file_extension = os.path.splitext(string_to_normalize) # separates file name and file extension
    file_extension = file_extension.lstrip(".")
    for character in file_name: # only file name is modified
        if character in POLISH_CHARACTERS: #changes polish characters to latin
            character = POLISH_CHARACTERS[character]
        if not re.search("\w", character): #charactes other then letters, digits and "_" gets replaced with "_"
            character = "_"
        modified_full_name += character
    modified_full_name += "." + file_extension
    return modified_full_name, file_name, file_extension

def going_through_folders_and_sorting_files_out(main_path_to_clean, current_path=None):
    """Funcion takes a path to folder to be cleaned as an argument and path to current subfolder(recurence)
    -funcion unpackes archives
    -normalize file names and moves them to designanted folders
    -doesnt change a name of a file with unknown extension"""
    if current_path == None:
        current_path = main_path_to_clean
    for item in current_path.iterdir():
        if item.is_dir(): #checks if item is a folder
            if item.name in DESIGNATED_FOLDERS.keys(): #ignoring certain folders
                continue
            else:
                going_through_folders_and_sorting_files_out(main_path_to_clean, item)  # going into subfolder
                continue      
        else: #item is a file
            if check_if_extension_is_known(item.name): #check if extension is known
                if normalize(item.name)[2].lower() in ARCHIVE_EXTENSIONS: #checks if file is an archive
                    move_archive_file(item, main_path_to_clean)
                else: # file with known extension, but not an archive
                    move_known_file(item, main_path_to_clean)
                continue
            else: # move file with unknown extension
                move_unknown_file(item, main_path_to_clean)
                continue
    return main_path_to_clean

def check_if_extension_is_known(name):
    """Method takes a string (file name) as an argument
    Returns True/False depending if extension is known"""
    file_extension = normalize(name)[2] #generating file extension
    if file_extension.lower() in KNOWN_EXTENSIONS:
        return True
    else:
        return False
    
def move_unknown_file(item, path):
    """Method takes an file path as argument
    Method moves an unknown file to 'Unknown' folder without changing a name
    Also adds an extension to a set to create a report later"""
    file_extension = normalize(item.name)[2] #generating file extension
    if not Path(f'{path}\\Unknown\\').exists(): #checks if Folder Unknown to exist and create it if necesary
        os.makedirs(Path(f'{path}\\Unknown\\')) #create folder to move a file
    shutil.move(item, Path(f'{path}\\Unknown\\{item.name}')) # move file to new location without changing a name
    unknown_extensions_found.add(file_extension) #adds unknown extension to a set to create a raport later on
    return

def move_archive_file(item, path):
    """Method takes an file path as argument
    Method unpacks an archive to an 'Archive' folder with new, normalized name
    Also adds an extension to a set to create a report later"""
    new_full_name, new_file_name, file_extension = normalize(item.name) #generating new name, also generating separated file name and extension
    if not Path(f'{path}\\Archives\\').exists(): #checks if Folder Unknown to exist and create it if necesary
        os.makedirs(Path(f'{path}\\Archives')) #create folder to move a file
    shutil.unpack_archive(item, Path(f'{path}\\Archives\\{new_file_name}')) #unpack archive in subfolder with designated name
    known_extensions_found.add(file_extension) #adds known archive extension to a set to create a raport later on    
    os.remove(item) #delete unpacked file
    return

def move_known_file(item, path):
    """Method takes an file path as argument
    Method determine a file type and moves it to a designated folder with new, normalized name
    Also adds an extension to a set to create a report later"""
    new_full_name, new_file_name, file_extension = normalize(item.name) #generating new name, also generating separated file name and extension
    for data_type, extension_list in DESIGNATED_FOLDERS.items(): #to determine type of a file
        if file_extension.lower() in extension_list:
            if not Path(f'{path}\{data_type}\\').exists(): #checks if Folder to move exist and create it if necesary
                os.makedirs(Path(f'{path}\{data_type}')) #create folder to move a file
            shutil.move(item, Path(f'{path}\{data_type}\{new_full_name}')) # move file to new location with new name
            known_extensions_found.add(file_extension) #adds known extension to a set to create a raport later on
    return

def delete_empty_folders(path):
    """Takes directory as an argument
    Method delete empty folders in a given directory
    Ignores designated folders"""
    for item in path.iterdir():
        if item.is_dir(): #checks if item is a folder
            if item.name in DESIGNATED_FOLDERS.keys(): #ignoring certain folders
                continue
            else:                
                if len(os.listdir(item)) == 0: #checks if folder is empty
                    os.rmdir(item)
                else:
                    delete_empty_folders(item)  # going into subfolder
                    os.rmdir(item) #delete a folder when all subfolders are gone
    return

def extensions_found_report():
    """Funcions prints report of found extension and gives files list"""
    if bool(unknown_extensions_found) or bool(known_extensions_found):
        print("\n")
        print('|{:^80}|'.format("-"*80))
        if bool(unknown_extensions_found): #unknown extension report 
            print('|{:^80}|'.format("*****Unknown Extensions Found*****"))
            print('|{:^80}|'.format("-"*80))
            for unknown_extension in unknown_extensions_found:
                print('|{:^80}|'.format(unknown_extension))
            print('|{:^80}|'.format("-"*80))
        if bool(known_extensions_found):
            print('|{:^80}|'.format("*****Known Extensions Found*****")) #known extensions report
            print('|{:^80}|'.format("-"*80))
            for known_extension in known_extensions_found:
                print('|{:^80}|'.format(known_extension))
            print('|{:^80}|'.format("-"*80))
        print("\n")
        return

def file_list_report(path):
    """Method prints complete file list"""
    for folder in DESIGNATED_FOLDERS: #going through main folders
        if folder == "Archives":
            if Path(f'{path}\{folder}\\').exists():
                print('|{:^80}|'.format("-"*80))
                print('|{:^80}|'.format(f"*****Folders in folder {folder}*****"))
                print('|{:^80}|'.format("-"*80))
                going_through_archive_folders_and_print_report(Path(f'{path}\\Archives\\')) #itering through archive folders
        else: #any other folder
            if Path(f'{path}\{folder}\\').exists():
                print('|{:^80}|'.format("-"*80))
                print('|{:^80}|'.format(f"*****Files in folder {folder}*****"))
                print('|{:^80}|'.format("-"*80))
                for file in Path(f'{path}\{folder}\\').iterdir():
                    print('|{:^80}|'.format(file.name))
    print('|{:^80}|'.format("-"*80))
    print("\n")
    return

def going_through_archive_folders_and_print_report(path): 
    """Method takes path item as argument
    Itering through all the Archive subfolders and printing file list"""
    for item in path.iterdir():
        if item.is_dir(): #check if item is a folder
            print('|{:^80}|'.format(f'***Files in folder {item.name}***'))
            print('|{:^80}|'.format("-"*80))
            going_through_archive_folders_and_print_report(item)
            continue
        else:
            print('|{:^80}|'.format(item.name))
    return
        
def main():
    folder_to_clean = check_argument()
    going_through_folders_and_sorting_files_out(folder_to_clean)
    delete_empty_folders(folder_to_clean)
    extensions_found_report()
    file_list_report(folder_to_clean)
    exit()

if __name__ == "__main__":
    main()
