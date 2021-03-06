<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInit2101aa85646e7c5d7aee5907769c7776
{
    public static $files = array (
        '538ca81a9a966a6716601ecf48f4eaef' => __DIR__ . '/..' . '/opis/closure/functions.php',
    );

    public static $prefixLengthsPsr4 = array (
        'O' => 
        array (
            'Opis\\Closure\\' => 13,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'Opis\\Closure\\' => 
        array (
            0 => __DIR__ . '/..' . '/opis/closure/src',
        ),
    );

    public static $classMap = array (
        'Composer\\InstalledVersions' => __DIR__ . '/..' . '/composer/InstalledVersions.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInit2101aa85646e7c5d7aee5907769c7776::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInit2101aa85646e7c5d7aee5907769c7776::$prefixDirsPsr4;
            $loader->classMap = ComposerStaticInit2101aa85646e7c5d7aee5907769c7776::$classMap;

        }, null, ClassLoader::class);
    }
}
