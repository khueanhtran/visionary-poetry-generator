var synthesis = window.speechSynthesis;
var lang = 'en'
var utterance = new SpeechSynthesisUtterance("");

function sayIt(textID){
  var voices = synthesis.getVoices()

  console.log(voices)

  if ('speechSynthesis' in window) {
    utterance.voice = voices[109]
    utterance.rate = 0.8
    utterance.pitch = 1.2
    console.log(utterance.voice)
    utterance.text = document.getElementById(textID).innerText;
    synthesis.speak(utterance);
  } else {
    console.log('Text-to-speech not supported.');
  }
}

