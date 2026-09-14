import (
    "strings"
)

// Create a function that returns true if the last character
// of a given string is an alphabetical character and is not
// a part of a word, and false otherwise.
// Note: "word" is a group of characters separated by space.
// 
// Examples:
// CheckIfLastCharIsALetter("apple pie") ➞ false
// CheckIfLastCharIsALetter("apple pi e") ➞ true
// CheckIfLastCharIsALetter("apple pi e ") ➞ false
// CheckIfLastCharIsALetter("") ➞ false
func CheckIfLastCharIsALetter(txt string) bool {

    split := strings.Split(txt, " ")
    check := strings.ToLower(split[len(split)-1])
    if len(check) == 1 && 'a' <= check[0] && check[0] <= 'z' {
        return true
    }
    return false
}

func TestCheckIfLastCharIsALetter(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, CheckIfLastCharIsALetter("apple"))
    assert.Equal(true, CheckIfLastCharIsALetter("apple pi e"))
    assert.Equal(false, CheckIfLastCharIsALetter("eeeee"))
    assert.Equal(true, CheckIfLastCharIsALetter("A"))
    assert.Equal(false, CheckIfLastCharIsALetter("Pumpkin pie "))
    assert.Equal(false, CheckIfLastCharIsALetter("Pumpkin pie 1"))
    assert.Equal(false, CheckIfLastCharIsALetter(""))
    assert.Equal(false, CheckIfLastCharIsALetter("eeeee e "))
    assert.Equal(false, CheckIfLastCharIsALetter("apple pie"))
    assert.Equal(false, CheckIfLastCharIsALetter("apple pi e "))
}
