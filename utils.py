class Error:
    def __init__(self, token, row, message):
        print(token,row,message)
        self.token = token
        self.row = row
        self.message = message

    def __str__(self):
        return f'Item: {self.token}, Row: {self.row}, Message: {self.message}'


def printter(items, file_path):
    results_path = f"results/{file_path.split('/')[-1].split('.')[0]}.txt"
    print(results_path)
    file = open(results_path, "w")
    for item in items:
        file.write(str(item['name']) + '\n')
        file.write(str(item['content']) + '\n\n')
    file.close()
        