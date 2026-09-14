package main

import (
    "fmt"
    "testing"
)

func f(text string, value string) string {
	newText := []rune(text)
	var length int

	defer func() {
		if r := recover(); r != nil {
			length = 0
		}
	}()

	newText = append(newText, []rune(value)...)
	length = len(newText)

	return "[" + fmt.Sprint(length) + "]"
}

func main() {
	text := "Hello"
	value := "World"
	result := f(text, value)
	fmt.Println(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abv", "a"), expected: "[4]" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
