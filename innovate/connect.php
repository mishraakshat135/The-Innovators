<?php
	$email = $_POST['email'];
	$username = $_POST['username'];
	

	$conn = new mysqli('localhost','root','','innovate');
	if($conn->connect_error){
		die('Connecetion Failed : '.$conn->connect_error);
	}else{
		$stmt = $conn->prepare("insert into signup(email, username)
			vlaues(?,?)");
	$stmt->blind_param("ss",$email, $username);
	$stmt->execute();
	echo "signup successful";
	$stmt->close();
	$conn->close();
?>
	