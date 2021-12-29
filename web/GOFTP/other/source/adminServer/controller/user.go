package controller

import (
	"adminServer/model"
	"encoding/json"
	"strings"

	"github.com/gin-gonic/gin"
)

func GetUser(c *gin.Context) {
	email := c.Query("email")
	username := c.Query("username")
	password := c.Query("password")

	hasEmail := (email != "")
	hasUsername := (username != "")
	hasPassword := (password != "")

	hasValues := (hasEmail || hasUsername || hasPassword)
	if !hasValues {
		users := []model.User{}
		if err := model.DB.Find(&users).Error; err != nil {
			c.JSON(500, gin.H{
				"data":  false,
				"value": err.Error(),
			})
			return
		} else {
			c.JSON(200, gin.H{
				"data":  users,
				"value": "Successful",
			})
			return
		}
	}

	user := new(model.User)
	sql := model.DB
	if hasEmail {
		sql = sql.Where("email = ?", email)
	}

	if hasUsername {
		sql = sql.Where("username = ?", username)
	}

	if hasPassword {
		sql = sql.Where("password = ?", model.PassHash(password))
	}

	if err := sql.First(user).Error; err != nil {
		c.JSON(404, gin.H{
			"data":  false,
			"value": err.Error(),
		})
		return
	}

	c.JSON(200, gin.H{
		"data":  user,
		"value": "Successful",
	})
}

func CreateUser(c *gin.Context) {
	ct := c.Request.Header.Get("Content-Type")
	if !strings.Contains(ct, "application/json") {
		c.JSON(400, gin.H{
			"data":  false,
			"value": "Doesn't Use JSON",
		})
		return
	}

	data := make(map[string]string)
	bytes, _ := c.GetRawData()
	if err := json.Unmarshal(bytes, &data); err != nil {
		c.JSON(400, gin.H{
			"data":  false,
			"value": err.Error(),
		})
		return
	}

	email := data["email"]
	username := data["username"]
	password := data["password"]

	hasEmail := (email != "")
	hasUsername := (username != "")
	hasPassword := (password != "")

	hasAllValues := (hasEmail && hasUsername && hasPassword)
	if !hasAllValues {
		c.JSON(400, gin.H{
			"data":  false,
			"value": "No Values",
		})
		return
	}

	user := new(model.User)

	if err := model.DB.Select("email").Where("email = ?", email).First(user).Error; err == nil {
		c.JSON(409, gin.H{
			"data":  false,
			"value": "Email Already Exists",
		})
		return
	}

	user = &model.User{
		Email:    email,
		Username: username,
		Password: model.PassHash(password),
	}

	if err := model.DB.Create(user).Error; err != nil {
		c.JSON(500, gin.H{
			"data":  false,
			"value": "DB Error",
		})
		return
	}

	c.JSON(200, gin.H{
		"data":  true,
		"value": "Successful",
	})
}
