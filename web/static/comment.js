function onButtonClick(id) {
  var comment = document.querySelectorAll("[id='comment']");
  var save = document.querySelectorAll("[id='save']");
  comment[id].className = "show";
  save[id].className = "show";
}