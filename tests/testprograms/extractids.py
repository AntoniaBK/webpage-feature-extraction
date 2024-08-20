from bs4 import BeautifulSoup

def extract_unique_ids(file_path):
	"""
	Extracts all unique ids from the given HTML content.

	Parameters:
	- html_content (str): A string containing HTML content.

	Returns:
	- set: A set containing all unique ids.
	"""
	with open(file_path, 'r', encoding='utf-8') as file:
		html_content = file.read()

	soup = BeautifulSoup(html_content, 'html.parser')
	ids = set()

	# Find all elements with an id attribute
	for element in soup.find_all(attrs={'id': True}):
		ids.add(element['id'])

	return ids

# Example usage:
if __name__ == "__main__":

	html_content = "./pages.html"

	unique_ids = extract_unique_ids(html_content)
	print(unique_ids)
