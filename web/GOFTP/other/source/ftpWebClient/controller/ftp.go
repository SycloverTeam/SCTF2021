package controller

import (
	"mime/multipart"

	. "WebFTPClient/model"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func UploadPage(c *gin.Context) {
	session := sessions.Default(c)

	c.HTML(200, "upload.html", gin.H{
		"user": session.Get("username"),
	})
}

func Upload(c *gin.Context) {
	var err error
	var file multipart.File
	var postFile *multipart.FileHeader
	addr := c.PostForm("addr")

	if postFile, err = c.FormFile("file"); err != nil && addr != "" {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": err.Error(),
		})
		return
	}

	if err = Open(addr); err != nil {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": "Ftp Connect Error.",
		})
		return
	}
	defer FTP.Close()

	if file, err = postFile.Open(); err != nil {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": err.Error(),
		})
		return
	}

	if err = FTP.Upload(postFile.Filename, file); err != nil {
		c.JSON(200, gin.H{
			"value":   false,
			"massage": err.Error(),
		})
		return
	}

	c.JSON(200, gin.H{
		"value":   true,
		"massage": "Uploaded successfully",
	})
	return
}
