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
    }
    );
    $('#scores_table').DataTable({
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
    $('#avg_tbl').DataTable({
        dom: 'lt',
        order: [],
        searching: false,
    }
    );
}
);
