const styleSheet = document.getElementById("theme");
const lightButton = document.getElementById("light-button");
const darkButton = document.getElementById("dark-button");
if (document.getElementById("AboutButton") !== null) {
    const aboutButton = document.getElementById("AboutButton");
}
if (document.getElementById("ResultsButton") !== null) {
    const resultsButton = document.getElementById("ResultsButton");
}
const responsiveCard = document.getElementById("responsive");
const aboutContainer = document.getElementById("aboutcontainer");
const artVoteLogo = document.getElementById("ArtVoteLogo");
const cunyLogo = document.getElementById("CUNYLogo");
const queensCollegeLogo = document.getElementById("QCLogo");
if (document.getElementById("AboutButton") !== null) {
    const storedaboutButton = localStorage.getItem("AboutButton");
}
if (document.getElementById("ResultsButton") !== null) {
    const storedresultsButton = localStorage.getItem("ResultsButton");
}
const storedTheme = localStorage.getItem("theme");
const storedArtVoteLogo = localStorage.getItem("artVoteLogo");
const storedQCLogo = localStorage.getItem("QCLogo");
const storedCUNYLogo = localStorage.getItem("CUNYLogo");
const storedResponsiveCard = localStorage.getItem("responsiveCard");
const storedAboutContainer = localStorage.getItem("aboutContainer");


if (storedTheme && (responsiveCard != null)) {
    styleSheet.href = storedTheme;
    artVoteLogo.src = storedArtVoteLogo;
    queensCollegeLogo.src = storedQCLogo;
    cunyLogo.src = storedCUNYLogo;
    responsiveCard.className = storedResponsiveCard;
    if (document.getElementById("AboutButton") !== null) {
        aboutButton.src = storedaboutButton;
    }
    if (document.getElementById("ResultsButton") !== null) {
        resultsButton.src = storedresultsButton;
    }
} else if(storedTheme && (responsiveCard == null)){
    styleSheet.href = storedTheme;
    artVoteLogo.src = storedArtVoteLogo;
    queensCollegeLogo.src = storedQCLogo;
    cunyLogo.src = storedCUNYLogo;
    aboutContainer.className = storedAboutContainer;
    if (document.getElementById("AboutButton") !== null) {
        aboutButton.src = storedaboutButton;
    }
    if (document.getElementById("ResultsButton") !== null) {
        resultsButton.src = storedresultsButton;
    }
}


if(artVoteLogo != null) {
    document.addEventListener("DOMContentLoaded", () => {
        lightButton.addEventListener("click", () => {
            enableLightMode();
            localStorage.setItem("theme", "lightmode.css");
            localStorage.setItem("artVoteLogo", "Images/ArtVoteLogoLight.webp");
            localStorage.setItem("QCLogo", "Images/QCLogo.webp");
            localStorage.setItem("CUNYLogo", "Images/CUNYLogo.webp");
            if(responsiveCard != null) {
                localStorage.setItem("responsiveCard", "border card bg-light mb-3");
            }
            localStorage.setItem("aboutContainer", "container card bg-light mb-3");
            if (document.getElementById("AboutButton") !== null) {
                localStorage.setItem("AboutButton", "Images/AboutLight.webp")
            }
            if (document.getElementById("ResultsButton") !== null) {
                localStorage.setItem("ResultsButton", "Images/ResultsLight.webp")
            }
        })

        darkButton.addEventListener("click", () => {
            enableDarkMode();
            localStorage.setItem("theme", "darkmode.css");
            localStorage.setItem("artVoteLogo", "Images/ArtVoteLogoDark.webp");
            localStorage.setItem("QCLogo", "Images/QCLogoDarkmode.webp");
            localStorage.setItem("CUNYLogo", "Images/CUNYLogoDarkmode.webp");
            if(responsiveCard != null) {
                localStorage.setItem("responsiveCard", "card bg-dark mb-3");
            }
            localStorage.setItem("aboutContainer", "container card bg-dark mb-3");
            if (document.getElementById("AboutButton") !== null) {
                localStorage.setItem("AboutButton", "Images/AboutDark.webp")
            }
            if (document.getElementById("ResultsButton") !== null) {
                localStorage.setItem("ResultsButton", "Images/ResultsDark.webp")
            }
        })
    })
}

function enableDarkMode() {
    styleSheet.href = "darkmode.css";
    artVoteLogo.src = "Images/ArtVoteLogoDark.webp";
    cunyLogo.src = "Images/CUNYLogoDarkmode.webp";
    queensCollegeLogo.src = "Images/QCLogoDarkmode.webp";
    if(responsiveCard != null) {
        responsiveCard.className -= ("border card bg-light mb-3");
        responsiveCard.className += ("card bg-dark mb-3");
    }
    aboutContainer.className -= ("container card bg-light mb-3");
    aboutContainer.className += ("container card bg-dark mb-3");

    if (document.getElementById("AboutButton") !== null) {
        aboutButton.src = "Images/AboutDark.webp";
    }
    if (document.getElementById("ResultsButton") !== null) {
        resultsButton.src = "Images/ResultsDark.webp";
    }
}

function enableLightMode() {
    styleSheet.href = "lightmode.css";
    artVoteLogo.src = "Images/ArtVoteLogoLight.webp";
    cunyLogo.src = "Images/CUNYLogo.webp";
    queensCollegeLogo.src = "Images/QCLogo.webp";
    if(responsiveCard != null) {
        responsiveCard.className -= ("card bg-dark mb-3");
        responsiveCard.className += ("border card bg-light mb-3");
    }
    aboutContainer.className -= ("container card bg-dark mb-3");
    aboutContainer.className += ("container card bg-light mb-3");

    if (document.getElementById("AboutButton") !== null) {
        aboutButton.src = "Images/AboutLight.webp";
    }
    if (document.getElementById("ResultsButton") !== null) {
        resultsButton.src = "Images/ResultsLight.webp";
    }
}