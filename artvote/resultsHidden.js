function setupButtons(image_category) {
    var Quartile = document.getElementById(image_category + "_Quartile");
    var Top5 = document.getElementById(image_category + "_Top5");
    var Worst5 = document.getElementById(image_category + "_Worst5");
    var All = document.getElementById(image_category + "_All");

    var CardGroup_Quartile = document.getElementById(image_category + "_Cardgroup_Quartile");
    var CardGroup_Top5 = document.getElementById(image_category + "_Cardgroup_Top5");
    var CardGroup_Worst5 = document.getElementById(image_category + "_Cardgroup_Worst5");
    var CardGroup_All = document.getElementById(image_category + "_Cardgroup_All"); 

    Quartile.style.backgroundColor = "#008822";
    CardGroup_Quartile.style.display = "flex";

    Quartile.addEventListener("click", function(e) {
        resetColorAll(Quartile, Top5, Worst5, All);
        Quartile.style.backgroundColor = "#008822";
    
        resetDisplayAll(CardGroup_Quartile, CardGroup_Top5, CardGroup_Worst5, CardGroup_All, image_category);
        CardGroup_Quartile.style.display = "flex";
    });

    Top5.addEventListener("click", function(e) {
        resetColorAll(Quartile, Top5, Worst5, All);
        Top5.style.backgroundColor = "#008822";
        
        resetDisplayAll(CardGroup_Quartile, CardGroup_Top5, CardGroup_Worst5, CardGroup_All, image_category);
        CardGroup_Top5.style.display = "flex";
    });

    Worst5.addEventListener("click", function(e) {
        resetColorAll(Quartile, Top5, Worst5, All);
        Worst5.style.backgroundColor = "#008822";
    
        resetDisplayAll(CardGroup_Quartile, CardGroup_Top5, CardGroup_Worst5, CardGroup_All, image_category);
        CardGroup_Worst5.style.display = "flex";
    });

    All.addEventListener("click", function(e) {
        resetColorAll(Quartile, Top5, Worst5, All);
        All.style.backgroundColor = "#008822";
        
        resetDisplayAll(CardGroup_Quartile, CardGroup_Top5, CardGroup_Worst5, CardGroup_All, image_category);
        CardGroup_All.style.display = "flex";
        for (var i = 5; i <= 495; i+=5) {
            CardGroup_All_i = document.getElementById(image_category + "_Cardgroup_All-" + i);
            CardGroup_All_i.style.display = "flex";
        }
    });
}

function resetColorAll(Quartile, Top5, Worst5, All) {
    Quartile.style.backgroundColor = "#AA0056";
    Top5.style.backgroundColor = "#AA0056";
    Worst5.style.backgroundColor = "#AA0056";
    All.style.backgroundColor = "#AA0056";
    
    // if((document.getElementById("gridofsquares_all") !== null) && (document.getElementById("gridofsquares_cardgroup_all") !== null)) {
    //     gridofsquares_all.style.backgroundColor = "#AA0056";
    // }
}

function resetDisplayAll(CardGroup_Quartile, CardGroup_Top5, CardGroup_Worst5, CardGroup_All, image_category) {
    CardGroup_Quartile.style.display = "none";
    CardGroup_Top5.style.display = "none";
    CardGroup_Worst5.style.display = "none";
    CardGroup_All.style.display = "none";
    for (var i = 5; i <= 495; i+=5) {
        CardGroup_All_i = document.getElementById(image_category + "_Cardgroup_All-" + i);
        CardGroup_All_i.style.display = "none";
    }

    // if((document.getElementById("gridofsquares_all") !== null) && (document.getElementById("gridofsquares_cardgroup_all") !== null)) {
    //     gridofsquares_cardgroup_all.style.display = "none";

    //     for (let i = 5; i <= 495; i+=5) {
    //         gridofsquares_cardgroup_all_i = document.getElementById("gridofsquares_cardgroup_all-" + i);
    //         gridofsquares_cardgroup_all_i.style.display = "none";
    //     }
    // }
}

var imageCategories = ["BezierCurves", "NeonSpirals", "NestedSquares", "KochCurves", "DegreePaths", "OverlappingDrops", "GridOfSquares", "PatternedLines"];
for (var i = 0; i < imageCategories.length; i++) {
    setupButtons(imageCategories[i]);
}

var allImages = document.querySelectorAll('img');
for (var i = 0; i < allImages.length; i++) {
    allImages[i].ondragstart = () => {
        return false;
    };
}