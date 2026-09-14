
// You are given a string s.
// Your task is to check if the string is happy or not.
// A string is happy if its length is at least 3 and every 3 consecutive letters are distinct
// For example:
// IsHappy(a) => false
// IsHappy(aa) => false
// IsHappy(abcd) => true
// IsHappy(aabb) => false
// IsHappy(adb) => true
// IsHappy(xyy) => false
func IsHappy(s string) bool {

    if len(s) < 3 {
        return false
    }
    for i := 0; i < len(s)-2; i++ {
        if s[i] == s[i+1] || s[i+1] == s[i+2] || s[i] == s[i+2] {
            return false
        }
    }
    return true
}

func TestIsHappy(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, IsHappy("a"), "a")
    assert.Equal(false, IsHappy("aa"), "aa")
    assert.Equal(true, IsHappy("abcd"), "abcd")
    assert.Equal(false, IsHappy("aabb"), "aabb")
    assert.Equal(true, IsHappy("adb"), "adb")
    assert.Equal(false, IsHappy("xyy"), "xyy")
    assert.Equal(true, IsHappy("iopaxpoi"), "iopaxpoi")
    assert.Equal(false, IsHappy("iopaxioi"), "iopaxioi")
}
