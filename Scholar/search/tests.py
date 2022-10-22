import requests

# t1 = time.time()
# print(get_index_data())
# t2 = time.time()
# print(t2 - t1)

params = {
    # "q": "StyTr2",
    "search": "Denoising Diffusion",
}
url = "https://api.openalex.org/" + "works"
response = requests.get(url, params=params)
print(response.json())
