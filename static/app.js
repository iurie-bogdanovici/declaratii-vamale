const upload_btn = document.getElementById("upload_btn")
const loading_btn = document.getElementById("loading_btn")
const cancel_btn = document.getElementById("cancel_btn")

const alert_wrapper = document.getElementById("alert_wrapper")

const download_btn = document.getElementById("dnld_btn")

const input = document.getElementById("file_input")
const file_input_label = document.getElementById("file_input_label")

function show_alert(message, alert) {
    alert_wrapper.innerHTML = `
    <div class="alert alert-${alert} alert-dismissible fade show" role="alert">
        <span>${message}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`
}

function enable_download_btn() {
    download_btn.classList.remove("invisible");
}

function change_upload_btn(btn_value) {
    upload_btn.innerText = btn_value;
}

function input_filename() {
    file_input_label.innerText = `${input.files[0].name}...`;
}

function download_file(fileUrl, fileName) {
    const a = document.createElement("a");
    a.href = fileUrl;
    a.setAttribute("download", fileName);
    a.click();
}

function upload(url) {
    if (!input.value) {
        show_alert("No file selected", "warning")
        return;
    }
    console.log("uploading")
    const data = new FormData();
    const request = new XMLHttpRequest();
    request.responseType = "json";
    alert_wrapper.innerHTML = '';
    input.disabled = true;
    upload_btn.classList.add("d-none");
    loading_btn.classList.remove("d-none");
    cancel_btn.classList.remove("d-none")

    //const file = input.files[0];

    for (let file of input.files) {
        data.append(file.name, file);
    }
    //change_upload_btn("Processing...");

    request.addEventListener("load", function(evt) {
        if (request.status == 200) {
            //change_upload_btn("Upload file");
            show_alert(`${request.response.message}`, "success")
            download_file("http://10.193.30.204:5000/export_csv", "declaratii_esb.csv")
        }
        else {
            show_alert("Error uploading the file", "danger")
        }
        reset();
    })

    request.addEventListener("error", function(evt) {
        reset();
        show_alert("Error uploading the file", "danger");
    })
    request.open("post", url);
    request.send(data);

    cancel_btn.addEventListener("click", function() {
        request.abort();
        reset();
    })
}


function reset() {
    input.value = null;
    input.disabled = false;
    cancel_btn.classList.add("d-none");
    loading_btn.classList.add("d-none");
    upload_btn.classList.remove("d-none");
    file_input_label.innerText = "Select file";
}
