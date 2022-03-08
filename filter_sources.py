import webbrowser
import click

def save_to_file(li):
	with open('filtered.txt', 'w') as f:
		f.write('\n'.join(li))

@click.command()
@click.option('--file')
def filter_sources(file: str):
	with open(file, 'r') as f:
		urls = f.read().split('\n')

	filtered = []

	click.echo(f'Reviewing ')

	for url in urls:
		if url:
			webbrowser.open(url, new=2)
			inp = input(f'Keep {url}? (Y/n): ')

			if inp.lower() == 'stop':
				save_to_file(filtered)
				return
			elif inp.lower() != 'n':
				filtered.append(url)
	
	save_to_file(filtered)

if __name__ == '__main__':
	filter_sources()