from fcpxml import AssetClipsReport

reportWriter = AssetClipsReport('/Users/gregc/Documents/Code/fcpxml/Info_19feb2024.fcpxml')
success = reportWriter.writeReport('/Users/gregc/Desktop/Info_19feb2024.txt')
print(f'success = {success}')
