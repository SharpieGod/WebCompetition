function deleteGrade(gradeId) {
    fetch("/delete-grade", {
        method: "POST",
        body: JSON.stringify({ gradeId: gradeId }),
    }).then((_res) => {
        location.reload(true);
    });
}
