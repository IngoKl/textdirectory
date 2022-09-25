import textdirectory

td = textdirectory.TextDirectory(directory='textdirectory/data/testdata/')
td.load_files(True, 'txt')

# Filter files by max characters
td.filter_by_max_chars(200)

# Stage the transformation to leetspeak
td.stage_transformation(['transformation_postag'])
td.print_pipeline()

# Perform the transformation
td.transform_to_memory()

print(td)
