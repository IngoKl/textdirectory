import textdirectory

td = textdirectory.TextDirectory(directory='data/testdata/')
td.load_files(True, 'txt')

td.filter_by_max_chars(480)
td.stage_transformation(['transformation_to_leetspeak'])
td.filter_by_min_chars(14)
td.print_pipeline()
td.load_aggregation_state()
td.print_pipeline()
td.print_saved_states()


td.transform_to_memory()
