import os
import shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from oozedle.stats import get_combined_df

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SITE_DIR = os.path.join(ROOT_DIR, 'site')
TEMPLATES_DIR = os.path.join(SITE_DIR, 'templates')
STATIC_DIR = os.path.join(SITE_DIR, 'static')

# Ensure site directories exist
os.makedirs(SITE_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

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

    # Choose the answer player deterministically by date
    if len(filtered) > 0:
        answer_idx = today.toordinal() % len(filtered)
        chosen_statline = filtered[answer_idx]
    else:
        chosen_statline = None

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('index.html')
    rendered = template.render(players=filtered, tournament=tournament_of_the_day, chosen_statline=chosen_statline)

    # Write the rendered HTML
    with open(os.path.join(SITE_DIR, 'index.html'), 'w') as f:
        f.write(rendered)

    # Copy static files (js/css)
    for fname in ['main.js', 'style.css']:
        src = os.path.join(TEMPLATES_DIR, fname)
        dst = os.path.join(STATIC_DIR, fname)
        if os.path.exists(src):
            shutil.copy(src, dst)

if __name__ == '__main__':
    main()
