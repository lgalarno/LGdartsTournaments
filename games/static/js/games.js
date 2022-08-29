$(function() {
    /////////////////////////////////////////////////////////////
    // DataTable
    /////////////////////////////////////////////////////////////
    $('#data_table').DataTable({
        searching: true,
        order: [],
    });

    let totalNewForms = document.getElementById('id_form-TOTAL_FORMS').value;
    let participantscheck = document.getElementById("participantscheck");

    function validateParticipants() {
        const darts_set = []
        for (let i = 0; i < totalNewForms; i++) {
            darts_set.push($("#id_form-" + i + "-darts").val())
        }
        let set_size = new Set(darts_set).size;
        if (darts_set.length !== set_size) {
            participantscheck.style.display = '';
            return false;
        } else {
            participantscheck.style.display = 'none';
            return true;
        }
      }

// Set_ranks according to the scores
    function rankings(arr) {
      const sorted = [...arr].sort((a, b) => b - a);
      return arr.map((x) => sorted.indexOf(x) + 1);
    };

    function set_ranks() {
        const scores = []
        for (let i = 0; i < totalNewForms; i++) {
            scores.push($("#id_form-" + i + "-score").val());
        }
        sorted_scores=rankings(scores);
        for (let i = 0; i < totalNewForms; i++) {
            $("#id_form-" + i + "-rank").val(sorted_scores[i]);
        }
      }

    // Submit button
    $("#submitbtn").click(function () {
        let gametypelement = document.getElementById("gametype");
        let gametype = gametypelement.getAttribute('gametype');
        if (
            gametype !== '501'
        ) {
            set_ranks()
        }

        let v = validateParticipants()
        if (
            v === true
        ) {
            return true;
        } else {
            return false;
        }
        });

});
