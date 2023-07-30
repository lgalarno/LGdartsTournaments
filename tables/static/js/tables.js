/////////////////////////////////////////////////////////////
// DataTable
/////////////////////////////////////////////////////////////
$(function() {
    $('#games_table').DataTable({
        searching: false,
        order: [],
        pageLength: 25,
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ],
        processing: true,
        deferRender: true,
    }
    );
    $('#standings_table').DataTable({
        dom: 'lt',
        order: [],
        searching: false,
/*            order: [[-1, 'des']],*/

    }
    );
}
);
