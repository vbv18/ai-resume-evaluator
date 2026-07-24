const form = document.getElementById("resumeForm");
const result = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append(
        "resume",
        document.getElementById("resume").files[0]
    );
    formData.append(
        "job_description",
        document.getElementById("job_description").value
    );

    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/evaluate", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        result.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        result.textContent = err.message;
    }
});