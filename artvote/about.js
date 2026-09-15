function chooseRandomPicture(random_category) {
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

document.getElementById("aboutbeziercurves").src = chooseRandomPicture(1);
document.getElementById("aboutneonspirals").src = chooseRandomPicture(5);
document.getElementById("aboutnestedsquares").src = chooseRandomPicture(4);
document.getElementById("aboutkochcurves").src = chooseRandomPicture(8);
document.getElementById("about45degreepaths").src = chooseRandomPicture(7);
document.getElementById("aboutoverlappingdrops").src = chooseRandomPicture(3);
document.getElementById("aboutgridofsquares").src = chooseRandomPicture(6);
document.getElementById("aboutpatternedlines").src = chooseRandomPicture(2);