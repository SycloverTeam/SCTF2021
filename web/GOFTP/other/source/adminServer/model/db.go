package model

import (
	"log"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

type GormModel gorm.Model

var DB *gorm.DB = nil

func Connect(dsn string) (err error) {
	if DB, err = gorm.Open(mysql.Open(dsn), &gorm.Config{}); err != nil {
		log.Fatalln(err.Error())
	}

	return
}

func Ping() (err error) {
	db, _ := DB.DB()
	return db.Ping()
}

func Close() (err error) {
	db, _ := DB.DB()
	return db.Close()
}
