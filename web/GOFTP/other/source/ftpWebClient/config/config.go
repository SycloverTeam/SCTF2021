package config

import (
	"encoding/json"
	"io/ioutil"
	"log"
)

type Config struct {
	App     WebConfig	  `json:"WebConfig"`
	Api     ApiConfig     `json:"ApiConfig"`
	Session SessionConfig `json:"SessionConfig"`
}

type WebConfig struct {
	Host string
	Port string
}

type ApiConfig struct {
	Addr string
}

type SessionConfig struct {
	Name   string
	Secret string
}

var AppConfig Config = GetAPPConfig()

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
