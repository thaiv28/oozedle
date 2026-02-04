// main.js - Oozedle game logic

// The PLAYERS variable is injected by Jinja2 in index.html

let chosen = typeof CHOSEN !== 'undefined' ? CHOSEN : null;

let guesses = [];
let maxGuesses = 6;
let gameWon = false;
let gameLost = false;


// No longer needed: statline is chosen deterministically in Python and injected as CHOSEN

function compareGuess(guess, answer) {
    // Returns feedback for each stat
    const feedback = {};
    for (const key of Object.keys(guess)) {
        if (key === 'Name' || key === 'Tournament') continue;
        if (answer[key] > guess[key]) feedback[key] = 'greater';
        else if (answer[key] < guess[key]) feedback[key] = 'less';
        else feedback[key] = 'equal';
    }
    return feedback;
}



function renderGame() {
    // Get unique player names for this tournament
    // Remove guessed players from the dropdown
    const guessedNames = guesses.map(g => g.Name);
    const playerNames = [...new Set(PLAYERS.map(p => p.Name))].filter(name => !guessedNames.includes(name)).sort();
    const statNames = ['Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers'];
    const statShort = {
        'Points Played': 'P',
        'Assists': 'A',
        'Goals': 'G',
        'Blocks': 'B',
        'Turnovers': 'T'
    };

    let html = '';
    if (gameWon || gameLost) {
        html += `<div class="congrats-message">
            <h2>${gameWon ? '🎉 Congrats! 🎉' : "Sorry, you didn't get it in 6 guesses."}</h2>
            <p>${gameWon ? 'You guessed the correct player!' : 'The correct player was:'}</p>
            <h3>${chosen.Name}</h3>
            <table class="statline-table congrats-message">
                <tbody>
                    <tr><th>Points Played</th><td>${chosen['Points Played']}</td></tr>
                    <tr><th>Assists</th><td>${chosen['Assists']}</td></tr>
                    <tr><th>Goals</th><td>${chosen['Goals']}</td></tr>
                    <tr><th>Blocks</th><td>${chosen['Blocks']}</td></tr>
                    <tr><th>Turnovers</th><td>${chosen['Turnovers']}</td></tr>
                </tbody>
            </table>
            <div style="margin-top: 24px;"><button id="share-results-btn">Share Results</button></div>
        </div>`;
    } else {
        html += '<form id="guess-form">';
        html += '<label for="player-select">Select a player:</label> ';
        html += '<select id="player-select" required>';
        html += '<option value="" disabled selected>Select player</option>';
        for (const name of playerNames) {
            html += `<option value="${name}">${name}</option>`;
        }
        html += '</select> ';
        html += '<button type="submit">Guess</button>';
        html += '</form>';
    }

    // Arrow meaning comment
    html += '<div class="arrow-legend">';
    html += '↑ = Hidden player had MORE of the stat <br>↓ = Hidden player had LESS of the stat';
    html += '</div>';

    // Guess grid
    html += '<table class="guess-grid">';
    html += '<thead><tr><th>Player</th>';
    for (const stat of statNames) {
        html += `<th>${statShort[stat]}</th>`;
    }
    html += '</tr></thead><tbody>';
    for (let i = 0; i < guesses.length; i++) {
        const guess = guesses[i];
        const feedback = compareGuess(guess, chosen);
        html += '<tr>';
        html += `<td>${guess.Name}</td>`;
        for (const stat of statNames) {
            let symbol = '';
            let cellClass = '';
            if (feedback[stat] === 'greater') {
                symbol = '↑';
                cellClass = 'arrow-up';
            } else if (feedback[stat] === 'less') {
                symbol = '↓';
                cellClass = 'arrow-down';
            } else if (feedback[stat] === 'equal') {
                symbol = '=';
                cellClass = 'arrow-equal';
            }
            html += `<td class="${cellClass}">${symbol}</td>`;
        }
        html += '</tr>';
    }
    html += '</tbody></table>';

    document.getElementById('game').innerHTML = html;

    if (!gameWon && !gameLost) {
        document.getElementById('guess-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const selectedName = document.getElementById('player-select').value;
            handleGuess(selectedName);
        });
    } else {
        // Add event listener for share button
        const shareBtn = document.getElementById('share-results-btn');
        if (shareBtn) {
            shareBtn.addEventListener('click', function() {
                const summary = generateShareSummary();
                navigator.clipboard.writeText(summary).then(() => {
                    shareBtn.textContent = 'Copied!';
                    setTimeout(() => { shareBtn.textContent = 'Share Results'; }, 1500);
                });
            });
        }
    }
// Generate a Wordle-like summary of the results
function generateShareSummary() {
    const statNames = ['Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers'];
    let summary = `Oozedle ${gameWon ? guesses.length : 'X'}/6\n`;
    for (let i = 0; i < guesses.length; i++) {
        const guess = guesses[i];
        const feedback = compareGuess(guess, chosen);
        let row = '';
        for (const stat of statNames) {
            if (feedback[stat] === 'equal') row += '🟩';
            else if (feedback[stat] === 'greater') row += '🟦';
            else if (feedback[stat] === 'less') row += '🟧';
        }
        if (i !== guesses.length - 1) {
            summary += row + '\n';
        }
    }
    return summary;
}
}


function handleGuess(playerName) {
    // Find the statline for the guessed player
    const guess = PLAYERS.find(p => p.Name === playerName);
    if (!guess) {
        alert('Invalid guess.');
        return;
    }
    guesses.push(guess);
    if (guess.Name === chosen.Name) {
        gameWon = true;
    } else if (guesses.length >= maxGuesses) {
        gameLost = true;
    }
    renderGame();
}

document.addEventListener('DOMContentLoaded', () => {
    renderGame();
});
