#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    int length = text.length();
    std::vector<char> letters(text.begin(), text.end());
    if (std::find(letters.begin(), letters.end(), value[0]) == letters.end()) {
        value = std::string(1, letters[0]);
    }
    return std::string(length, value[0]);
}
int main() {
    auto candidate = f;
    assert(candidate(("ldebgp o"), ("o")) == ("oooooooo"));
}
