import csv

result_map = {}

with open('classification_results.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        result_map[row[0]] = row[1]

count = 0

with open('output.txt') as file:
    lines = file.readlines()
    for line in lines:
        if "Classification result" in line:
            count += 1
            split_list = line.replace('Classification result: ', '').strip().split(',')
            if len(split_list) == 1:
                print("Missing output!")
                exit()
            output = split_list[1][:-2]
            image_name_list = split_list[0].strip().split('"')[-1].split(".")
            image_name_list[-1] = image_name_list[-1].upper()
            image_name = ".".join(image_name_list)
            if image_name not in result_map:
                print(image_name, ": missing output")
            elif output != result_map[image_name]:
                print("Wrongly classified")
                exit()
            else:
                print(image_name, output)


print(count)

if count != len(result_map):
    print("Images missed")

else:
    print("All images are correctly processed and classified")
'''
python3 multithread_workload_generator.py \
 --num_request 100\
 --url 'http://{ec2_public_url}/get_output' \
 --image_folder "./imagenet-100/"
'''

