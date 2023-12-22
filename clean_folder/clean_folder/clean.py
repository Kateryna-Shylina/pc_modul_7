import re
import sys
import shutil
from pathlib import Path

UKRAINIAN = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS_DICT = {}

images = list()
documents = list()
audio = list()
video = list()
folders = list()
archives = list()
others = list()
unknown_extensions = set()
registered_extensions = set()

main_folders = {
    'images': [images, ['JPEG', 'PNG', 'JPG', 'SVG']],
    'documents': [documents, ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']],
    'audio': [audio, ['MP3', 'OGG', 'WAV', 'AMR']],
    'video': [video, ['AVI', 'MP4', 'MOV', 'MKV']],
    'archives': [archives, ['ZIP', 'GZ', 'TAR']],
    'folders': [folders],    
    'others': [others] 
}

for key, value in zip(UKRAINIAN, TRANSLATION):
    TRANS_DICT[ord(key)] = value
    TRANS_DICT[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS_DICT)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def sort(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('images', 'documents',  'audio', 'video', 'folders', 'archives', 'others'):
                folders.append(item)
                sort(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            container = None
            for key, value in main_folders.items():
                if key not in ('folders', 'others'):
                    for ext in value[1]:                        
                        if extension == ext:
                            container = value[0]
                            break
                    if container != None:
                        registered_extensions.add(extension)
                        container.append(new_name)
                        break                
            else:
                unknown_extensions.add(extension)
                others.append(new_name)      


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name.replace(".zip", '').replace(".gz", '').replace(".tar", ''))

    archive_folder = target_folder/new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def get_files_list(path):
    files_list = list()
    if path.exists():        
        for item in path.iterdir():
            files_list.append(item.name)

    return files_list

def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    
    sort(folder_path)

    for file in images:
        handle_file(file, folder_path, "images")

    for file in documents:
        handle_file(file, folder_path, "documents")

    for file in audio:
        handle_file(file, folder_path, "audio")

    for file in video:
        handle_file(file, folder_path, "video")

    for file in others:
        handle_file(file, folder_path, "others")

    for file in archives:
        handle_archive(file, folder_path, "archives")

    remove_empty_folders(folder_path)

    result_file_path = folder_path/'FilesList.txt'
    with open(result_file_path, 'w') as fw:
        fw.write(f"All extensions: {registered_extensions}\n")
        fw.write(f"Unknown extensions: {unknown_extensions}\n")
        fw.write(f"images: {get_files_list(folder_path/'images')}\n")
        fw.write(f"documents: {get_files_list(folder_path/'documents')}\n")
        fw.write(f"audio: {get_files_list(folder_path/'audio')}\n")
        fw.write(f"video: {get_files_list(folder_path/'video')}\n")
        fw.write(f"archive: {get_files_list(folder_path/'archives')}\n")
        fw.write(f"others: {get_files_list(folder_path/'others')}\n")
        

if __name__ == '__main__':
    main()