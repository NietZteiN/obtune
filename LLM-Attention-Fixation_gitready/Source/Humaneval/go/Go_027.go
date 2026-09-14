import (
    "strings"
)

// For a given string, flip lowercase characters to uppercase and uppercase to lowercase.
// >>> FlipCase('Hello')
// 'hELLO'
func FlipCase(str string) string {

    result := []rune{}
    for _, c := range str {
        if c >= 'A' && c <= 'Z' {
            result = append(result, 'a' + ((c - 'A' + 26) % 26))
        } else if c >= 'a' && c <= 'z' {
            result = append(result, 'A' + ((c - 'a' + 26) % 26))
        } else {
            result = append(result, c)
        }
    }
    return string(result)
}

func TestFlipCase(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("", FlipCase(""))
    assert.Equal("hELLO!", FlipCase("Hello!"))
    assert.Equal("tHESE VIOLENT DELIGHTS HAVE VIOLENT ENDS",FlipCase("These violent delights have violent ends"))
}
