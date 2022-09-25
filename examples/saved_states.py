import textdirectory

td = textdirectory.TextDirectory(directory='textdirectory/data/testdata/')
td.load_files(True, 'txt')

td.filter_by_max_chars(100)
print(td)

td.filter_by_random_sampling(2)
print(td)

td.print_saved_states()

# Going back to a previous state
td.load_aggregation_state(1)
print(td)
