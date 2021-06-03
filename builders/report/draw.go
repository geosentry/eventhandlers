package report

import (
	"fmt"

	"github.com/signintech/gopdf"
)

func (report *Report) SetTextColor(color string) error {

	rgb, ok := ColorConfig[color]
	if !ok {
		return fmt.Errorf("invalid color option")
	}

	report.File.SetTextColor(rgb[0], rgb[1], rgb[2])
	return nil
}

func (report *Report) SetFont(font string, size int) error {
	err := report.File.SetFont(font, "", size)
	return err
}

func (report *Report) WriteLogo() {

	report.SetFont("montserrat-black", 28)
	report.MoveCursor(report.wscale(35), report.hscale(2))

	report.SetTextColor("green")
	report.File.Cell(&gopdf.Rect{W: 76, H: 0}, "terra")

	report.SetTextColor("brown")
	report.File.Cell(&gopdf.Rect{W: 91, H: 0}, "scope")

	report.SetTextColor("green")
	report.File.Cell(&gopdf.Rect{W: 0, H: 0}, ".")
}

func (report *Report) WriteLine() {

	report.File.SetLineWidth(2)
	//report.File.SetLineType("dotted")
	report.File.SetStrokeColor(103, 166, 23)

	// top line
	report.File.Line(report.wscale(10), report.hscale(8), report.wscale(90), report.hscale(8))

	// bottom line
	report.File.Line(report.wscale(10), report.hscale(92), report.wscale(90), report.hscale(92))
}

func (report *Report) hscale(perc float64) float64 {
	return (perc / 100) * report.height
}

func (report *Report) wscale(perc float64) float64 {
	return (perc / 100) * report.width
}

func (report *Report) WriteImage() {
	report.File.Image("./elements/assets/ndvifield.jpg", report.wscale(10), 90, &gopdf.Rect{W: report.wscale(60), H: report.hscale(30)})

}
