<?php
$container->set('config_bd',function(){
    return(object)[
        "host"=>"datbasesluis2024.database.windows.net",
        "db"=> "IF5100_WorldChat",
        "usr"=> "adminsql",
        "passw"=>"123SqlAdmin",
        "charset"=> "utf8mb4"

    ];
}
);