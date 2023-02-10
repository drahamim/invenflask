import { emulateTab } from "https://cdn.skypack.dev/emulate-tab@^1.2.1";

function formNotifyingListener(event) {
  event.preventDefault();
  const theFormNotification = event.target.nextElementSibling.querySelector(".a-form-notification");
  theFormNotification.stepUp();
  setTimeout(function (theFormNotification) {
    theFormNotification.stepDown();
  }, 1500, theFormNotification);
}
for (const aForm of document.querySelectorAll(`.a-form`)) {
  aForm.addEventListener("submit", formNotifyingListener);
}

// document.getElementById("the-vanilla-form").addEventListener("keypress", function (event) {
//   if (event.key === "Enter" && document.querySelector(`#override-enter:checked`) !== null && !event.target.matches(`input[type="submit"]`)) {
//     event.preventDefault();
//     const substituteEvent = new KeyboardEvent("keypress", {key: "Tab"});
//     event.target.dispatchEvent(substituteEvent);
//   }
// }, {capture: true});

document.getElementById("inputform").addEventListener("keypress", function (event) {
  if (event.key === "Enter" && document.querySelector(`#override-enter:checked`) !== null && !event.target.matches(`input[type="submit"]`)) {
    event.preventDefault();
    emulateTab.from(event.target).toNextElement();
  }
}, {capture: true});