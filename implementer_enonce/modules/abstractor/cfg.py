import os 

def read_api_key(api:str=""):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"{api}_api_key.txt")) as file:
        content=file.read()
    return content

if __name__=="__main__":
    APIKEY=read_api_key().strip().strip('"')
