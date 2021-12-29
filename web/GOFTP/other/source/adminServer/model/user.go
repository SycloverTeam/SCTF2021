package model

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
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
	tmp := md5.Sum([]byte(fmt.Sprintf("%s", pass)))
	hashPass = hex.EncodeToString(tmp[:])
	return
}
