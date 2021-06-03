package main

import (
	report "github.com/manishmeganathan/terrascope/builders/report"
)

func main() {
	pdf := report.NewReport("test")

	pdf.WriteLogo()
	pdf.WriteLine()
	pdf.WriteImage()
	pdf.Save()
}
