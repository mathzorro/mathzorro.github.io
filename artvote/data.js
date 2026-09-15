const labels = ['User Feedback', 'User Feedback', 'User Feedback', 'User Feedback', 'User Feedback'];
const images = ['Images/1chart.webp', 'Images/2chart.webp', 'Images/3chart.webp', 'Images/4chart.webp', 'Images/5chart.webp'];

var chartObject = {destroy: ()=>{} };
function redrawChart(values) {
  chartObject = new Chart(document.getElementById("data"), {
    type: "bar",
    plugins: [{
      afterDraw: chart => {      
        var ctx = chart.chart.ctx; 
        var xAxis = chart.scales['x-axis-0'];
        var yAxis = chart.scales['y-axis-0'];
        xAxis.ticks.forEach((value, index) => {  
          var x = xAxis.getPixelForTick(index);      
          var image = new Image();
          image.src = images[index],
          ctx.drawImage(image, x - 12, yAxis.bottom + 10, 24, 24);
        });      
      }
    }],
    data: {
      labels: labels,
      datasets: [{
        label: 'Number of Ratings',
        data: values,
        backgroundColor: ['#E83535', '#F7974C', '#F7EC4C', '#C1F841', '#4CE262']
      }]
    },
    options: {
      responsive: false,
      tooltips: {enabled: false},
      hover: {mode: false},
      layout: {
        padding: {
          bottom: 30
        }
      },
      legend: {
        display: false
      },    
      scales: {
        yAxes: [{ 
          ticks: {
            beginAtZero: true
          }
        }],
        xAxes: [{
          ticks: {
            display: false
          }   
        }],
      }
    }
  });
}

function countTotalVotes(values) {
  var totalvotes = 0;
  for (i = 0; i < 5; i++) {
    totalvotes += values[i];
  }
  return totalvotes;
}

function calculateAverage(values) {
  var average = 0.0;

  for(i = 1; i <= 5; i++) {
    average += i * values[i-1];
  }
  average = average / countTotalVotes(values);
  return average;
}

function redrawAverageSmiley(average) {
  var buttons = ["1chart.webp", "2chart.webp", "3chart.webp", "4chart.webp", "5chart.webp"]
  if(average <= 1.8) {
    document.getElementById("averageSmiley").src = "Images/" + buttons[0];
  } else if(average <= 2.6) {
    document.getElementById("averageSmiley").src = "Images/" + buttons[1];
  } else if(average <= 3.4) {
    document.getElementById("averageSmiley").src = "Images/" + buttons[2];
  } else if(average <= 4.2) {
    document.getElementById("averageSmiley").src = "Images/" + buttons[3];
  } else if(average <= 5.0) {
    document.getElementById("averageSmiley").src = "Images/" + buttons[4];
  }
}