import os
import shutil
import random

from jinja2 import Environment, FileSystemLoader

from oozedle.stats import get_combined_df

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Output directory for the static site
SITE_DIR = os.path.join(ROOT_DIR, 'output')
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'site', 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'site', 'static')
OUTPUT_STATIC_DIR = os.path.join(SITE_DIR, 'static')

# Ensure output directories exist
os.makedirs(SITE_DIR, exist_ok=True)
os.makedirs(OUTPUT_STATIC_DIR, exist_ok=True)

def main():

    years = [2024, 2025, 2026]
    stat_headers_by_year = {
        2024: ['Points Played', 'Assists', 'Goals', "D's", 'Turnovers'],
        2025: ['Points Played', 'Assists', 'Goals', "D's", 'Turnovers'],
        2026: ['Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers'],
    }

    import datetime
    today = datetime.date.today()

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('index.html')

    for year in years:
        df = get_combined_df(year)
        tournaments = sorted(df['Tournament'].unique())
        tournament_of_the_day = tournaments[today.toordinal() % len(tournaments)]
        filtered_df = df[df['Tournament'] == tournament_of_the_day]
        filtered = filtered_df.to_dict(orient='records')
        chosen_statline = random.choice(filtered)
        stat_headers = stat_headers_by_year[year]
        rendered = template.render(players=filtered, tournament=tournament_of_the_day, chosen_statline=chosen_statline, stat_headers=stat_headers, year=year)
        # Write the rendered HTML for this year
        with open(os.path.join(SITE_DIR, f'{year}.html'), 'w') as f:
            f.write(rendered)

    # Also write index.html as a redirect to the latest year (2026)
    index_redirect = '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=2026.html"></head><body></body></html>'
    with open(os.path.join(SITE_DIR, 'index.html'), 'w') as f:
        f.write(index_redirect)

    # Copy static files (js/css) from site/static or site/templates to output/static
    for fname in ['main.js', 'style.css']:
        src_static = os.path.join(STATIC_DIR, fname)
        src_templates = os.path.join(TEMPLATES_DIR, fname)
        dst = os.path.join(OUTPUT_STATIC_DIR, fname)
        if os.path.exists(src_static):
            shutil.copy(src_static, dst)
        elif os.path.exists(src_templates):
            shutil.copy(src_templates, dst)

if __name__ == '__main__':
    main()
