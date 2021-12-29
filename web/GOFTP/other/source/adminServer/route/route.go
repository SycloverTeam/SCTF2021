package route

import (
	. "adminServer/controller"

	"github.com/gin-gonic/gin"
)

func SetAdminRoute(app *gin.Engine) {
	api := app.Group("/api")

	users := api.Group("/user")
	users.GET("", GetUser)
	// users.POST("")
	users.PUT("", CreateUser)
	// users.DELETE("")
}
