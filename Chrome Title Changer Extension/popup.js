  let changeColor = document.getElementById('changeColor');

  chrome.storage.sync.get('color', function(data) {
    changeColor.setAttribute('value', data.color);
  });

  changeColor.onchange = function(element) {
    let color = element.target.value;
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.executeScript(
          tabs[0].id,
          {code: 'if(document.getElementsByTagName("head").length==0) {var headerForTitle = document.createElement("head"); document.body.before(headerForTitle); var ttl = document.createElement("title"); document.head.appendChild(ttl);} document.title = "' + color + '";'});

    });
window.close();
  };