<?php
   
    use Slim\Factory\AppFactory;

    use DI\Container;

    require __DIR__ . '/../../vendor/autoload.php';

    $container = new Container();

    AppFactory::SetContainer($container);
    
    $app = AppFactory::create();

    require "routes.php";
    

    $app->run();