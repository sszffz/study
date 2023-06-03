import os

def search_in_folder(root_path, keywords, log_file):
    for dir, folders, files in os.walk(root_path):
        print(dir)
        for file in files:
            if file.endswith(".docx") or file.endswith(".doc"):
                for keyword in keywords:
                    if keyword in file:
                        with open(log_file, "a+", encoding='utf-8') as fp:
                            fp.write(os.path.join(dir, file))
                            fp.write("\n")

# root_path_list = ["c:\\", "d:\\"]
root_path_list = ["g:\\"]
log_file = "search.log"
# keywords = ["2021", "2020", "2019", "2018", "summary", "总结", "年终", "年度"]
keywords = ["2021", "summary", "总结", "年终", "年度"]

for root_path in root_path_list:
    search_in_folder(root_path, keywords, log_file)





