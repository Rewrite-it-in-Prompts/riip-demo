package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/bedrockruntime"
)

const (
	region = "us-west-2"
	modelHaiku  = "anthropic.claude-3-haiku-20240307-v1:0"
	modelSonnet = "anthropic.claude-3-5-sonnet-20241022-v2:0"
	modelOpus   = "anthropic.claude-3-opus-20240229-v1:0"
)

type msg struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type cfg struct {
	System   string `json:"system"`
	Messages []msg  `json:"messages"`
	MaxToks  int    `json:"max_tokens"`
	Temp     float64 `json:"temperature"`
	Version  string  `json:"anthropic_version"`
}

type usage struct {
	InToks  int `json:"input_tokens"`
	OutToks int `json:"output_tokens"`
}

type content struct {
	Text string `json:"text"`
}

type resp struct {
	Content []content `json:"content"`
	Usage   usage    `json:"usage"`
}

type chat struct {
	c *bedrockruntime.Client
	m string
	h []msg
}

func newChat(level int) (*chat, error) {
	ctx := context.Background()
	cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion(region))
	if err != nil {
		return nil, fmt.Errorf("config load: %w", err)
	}

	c := bedrockruntime.NewFromConfig(cfg)
	models := []string{modelHaiku, modelSonnet, modelOpus}
	if level < 0 || level >= len(models) {
		level = 0
	}

	return &chat{c: c, m: models[level], h: []msg{}}, nil
}

func (c *chat) invoke(ctx context.Context, up, ft, sp string) (string, int, int, error) {
	if sp == "" {
		sp = fmt.Sprintf(`You are an expert developer of %s files. You deliver complete solutions without placeholders. 
When fixing code, you repeat the entire file contents. Format each file as:
filename%s:
` + "```go" + `
// Generated by AI
// Change Log:
// v1.0 Initial version
// code here
` + "```" + `
`, ft, ft)
	}

	c.h = append(c.h, msg{Role: "user", Content: up})

	cfg := cfg{
		System:   sp,
		Messages: c.h,
		MaxToks:  8000,
		Temp:     0.5,
		Version:  "bedrock-2023-05-31",
	}

	body, err := json.Marshal(cfg)
	if err != nil {
		return "", 0, 0, fmt.Errorf("marshal: %w", err)
	}

	out, err := c.c.InvokeModel(ctx, &bedrockruntime.InvokeModelInput{
		ModelId: aws.String(c.m),
		Body:    body,
	})
	if err != nil {
		return "", 0, 0, fmt.Errorf("invoke: %w", err)
	}

	var r resp
	if err := json.NewDecoder(bytes.NewReader(out.Body)).Decode(&r); err != nil {
		return "", 0, 0, fmt.Errorf("decode: %w", err)
	}

	if len(r.Content) == 0 {
		return "", 0, 0, errors.New("no content")
	}

	txt := strings.TrimSpace(r.Content[0].Text)
	c.h = append(c.h, msg{Role: "assistant", Content: txt})

	return txt, r.Usage.InToks, r.Usage.OutToks, nil
}

type gen struct {
	ch      *chat
	outDir  string
	exec    string
	maxTry  int
	files   map[string]string
	fileRe  *regexp.Regexp
	startRe *regexp.Regexp
	endRe   *regexp.Regexp
}

func newGen(outDir, exec string, maxTry int) (*gen, error) {
	ch, err := newChat(0)
	if err != nil {
		return nil, err
	}

	fileRe := regexp.MustCompile(`(?m)^([^:]+\.[^:]+):[\s]*$`)
	startRe := regexp.MustCompile(`(?m)^` + "```" + `(?:go)?[\s]*$`)
	endRe := regexp.MustCompile(`(?m)^` + "```" + `[\s]*$`)

	return &gen{
		ch:      ch,
		outDir:  outDir,
		exec:    exec,
		maxTry:  maxTry,
		files:   make(map[string]string),
		fileRe:  fileRe,
		startRe: startRe,
		endRe:   endRe,
	}, nil
}

func (g *gen) parseFiles(txt string) error {
	g.files = make(map[string]string)
	lines := strings.Split(txt, "\n")
	var cur string
	var buf []string
	inCode := false

	log.Printf("Parsing response:\n%s", txt)

	for _, l := range lines {
		l = strings.TrimSpace(l)
		if l == "" {
			continue
		}

		if m := g.fileRe.FindStringSubmatch(l); len(m) > 1 {
			if cur != "" && len(buf) > 0 {
				content := strings.TrimSpace(strings.Join(buf, "\n"))
				g.files[cur] = content
				log.Printf("Added file %s (%d bytes)", cur, len(content))
			}
			cur = m[1]
			buf = nil
			continue
		}

		if g.startRe.MatchString(l) {
			inCode = true
			continue
		}

		if g.endRe.MatchString(l) {
			inCode = false
			continue
		}

		if inCode {
			buf = append(buf, l)
		}
	}

	if cur != "" && len(buf) > 0 {
		content := strings.TrimSpace(strings.Join(buf, "\n"))
		g.files[cur] = content
		log.Printf("Added file %s (%d bytes)", cur, len(content))
	}

	log.Printf("Found %d files", len(g.files))
	return nil
}

