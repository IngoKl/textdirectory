import textdirectory

td = textdirectory.TextDirectory(directory='textdirectory/data/testdata/')
td.load_files(True, 'txt')

# Stage three transformations
td.stage_transformation(['transformation_lowercase'])
# Transformation with arguments
td.stage_transformation(['transformation_remove_stopwords', 'internal', 'en', 'en_core_web_sm', 'lorem,ipsum'])
td.stage_transformation(['transformation_remove_nl'])

td.print_pipeline()

# Perform the transformation
td.transform_to_memory()

print(td)
