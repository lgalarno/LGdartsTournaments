$(function() {

    /////////////////////////////////////////////////////////////
    // Set_ranks according to the scores
    /////////////////////////////////////////////////////////////

    function validateParticipants(totalNewForms) {
        let participantscheck = document.getElementById("participantscheck");
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

    /////////////////////////////////////////////////////////////
    // Set_ranks according to the scores
    /////////////////////////////////////////////////////////////

    function rankings(arr) {
      const sorted = [...arr].sort((a, b) => b - a);
      return arr.map((x) => sorted.indexOf(x) + 1);
    };

    function set_ranks(totalNewForms) {
        const scores = []
        for (let i = 0; i < totalNewForms; i++) {
            scores.push($("#id_form-" + i + "-score").val());
        }
        sorted_scores=rankings(scores);
        for (let i = 0; i < totalNewForms; i++) {
            $("#id_form-" + i + "-rank").val(sorted_scores[i]);
        }
      }
    /////////////////////////////////////////////////////////////
    // Submit button for the create game form
    /////////////////////////////////////////////////////////////
    $("#submitnewgame").click(function () {
        let totalNewForms = document.getElementById('id_form-TOTAL_FORMS').value;
        let gametypelement = document.getElementById("gametype");
        let gametype = gametypelement.getAttribute('gametype');
        if (
            gametype !== '501'
        ) {
            set_ranks(totalNewForms)
        }

        let v = validateParticipants(totalNewForms)
        if (
            v === true
        ) {
            return true;
        } else {
            return false;
        }
        });
/*

    /////////////////////////////////////////////////////////////
    // Create round-robin
    /////////////////////////////////////////////////////////////

    $("#btnNrounds").click(function (){
        let this_ = $(this)
        let ApiUrl = this_.attr("data-href")
        let nrounds = document.getElementById('number-rounds').value;
        console.log(ApiUrl)
        console.log(nrounds)
        if (ApiUrl){
             $.ajax({
                 url: ApiUrl + '?nrounds=' + nrounds,
                 method: "GET",
                 data: {},
                 dataType: "json",
                 contentType: false,
                 cache: false,
                 processData: false,
                 success: function (data){
                     console.log(data.games)
                     console.log(data.nrounds)
                    },
                 error: function (error){
                        console.log("error")
                        console.log(error)
                    }
            })
        }
        })
*/

});
