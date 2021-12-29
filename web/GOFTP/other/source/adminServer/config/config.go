package config

import (
	"encoding/json"
	"io/ioutil"
	"log"
)

type Config struct {
	App AppConfig 	`json:"AppConfig"`
	DB DBConfig 	`json:"DBConfig"`
}

type AppConfig struct {
	Host string
	Port string
}

type DBConfig struct {
	Username string
	Password string
	Address  string
	Database string
}

var WebAppConfig Config = GetAPPConfig()

func GetAPPConfig() Config {
	var (
		err      error
		config   Config
		jsonData []byte
	)

	if jsonData, err = ioutil.ReadFile("./config.json"); err != nil {
		log.Panicln(err.Error())
	}

	json.Unmarshal(jsonData, &config)
	return config
}
