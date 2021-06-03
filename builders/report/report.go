package report

import (
	"fmt"
	"log"

	"github.com/signintech/gopdf"
)

type Report struct {
	File   *gopdf.GoPdf
	Path   string
	height float64
	width  float64
}

var FontConfig = map[string]string{
	"montserrat-regular": "builders/elements/fonts/MontserratAlternates-Regular.ttf",
	"montserrat-bold":    "builders/elements/fonts/MontserratAlternates-Bold.ttf",
	"montserrat-black":   "builders/elements/fonts/MontserratAlternates-Black.ttf",
}

var ColorConfig = map[string][3]uint8{
	"green": {103, 166, 23},
	"brown": {128, 68, 37},
}

func NewReport(name string) *Report {
	filepath := fmt.Sprintf("./tmp/reports/report-%s.pdf", name)

	file := gopdf.GoPdf{}
	size := *gopdf.PageSizeA4

	file.Start(gopdf.Config{PageSize: size})
	file.AddPage()

	for font, path := range FontConfig {
		err := file.AddTTFFont(font, path)
		if err != nil {
			log.Fatalf("failed to add font - %s. error - %v", font, err)
		}
	}

	pdf := Report{File: &file, Path: filepath, height: size.H, width: size.W}
	return &pdf
}

func (pdf *Report) MoveCursor(x, y float64) {
	pdf.File.SetX(x)
	pdf.File.SetY(y)
}

func (report *Report) Save() {
	report.File.WritePdf(report.Path)
}
