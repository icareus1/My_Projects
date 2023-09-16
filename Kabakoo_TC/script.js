document.addEventListener("DOMContentLoaded", function() {
    let randomWord = '',
    wordDefinition = '',
    infos = '',
    maxGuesses,
    corrects = [],
    incorrects = [];

    const inputs = document.querySelector(".inputs"),
    resetBtn = document.querySelector('.reset-btn'),
    definition = document.querySelector('.hint span'),
    moreInfo = document.querySelector('#infos'),
    wrongLetter = document.querySelector('.wrong-letter span'),
    guessLeft = document.querySelector('.guess-left span'),
    typingInput = document.querySelector('.typing-input');


    function fetchRandomWordAndDefinition() {
        let html = '';
        incorrects = [];
        corrects = [];
    // Fetch a random word from https://random-word-api.herokuapp.com/word
    fetch('https://random-word-api.herokuapp.com/word')
        .then(response => response.json())
        .then(async data => {
        randomWord = data; // Assign the random word to a variable
        // Use the random word to search for its definition in the dictionary API
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${randomWord}`);
            if (response.status === 404) {
                console.log(`No definition found for '${randomWord}'. Trying again...`);
                // If the response status is 404, recursively call the function to fetch another random word
                fetchRandomWordAndDefinition();
            } else {
                return response.json();
            }
        })
        .then(dictionaryData => {
            if (Array.isArray(dictionaryData) && dictionaryData.length > 0) {
                wordDefinition = dictionaryData[0].meanings[0]?.definitions[0]?.definition;
                infos = dictionaryData[0].meanings[0].partOfSpeech;

                //Convert the word and its definition into a string
                randomWord = randomWord.toString();
                wordDefinition = wordDefinition.toString();
                //End
                maxGuesses = Math.floor(2 + (randomWord.length));// Get the max guesses based on word length
                console.log(`Random Word: ${randomWord}`);
                console.log(`Definition: ${wordDefinition}`);
                    for (let i = 0; i < randomWord.length; i++) {
                        html += `<input type="text" disabled>`;
                    }
                    inputs.innerHTML = html;
                    moreInfo.innerHTML = `<p><span>${infos}</span>`
                    definition.innerText = wordDefinition;
                    guessLeft.innerText = maxGuesses;
                    wrongLetter.innerText = incorrects;
            }
        })
        .catch(error => {
            console.error(error.message)
            fetchRandomWordAndDefinition();
        });

    }
    function playSound() {
        sound.play();
    }

    // Start the process by fetching a random word and its definition
    fetchRandomWordAndDefinition();
    // Initialize the game
    function initGame(e) {
        let key = e.target.value;
        if (key.match(/^[a-zA-Z]+$/) && !incorrects.includes(` ${key}`) && !corrects.includes(key)) {
            if (randomWord.includes(key)) {
                for (let i = 0; i < randomWord.length; i++) {
                    if (randomWord[i] === key) {
                        corrects.push(key);
                        inputs.querySelectorAll('input')[i].value = key;
                    }
                }
            } else {
                maxGuesses--;
                incorrects.push(` ${key}`);
            }
            guessLeft.innerText = maxGuesses;
            wrongLetter.innerText = incorrects;
        }
        typingInput.value = '';
        setTimeout(() => {
            if (corrects.length === randomWord.length) {
                swal({
                    title: "Yay!",
                    text: "Congrats! You have found the word!",
                    icon: "success",
                    button: "Continue",
                });

            } else if (maxGuesses < 1) {
                swal({
                    title: "Game Over",
                    text: "You have no guesses remaining",
                    icon: "error",
                    button: "Try Again",
                });
                for (let i = 0; i < randomWord.length; i++) {
                    inputs.querySelectorAll('input')[i].value = randomWord[i];
                }
            }
        });
    }
    // Reset button
    resetBtn.addEventListener('click', fetchRandomWordAndDefinition);
    // Typing input
    typingInput.addEventListener('input', initGame);
    typingInput.addEventListener('click', () => typingInput.focus());
    document.addEventListener('keydown', () => typingInput.focus());

});