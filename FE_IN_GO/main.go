package main

import (
	"fmt"
	"os"

	"github.com/akamensky/argparse"
)

type Arguments struct {
	shake_tree_flag *bool
	stdlib_flag     *string
	arch_flag       *string
	emit_ir_flag    *bool
	source_files    *string
}

func main() {
	args := Arguments{}
	parser := argparse.NewParser("pretty_printer", "pretty_printer")
	args.shake_tree_flag = parser.Flag("", "shake_tree", &argparse.Options{Help: "remove unreachable functions"})
	args.stdlib_flag = parser.String("", "stdlib", &argparse.Options{Help: "path to stdlib directory", Default: "./Lib"})
	args.arch_flag = parser.String("", "arch", &argparse.Options{Help: "architecture to generated IR for", Default: "x64"})
	args.emit_ir_flag = parser.Flag("", "emit_ir", &argparse.Options{Help: "stop at the given stage and emit ir"})
	args.source_files = parser.String("F", "files", &argparse.Options{Required: true, Help: "an input source file"})

	parse_err := parser.Parse(os.Args)
	if parse_err != nil {
		fmt.Print(parser.Usage(parse_err))
		os.Exit(1)
	}

	//Debug Print
	fmt.Println("shake tree flag:", *args.shake_tree_flag)
	fmt.Println("stdlib flag:", *args.stdlib_flag)
	fmt.Println("arch flag:", *args.arch_flag)
	fmt.Println("emit_ir flag:", *args.emit_ir_flag)
	fmt.Println("source files flag:", *args.source_files)
	//Debug End

}
