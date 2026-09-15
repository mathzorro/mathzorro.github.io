var encryptedGeneratedURL = "null";
var buttonScore = -1;

if (localStorage.getItem("voteCountStored") == null) {
    voteCount = 0;
} else {
    voteCount = localStorage.getItem("voteCountStored")
}

averageVote = 11;
const averageVoteCountText = document.getElementById('averageVoteCount');

var voteCountStored = localStorage.getItem("voteCountStored")
const userVoteCountText = document.getElementById('userVoteCount');

// regenerate a new image when visiting site:
window.addEventListener("load", function() {
    document.getElementById("resultsscreen").style.display = "none";
    fetchNextImage();
    userVoteCountText.innerHTML = "You have voted " + voteCount + " times";
  });

const button1 = document.getElementById('button1');
button1.addEventListener("click", function(e) {
    showResultsScreen(1);
    //sendScore(1);
    setTimeout(fetchNextImage,2500);
    chartObject.destroy();
    voteCount++;
    localStorage.setItem("voteCountStored", voteCount);
});

const button2 = document.getElementById('button2');
button2.addEventListener("click", function(e) {
    showResultsScreen(2);
    //sendScore(2);
    setTimeout(fetchNextImage,2500);
    chartObject.destroy();
    voteCount++;
    localStorage.setItem("voteCountStored", voteCount);
});

const button3 = document.getElementById('button3');
button3.addEventListener("click", function(e) {
    showResultsScreen(3);
    //sendScore(3);
    setTimeout(fetchNextImage,2500);
    chartObject.destroy();
    voteCount++;
    localStorage.setItem("voteCountStored", voteCount);
});

const button4 = document.getElementById('button4');
button4.addEventListener("click", function(e) {
    showResultsScreen(4);
    //sendScore(4);
    setTimeout(fetchNextImage,2500);
    chartObject.destroy();
    voteCount++;
    localStorage.setItem("voteCountStored", voteCount);
});

const button5 = document.getElementById('button5');
button5.addEventListener("click", function(e) {
    showResultsScreen(5);
    //sendScore(5);
    setTimeout(fetchNextImage,2500);
    chartObject.destroy();
    voteCount++;
    localStorage.setItem("voteCountStored", voteCount);
});

function showVotingScreen() {
    document.getElementById("votingscreen").style.display = "block";
    document.getElementById("resultsscreen").style.display = "none";
}

function showResultsScreen(scorePressed) {
    document.getElementById("votingscreen").style.display = "none";
    document.getElementById("resultsscreen").style.display = "block";

    var scorePressed = scorePressed - 1;
    var buttons = ["1chart.webp", "2chart.webp", "3chart.webp", "4chart.webp", "5chart.webp"]
    document.getElementById("userrating").src = "Images/" + buttons[scorePressed];
}

function chooseRandomPicture() {
    var random_category = (Math.floor(Math.random() * 8) + 1); // rand(1,8)

    if(random_category == 1) {
        var image_type = "BezierCurves";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '15' + random_num;
    } else if (random_category == 2) {
        var image_type = "PatternedLines";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '12' + random_num;
    } else if (random_category == 3) {
        var image_type = "OverlappingDrops";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '16' + random_num;
    } else if (random_category == 4) {
        var image_type = "NestedSquares";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '13' + random_num;
    } else if (random_category == 5) {
        var image_type = "NeonSpirals";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '10' + random_num;
    } else if (random_category == 6) {
        var image_type = "GridOfSquares";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '11' + random_num;
    } else if (random_category == 7) {
        var image_type = "45DegreePaths";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '14' + random_num;
    } else if (random_category == 8) {
        var image_type = "KochCurves";
        var random_num = Math.floor(Math.random() * (1025 - 1001 + 1)) + 1001; // rand(1001,1025)
        var image_id = '17' + random_num;
    }

    return `GeneratedArt/${image_type}/${image_id}.webp`; 
}

function fetchNextImage() {
    showVotingScreen();
    var randomImage = chooseRandomPicture();
    document.getElementById("generatedart").src = randomImage;
    document.getElementById("generatedart").height = "500";
    document.getElementById("generatedart").width = "500";

    if(voteCount > 1) {
        userVoteCountText.innerHTML = "You have voted " + voteCount + " times";
    } else {
        userVoteCountText.innerHTML = "You have voted " + voteCount + " time";
    }

    if(voteCount >= 11 && voteCount < 20) {
        averageVoteCountText.innerHTML = "The top 10% of visitors vote over 20 times";
    } else if (voteCount >= 20) {
        averageVoteCountText.innerHTML = "You are in the top 10% of voters";
    }
}

// function sendScore(buttonScore) {
//     fetch('/db.php?i=' + encryptedGeneratedURL + '&score=' + buttonScore)
//     .then(response => response.json())
//     .then(data => {
//         values = [data.numOf1, data.numOf2, data.numOf3, data.numOf4, data.numOf5];
//         redrawAverageSmiley(calculateAverage(values));
//         redrawChart(values);
//         document.getElementById("numOfVotes").innerHTML = "Total Votes: " + countTotalVotes(values);
//     });
// }