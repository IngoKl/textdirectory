import textdirectory

td = textdirectory.TextDirectory(directory='data/testdata/')
td.load_files(True, 'txt')

td.filter_by_max_chars(480)
td.stage_transformation(['transformation_to_leetspeak'])
td.print_pipeline()

td.transform_to_memory()