func (g *gen) writeFiles() error {
	if err := os.MkdirAll(g.outDir, 0755); err != nil {
		return err
	}

	for f, c := range g.files {
		p := filepath.Join(g.outDir, f)
		if err := os.WriteFile(p, []byte(c), 0644); err != nil {
			return err
		}
		log.Printf("wrote %s", p)
	}
	return nil
}

func (g *gen) exec_() (int, string, string, error) {
	parts := strings.Split(g.exec, " ")
	if len(parts) == 0 {
		return 0, "", "", errors.New("empty exec")
	}

	cmd := exec.Command(parts[0], parts[1:]...)
	cmd.Dir = g.outDir

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	rc := 0
	if err != nil {
		if ee, ok := err.(*exec.ExitError); ok {
			rc = ee.ExitCode()
		} else {
			return 0, "", "", err
		}
	}

	return rc, stdout.String(), stderr.String(), nil
}

func (g *gen) run(ctx context.Context, in io.Reader) error {
	b, err := io.ReadAll(in)
	if err != nil {
		return err
	}

	up := string(b)
	next := up
	try := 0

	for next != "" && try < g.maxTry {
		try++
		log.Printf("attempt %d/%d", try, g.maxTry)

		txt, _, _, err := g.ch.invoke(ctx, next, ".go", "")
		if err != nil {
			return err
		}

		if err := g.parseFiles(txt); err != nil {
			next = "Failed to parse output. Please format each file as 'filename.ext:' followed by code in ```go blocks."
			continue
		}

		if err := g.writeFiles(); err != nil {
			return err
		}

		if g.exec == "" {
			return nil
		}

		rc, stdout, stderr, err := g.exec_()
		if err != nil {
			return err
		}

		if rc == 0 {
			log.Printf("success!")
			return nil
		}

		log.Printf("exec failed: rc=%d\nstdout:\n%s\nstderr:\n%s", rc, stdout, stderr)
		next = fmt.Sprintf("Fix errors:\nrc=%d\nstdout:\n%s\nstderr:\n%s", rc, stdout, stderr)
	}

	if try >= g.maxTry {
		return fmt.Errorf("max retries (%d) reached", g.maxTry)
	}

	return nil
}

func test() error {
	g, err := newGen("", "", 0)
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()

	txt, _, _, err := g.ch.invoke(ctx, "Please generate a main.go file and a helper.go file for testing purposes. Format each file as filename.go: followed by code in ```go blocks.", ".go", "")
	if err != nil {
		return err
	}

	if err := g.parseFiles(txt); err != nil {
		return err
	}

	if len(g.files) != 2 {
		return fmt.Errorf("expected 2 files, got %d", len(g.files))
	}

	for f, c := range g.files {
		found := false
		lines := strings.Split(c, "\n")
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if strings.HasPrefix(line, "package") {
				found = true
				break
			}
		}
		if !found {
			return fmt.Errorf("file %s doesn't contain package declaration", f)
		}
	}

	return nil
}

func main() {
	var (
		outDir  string
		exec    string
		maxTry  int
		doTest  bool
		inFiles []string
	)

	flag.StringVar(&outDir, "o", "", "output directory")
	flag.StringVar(&exec, "x", "", "exec command")
	flag.IntVar(&maxTry, "n", 3, "max retries")
	flag.BoolVar(&doTest, "t", false, "test mode")
	flag.Parse()

	if doTest {
		if err := test(); err != nil {
			log.Fatal(err)
		}
		return
	}

	inFiles = flag.Args()
	if len(inFiles) == 0 {
		log.Fatal("no input files")
	}

	if outDir == "" {
		log.Fatal("no output directory (-o)")
	}

	g, err := newGen(outDir, exec, maxTry)
	if err != nil {
		log.Fatal(err)
	}

	ctx := context.Background()
	var in io.Reader
	if inFiles[0] == "-" {
		in = os.Stdin
	} else {
		f, err := os.Open(inFiles[0])
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()
		in = f
	}

	if err := g.run(ctx, in); err != nil {
		log.Fatal(err)
	}
}