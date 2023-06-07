function toggleCommentSection(id) {
  var commentSection = document.getElementById("commentSection" + id);
  var addCommentButton = document.querySelector("#commentSection" + id + " .add");
  
  // Toggle visibility by adding or removing the 'd-none' class
  commentSection.classList.toggle("d-none");
  addCommentButton.classList.add("d-none");
}
