from fcpxml import AssetClipsCSV

csvWriter = AssetClipsCSV('/Users/gregc/Documents/Code/fcpxml/tests/files/Info.fcpxml')
success = csvWriter.writeCSV('/Users/gregc/Desktop/Info.csv')
print(f'success = {success}')