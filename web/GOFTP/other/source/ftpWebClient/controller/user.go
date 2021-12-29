package controller

import (
	. "WebFTPClient/model"
	"strings"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func LoginPage(c *gin.Context) {
	c.HTML(200, "login.html", gin.H{})
}

func RegisterPage(c *gin.Context) {
	c.HTML(200, "register.html", gin.H{})
}

func Login(c *gin.Context) {
	email := c.PostForm("email")
	password := c.PostForm("password")
	if len(email) == 0 || len(password) == 0 {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "No Values",
		})
		return
	}

	session := sessions.Default(c)
	if session.Get("username") != nil {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "You are already logged in.",
		})
		return
	}

	if data, auth := AuthUser(email, password); !auth {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "Wrong email or password",
		})
	} else {
		session.Set("username", data["Username"])
		session.Set("email", data["Email"])
		session.Save()
		c.JSON(200, gin.H{
			"value":   true,
			"massage": "Login Successful",
		})
	}
}

func Register(c *gin.Context) {
	email := c.PostForm("email")
	username := c.PostForm("username")
	password := c.PostForm("password")

	if len(email) == 0 || len(password) == 0 || len(username) == 0 {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "No Values",
		})
		return
	} else if len(username) > 10 {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "Username is too long",
		})
		return
	} else if strings.EqualFold(username, "admin") {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "Username cannot be 'admin'",
		})
		return
	}

	if mess, ok := CreateUser(email, username, password); ok {
		c.JSON(200, gin.H{
			"value":   true,
			"massage": "Registration Success",
		})
	} else {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": mess,
		})
	}
}

func Logout(c *gin.Context) {
	session := sessions.Default(c)
	if session.Get("username") == nil {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "You are not logged in",
		})
		return
	}

	session.Clear()
	session.Save()
	c.JSON(200, gin.H{
		"value":   true,
		"massage": "Sign out successfully",
	})
}
