if(!localStorage.getItem('readout'))
  localStorage.setItem('readout', 0);

document.querySelector('#counter').innerHTML = localStorage.getItem('readout')

function whyme() {  
  let readout = localStorage.getItem('readout')
  readout++
  document.querySelector('#counter').innerHTML = readout
  localStorage.setItem('readout', readout)
}
