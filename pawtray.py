__version__ = '0.1'

import argparse
from pathlib import Path
from datetime import datetime as dt
from playwright.sync_api import sync_playwright

def main():
	parser = argparse.ArgumentParser(
		description=f'Version: {__version__}'
	)
	parser.add_argument('targetsfile', action='store', help='file with one url per line ([http|s://]host[:port][/path])')
	parser.add_argument('-l', '--loot', required=False, default='./', action='store', help='directory to store the screenshots in')
	parser.add_argument('-a', '--append', required=False, default='', action='store', help='suffix to append to every url')
	parser.add_argument('-s', '--ssl', required=False, action='store_true', help='default to https instead of http when no protocol is specified')
	parser.add_argument('-v', '--version', required=False, action='store_true', help='print version')

	args = parser.parse_args()

	if args.version == True:
		print(f'v{__version__}')
		exit(0)

	targets = Path(args.targetsfile)
	if not targets.is_file():
		print(f'[!] Failed to open {args.targetsfile}')
		exit(1)

	lootdir = Path(args.loot)
	lootdir.mkdir(parents=True, exist_ok=True)

	take_screenshots(targets, args.append, lootdir, args.ssl)

def take_screenshots(targets, targets_suffix, lootdir, default_to_https):
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context()

		page = context.new_page()

		total= sum(1 for i in open(targets, 'rb'))

		with open(targets, 'r') as f:
			n_done = 0
			print(f'[+] Starting at {dt.now().strftime("%Y-%m-%d %H:%M:%S")}')
			for target in f:
				target = target.strip()
				if target == '':
					continue
				try:
					port = '443' if default_to_https else '80'
					if ':' in target:
						port = target.split(':')[1].split('/')[0]

					if not target.startswith('http'):
						if port == '80':
							target = 'http://' + target
						elif port == '443':
							target = 'https://' + target
						else:
							target = 'http' + ('s' if default_to_https else '') + target

					target = target+targets_suffix

					print(f'[{n_done:>6}|{total}] ({int(n_done/total*100):>3}%) Capturing: {target}', end='\r')
					page.goto(target)

					filename = target
					filename = filename.replace('/', '_')
					filename = filename.replace('#', '_')
					filename = filename.replace('%', '_')
					filename = filename.replace('{', '_')
					filename = filename.replace('}', '_')
					filename = filename.replace('\\', '_')
					filename = filename.replace('<', '_')
					filename = filename.replace('>', '_')
					page.screenshot(path=lootdir.joinpath(f'{filename}_{dt.now().strftime("%Y-%m-%d_%H:%M:%S")}.png'), full_page=True)
					n_done += 1
					if n_done == total:
						print(f'[{n_done:>6}|{total}] ({int(n_done/total*100):>3}%)')
				except Exception as e:
					print(f'[!] Parsing {target} failed with: {e}')
					exit(1)
			print(f'[+] Finished at {dt.now().strftime("%Y-%m-%d %H:%M:%S")}')
			print(f'[+] Written {n_done} screenshots to {lootdir}.')

if __name__ == '__main__':
	main()
