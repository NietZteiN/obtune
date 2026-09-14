import (
    "bytes"
)

// You are given a word. Your task is to find the closest vowel that stands between
// two consonants from the right side of the word (case sensitive).
// 
// Vowels in the beginning and ending doesn't count. Return empty string if you didn't
// find any vowel met the above condition.
// 
// You may assume that the given string contains English letter only.
// 
// Example:
// GetClosestVowel("yogurt") ==> "u"
// GetClosestVowel("FULL") ==> "U"
// GetClosestVowel("quick") ==> ""
// GetClosestVowel("ab") ==> ""
func GetClosestVowel(word string) string {

    if len(word) < 3 {
        return ""
    }

    vowels := []byte("aeiouAEOUI")
    for i := len(word)-2; i > 0; i-- {
        if bytes.Contains(vowels, []byte{word[i]}) {
            if !bytes.Contains(vowels, []byte{word[i+1]}) && !bytes.Contains(vowels, []byte{word[i-1]}) {
                return string(word[i])
            }
        }
    }
    return ""
}

func TestGetClosestVowel(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("u", GetClosestVowel("yogurt"))
    assert.Equal("u", GetClosestVowel("full"))
    assert.Equal("", GetClosestVowel("easy"))
    assert.Equal("", GetClosestVowel("eAsy"))
    assert.Equal("", GetClosestVowel("ali"))
    assert.Equal("a", GetClosestVowel("bad"))
    assert.Equal("o", GetClosestVowel("most"))
    assert.Equal("", GetClosestVowel("ab"))
    assert.Equal("", GetClosestVowel("ba"))
    assert.Equal("", GetClosestVowel("quick"))
    assert.Equal("i", GetClosestVowel("anime"))
    assert.Equal("", GetClosestVowel("Asia"))
    assert.Equal("o", GetClosestVowel("Above"))
}
