package model

import (
	"crypto/md5"
	"encoding/hex"
)

type User struct {
	ID       uint `gorm:"primaryKey"`
	Username string
	Password string
	Email    string
}

func (User) TableName() string {
	return "user"
}

func PassHash(pass string) (hashPass string) {
	tmp := md5.Sum([]byte(pass))
	hashPass = hex.EncodeToString(tmp[:])
	return
}
