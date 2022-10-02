import textdirectory

td = textdirectory.TextDirectory(directory='textdirectory/data/testdata/')
td.load_files(True, 'txt')

# Stage the same transformation with different arguments
td.stage_transformation(['transformation_replace_string', 'Lorem', 'X'])
td.stage_transformation(['transformation_replace_string', 'ipsum', 'Y'])
td.print_pipeline()

# Perform the transformation
td.transform_to_memory()

print(td)
