package model

import (
	"io"
	"net/url"

	"github.com/dutchcoders/goftp"
)

type ftp struct {
	conn *goftp.FTP
}

var FTP ftp

func Open(addr string) (err error) {
	var u *url.URL

	if u, err = url.Parse(addr); err != nil {
		return
	}

	if FTP.conn, err = goftp.Connect(u.Host); err != nil {
		return
	}

	var pass string
	var hasPass bool
	if pass, hasPass = u.User.Password(); !hasPass {
		pass = ""
	}

	var user string
	if len(u.User.Username()) > 0 {
		user = u.User.Username()
	} else {
		user = "anonymous"
	}

	if err = FTP.conn.Login(user, pass); err != nil {
		return
	}

	return
}

func (FTP *ftp) Close() (err error) {
	return FTP.conn.Quit()
}

func (FTP *ftp) Upload(path string, r io.Reader) (err error) {
	return FTP.conn.Stor(path, r)
}
