csv_file_path_read = 'block_data.csv'
csv_file_path_write = 'post_June_data.csv'

start_block = 19993250
end_block = float('inf')

with open(csv_file_path_read, 'r') as file:
    lines = file.readlines()

# Retain the header
header = lines[0]

filtered_lines = [line for line in lines[1:] if start_block <= int(line.split(',')[0]) <= end_block]

# Write the header and the filtered lines back to the file
with open(csv_file_path_write, 'w') as file:
    file.write(header)  # Write the header first
    file.writelines(filtered_lines)
