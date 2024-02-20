from fcpxml import AssetClipsReport

reportWriter = AssetClipsReport('/Users/gregc/Documents/Code/fcpxml/Info_20Feb2024.fcpxml')
success = reportWriter.writeReport('/Users/gregc/Desktop/Info_20Feb2024.txt')
print(f'success = {success}')
