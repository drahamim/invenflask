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

document.getElementById("inputform").addEventListener("keypress", function (event) {
  if (event.key === "Enter" && !event.target.matches(`input[type="submit"]`)) {
    event.preventDefault();
    emulateTab.from(event.target).toNextElement();
  }
}, {capture: true});