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
    # Get stats data
    df = get_combined_df()

    # Pick a tournament for today (e.g., rotate by date)
    tournaments = sorted(df['Tournament'].unique())
    import datetime
    today = datetime.date.today()
    tournament_of_the_day = tournaments[today.toordinal() % len(tournaments)]


    # Filter data to only this tournament
    filtered_df = df[df['Tournament'] == tournament_of_the_day]
    filtered = filtered_df.to_dict(orient='records')

    # Add a fixed offset to change the player selection
    chosen_statline = random.choice(filtered)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('index.html')
    rendered = template.render(players=filtered, tournament=tournament_of_the_day, chosen_statline=chosen_statline)

    # Write the rendered HTML
    with open(os.path.join(SITE_DIR, 'index.html'), 'w') as f:
        f.write(rendered)

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
