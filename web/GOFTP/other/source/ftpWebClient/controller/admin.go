package controller

import (
	. "WebFTPClient/model"
	"io/ioutil"

	"github.com/gin-gonic/gin"
)

func AddAdminUser(c *gin.Context) {
	username := "admin"
	email := c.PostForm("email")
	password := c.PostForm("password")

	if len(email) == 0 || len(password) == 0 {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "No Values",
		})
		return
	}

	if mess, ok := CreateUser(email, username, password); ok {
		c.JSON(200, gin.H{
			"value":   true,
			"massage": "Create Admin Success",
		})
	} else {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": mess,
		})
	}
}

func ShowSecretPage(c *gin.Context) {
	flagBytes, _ := ioutil.ReadFile("/flag")
	flag := string(flagBytes[:])

	c.HTML(200, "flag.html", gin.H{
		"flag": flag,
	})
}
