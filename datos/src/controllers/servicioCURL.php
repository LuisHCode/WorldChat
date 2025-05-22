<?php
namespace App\controllers;

class servicioCURL{
    private const URL = "http://webdatos/api";

    public function ejecutionCURL($endpoint, $method, $data = null){
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, self::URL . $endpoint);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        if ($data != null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }

        switch($method){
            case 'POST':
            case 'PUT':
            case 'PATCH':
            case 'DELETE':
                curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PATCH');
                break;
            default:
                curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'GET');
        }
        
        $response = curl_exec($ch);
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return ['resp' => $response, 'status' => $status];
    }
}