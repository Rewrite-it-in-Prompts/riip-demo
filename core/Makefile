# Create gen-2.py from code in gen-1.py and specifications in gen-2-specs.txt
gen-2.py:
	python gen-1.py gen-1.py gen-2-specs.txt -o gen-2.py -n 3 -x "python gen-2-test.py"

# Rewrite gen-2.py in Golang
GO=gen-3/golang-local
g3-golang:
	python gen-2.py -l golang \
		llm_client.py gen-2-specs.txt gen-2.py $(GO)/golang-guide.md $(GO)/go.mod \
		-o $(GO) -n 3 -x "go build ./cmd/gen-3"
# -x "go test ./..."

g3-rust-container:
	python gen-3/rust-container/build.py
