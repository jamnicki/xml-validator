document.querySelectorAll(".drop-zone__input").forEach((inputElement) => {
    const dropZoneElement = inputElement.closest(".drop-zone");
  
    dropZoneElement.addEventListener("click", (e) => {
      inputElement.click();
    });
  
    inputElement.addEventListener("change", (e) => {
      if (inputElement.files.length) {
        for (let i = 0; i < inputElement.files.length; i++) {
          if (i == 15) {
            createFilesLeftThumbnail(dropZoneElement, inputElement.files.length-i)
            break;
          }
          updateThumbnail(dropZoneElement, inputElement.files[i]);
        }
      }
    });
  
    dropZoneElement.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZoneElement.classList.add("drop-zone--over");
    });
  
    ["dragleave", "dragend"].forEach((type) => {
      dropZoneElement.addEventListener(type, (e) => {
        dropZoneElement.classList.remove("drop-zone--over");
      });
    });
  
    dropZoneElement.addEventListener("drop", (e) => {
      e.preventDefault();
  
      if (e.dataTransfer.files.length) {
        inputElement.files = e.dataTransfer.files;
        for (let i = 0; i < inputElement.files.length; i++) {
          if (i == 15) {
            createFilesLeftThumbnail(dropZoneElement, inputElement.files.length-i)
            break;
          }
          updateThumbnail(dropZoneElement, e.dataTransfer.files[i]); 
        }
      }
  
      dropZoneElement.classList.remove("drop-zone--over");
    });
  });
  
  /**
   * Updates the thumbnail on a drop zone element.
   *
   * @param {HTMLElement} dropZoneElement
   * @param {File} file
   */
  function updateThumbnail(dropZoneElement, file) {
    let thumbnailsContainer = dropZoneElement.querySelector(".thumbnails-container");

    // First time - remove the prompt
    if (dropZoneElement.querySelector(".drop-zone__prompt")) {
      dropZoneElement.querySelector(".drop-zone__prompt").remove();
    }

    // First time - there is no thumbnail container element, so lets create it
    if (!thumbnailsContainer) {
      thumbnailsContainer = document.createElement("div");
      thumbnailsContainer.classList.add("thumbnails-container");
      dropZoneElement.appendChild(thumbnailsContainer);
    }
    
    thumbnailElement = document.createElement("div");
    thumbnailElement.classList.add("drop-zone__thumb");
    thumbnailsContainer.appendChild(thumbnailElement);
    thumbnailElement.style.backgroundImage = "url('/static/images/xml-file-format-symbol.svg')";
    thumbnailElement.dataset.label = file.name;
  }

  function createFilesLeftThumbnail(dropZoneElement, filesLeft) {
    let thumbnailsContainer = dropZoneElement.querySelector(".thumbnails-container");
    let thumbnailText = filesLeft.toString() + '+'

    thumbnailElement = document.createElement("div");
    thumbnailElement.classList.add("drop-zone__thumb");
    thumbnailElement.setAttribute("id", "files-left-thumb")
    thumbnailTextElement = document.createElement("a")
    thumbnailTextElement.setAttribute("id", "files-left-text")
    thumbnailTextElement.innerHTML = thumbnailText

    thumbnailElement.appendChild(thumbnailTextElement)
    thumbnailsContainer.appendChild(thumbnailElement);
  }
