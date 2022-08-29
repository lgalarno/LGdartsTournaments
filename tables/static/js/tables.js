/////////////////////////////////////////////////////////////
// DataTable
/////////////////////////////////////////////////////////////
$(function() {
    $('#games_table').DataTable({
        searching: false,
        order: [],
        columnDefs: [
            { orderable: false,
                targets: -1 }
            ]
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
