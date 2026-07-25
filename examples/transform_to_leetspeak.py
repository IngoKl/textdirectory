import textdirectory

td = textdirectory.TextDirectory(directory='tests/data/testdata/')
td.load_files(recursive=True, filetype='txt')

# Stage the transformation to leetspeak
td.stage_transformation(['transformation_to_leetspeak'])
td.print_pipeline()

# Perform the transformation
td.transform_to_memory()

print(td)
