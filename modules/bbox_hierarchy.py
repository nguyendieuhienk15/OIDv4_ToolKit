import csv

from modules.csv_downloader import *
from modules.hierarchy_getter import get_all_classes
from modules.utils import *
from modules.utils import bcolors as bc

class_length_file = 'length.csv'
class_error_file = 'error.csv'


def bbox_images(args, DEFAULT_OID_DIR):
    if not args.Dataset:
        dataset_dir = os.path.join(DEFAULT_OID_DIR, 'Dataset')
        csv_dir = os.path.join(DEFAULT_OID_DIR, 'csv_folder')
    else:
        dataset_dir = os.path.join(DEFAULT_OID_DIR, args.Dataset)
        csv_dir = os.path.join(DEFAULT_OID_DIR, 'csv_folder')

    name_file_class = 'class-descriptions-boxable.csv'
    CLASSES_CSV = os.path.join(csv_dir, name_file_class)

    folder = ['train', 'validation', 'test']
    file_list = ['train-annotations-bbox.csv', 'validation-annotations-bbox.csv', 'test-annotations-bbox.csv']

    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    if args.command == 'count':

        if args.type_csv is None:
            print(bc.FAIL + 'Missing type_csv argument.' + bc.ENDC)
            exit(1)
        if args.classes is None:
            print(bc.FAIL + 'Missing classes argument.' + bc.ENDC)
            exit(1)

        if args.classes[0].endswith('.txt'):
            with open(args.classes[0]) as f:
                args.classes = f.readlines()
                args.classes = [x.strip() for x in args.classes]
        else:
            args.classes = [arg.replace('_', ' ') for arg in args.classes]

        write_code = 'print'

        for classes in args.classes:

            print(bc.INFO + 'Counting {}.'.format(classes) + bc.ENDC)
            class_name = classes

            error_csv(name_file_class, csv_dir)
            df_classes = pd.read_csv(CLASSES_CSV, header=None)

            class_code = df_classes.loc[df_classes[1] == class_name].values[0][0]

            if args.type_csv == 'train':
                name_file = file_list[0]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[0], class_name, class_code, write_code)

            elif args.type_csv == 'validation':
                name_file = file_list[1]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[1], class_name, class_code, write_code)

            elif args.type_csv == 'test':
                name_file = file_list[2]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[2], class_name, class_code, write_code)

            elif args.type_csv == 'all':
                for i in range(3):
                    name_file = file_list[i]
                    df_val = TTV(csv_dir, name_file)
                    count_images(args, df_val, folder[i], class_name, class_code, write_code)
            else:
                print(bc.ERROR + 'csv file not specified' + bc.ENDC)
                exit(1)

    elif args.command == 'count_all':

        if args.type_csv is None:
            print(bc.FAIL + 'Missing type_csv argument.' + bc.ENDC)
            exit(1)

        all_my_class = get_all_classes()
        already_count_class = []

        # Skip counted class
        try:
            with open(class_length_file, 'r') as f:
                reader = csv.DictReader(f, ['class_name', 'length'])
                for row in reader:
                    already_count_class.append(row['class_name'])
                del already_count_class[0]  # delete tile 'class_name'
                t = len(already_count_class)
                all_my_class = all_my_class[t:]
            f.close()
            print(bc.INFO + 'Already counted: {}'.format(already_count_class) + bc.ENDC)
        except FileNotFoundError:
            with open(class_length_file, 'w') as f:
                writer = csv.DictWriter(f, ['class_name', 'length'])
                writer.writeheader()
            f.close()

        write_code = 'write_file'

        for classes in all_my_class:

            print(bc.INFO + 'Counting {}.'.format(classes) + bc.ENDC)

            class_name = classes
            error_csv(name_file_class, csv_dir)
            df_classes = pd.read_csv(CLASSES_CSV, header=None)

            try:
                class_code = df_classes.loc[df_classes[1] == class_name].values[0][0]
            except IndexError:
                write_error(class_name)
                write_length(class_name, 0)
                continue

            if args.type_csv == 'train':
                name_file = file_list[0]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[0], class_name, class_code, write_code)

            elif args.type_csv == 'validation':
                name_file = file_list[1]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[1], class_name, class_code, write_code)

            elif args.type_csv == 'test.json':
                name_file = file_list[2]
                df_val = TTV(csv_dir, name_file)
                count_images(args, df_val, folder[2], class_name, class_code, write_code)

            elif args.type_csv == 'all':
                for i in range(3):
                    name_file = file_list[i]
                    df_val = TTV(csv_dir, name_file)
                    count_images(args, df_val, folder[i], class_name, class_code, write_code)

            else:
                print(bc.ERROR + 'csv file not specified' + bc.ENDC)
                exit(1)


def count_images(args, df_val, folder, class_name, class_code, count_code):
    df_val_images = images_options(df_val, args)

    try:
        images_list = df_val_images['ImageID'][df_val_images.LabelName == class_code].values
        images_list = set(images_list)
        length = len(images_list)
        print(bc.INFO + 'Found {} online images of {} for {}.'.format(length, class_name, folder) + bc.ENDC)
        if count_code == 'write_file':
            write_length(class_name, length)
    except IndexError:
        if count_code == 'write_file':
            write_error(class_name)
        else:
            print(bc.INFO + '{} for {} not found.'.format(class_name, folder) + bc.ENDC)


def write_length(class_name, length):
    with open(class_length_file, 'a') as f:
        writer = csv.DictWriter(f, ['class_name', 'length'])
        writer.writerow({'class_name': class_name, 'length': str(length)})
    f.close()


def write_error(class_name):
    f = open(class_error_file, 'a')
    f.write(class_name + "\n")
    f.close()
