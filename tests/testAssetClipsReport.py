from fcpxml import AssetClipsReport

reportWriter = AssetClipsReport('/Users/gregc/Documents/Code/fcpxml/Info.fcpxml')
success = reportWriter.writeReport('/Users/gregc/Desktop/Info.txt')
print(f'success = {success}')
