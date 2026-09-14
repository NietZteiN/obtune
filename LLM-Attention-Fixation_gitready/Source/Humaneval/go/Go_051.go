import (
    "regexp"
)

// RemoveVowels is a function that takes string and returns string without vowels.
// >>> RemoveVowels('')
// ''
// >>> RemoveVowels("abcdef\nghijklm")
// 'bcdf\nghjklm'
// >>> RemoveVowels('abcdef')
// 'bcdf'
// >>> RemoveVowels('aaaaa')
// ''
// >>> RemoveVowels('aaBAA')
// 'B'
// >>> RemoveVowels('zbcd')
// 'zbcd'
func RemoveVowels(text string) string {

    var re = regexp.MustCompile("[aeiouAEIOU]")
	text = re.ReplaceAllString(text, "")
	return text
}

func TestRemoveVowels(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("", RemoveVowels(""))
    assert.Equal("bcdf\nghjklm", RemoveVowels("abcdef\nghijklm"))
    assert.Equal("fdcb", RemoveVowels("fedcba"))
    assert.Equal("", RemoveVowels("eeeee"))
    assert.Equal("cB", RemoveVowels("acBAA"))
    assert.Equal("cB", RemoveVowels("EcBOO"))
    assert.Equal("ybcd", RemoveVowels("ybcd"))
}
