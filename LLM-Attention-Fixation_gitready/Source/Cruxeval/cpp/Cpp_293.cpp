#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string s = text;
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);

    for (size_t i = 0; i < s.length(); ++i) {
        if (s[i] == 'x') {
            return "no";
        }
    }

    return std::all_of(text.begin(), text.end(), ::isupper) ? "1" : "0";
}
int main() {
    auto candidate = f;
    assert(candidate(("dEXE")) == ("no"));
}
