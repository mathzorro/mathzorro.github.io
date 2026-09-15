<?php
include('generateArtDirectory.php');

$encryptedGeneratedURL = $_GET['i'];
$score = $_GET['score'];

// ----------------------------Anticipating the received encryptedURL from JS:------------------------------------------
$decryptedURL = decryptImageURL($encryptedGeneratedURL, $encryption_key_256bit);

$explodedArray = explode("/", $decryptedURL);
$explodedimageid = $explodedArray[3];
$explodedArray2 = explode(".", $explodedimageid);
// ---------------------------------------------------------------------------------------------------------------------

// MySQL database connection info:
$servername = "localhost";
$username = "root";
$password = "GenArtRulez1!";
$dbname = "ArtVote";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Database Table:
$dbtable = "votes";

// Database Columns:
$imagetype = $explodedArray[2];
$imageid = strval($explodedArray2[0]); // allows for imageids starting with 0 (03211 would be valid)
$imageurl = $decryptedURL;
$rating = $score;
$ip = $_SERVER['REMOTE_ADDR'];
$unixtimestamp = time();

// prepare and bind
$stmt = $conn->prepare("INSERT INTO $dbtable (imagetype, imageid, imageurl, rating, ip, unixtimestamp) VALUES (?, ?, ?, ?, ?, ?)");
$stmt->bind_param("sssisi", $imagetype, $imageid, $imageurl, $rating, $ip, $unixtimestamp);
$stmt->execute();
$stmt->close();

// This command complexity via MySql's sorting internally is a B-tree with O(log n):
$stmt2 = $conn->prepare("SELECT
COUNT(IF(rating=1, 1, NULL)) 'numOf1',
COUNT(IF(rating=2, 1, NULL)) 'numOf2',
COUNT(IF(rating=3, 1, NULL)) 'numOf3',
COUNT(IF(rating=4, 1, NULL)) 'numOf4',
COUNT(IF(rating=5, 1, NULL)) 'numOf5' FROM votes WHERE imageurl='$imageurl';");
$stmt2->execute();
echo json_encode($stmt2->get_result()->fetch_assoc());
?>