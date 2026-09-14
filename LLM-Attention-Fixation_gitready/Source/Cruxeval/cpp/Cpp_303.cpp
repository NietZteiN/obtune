#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int i = (text.length() + 1) / 2;
    std::vector<char> result(text.begin(), text.end());
    while (i < text.length()) {
        char t = std::tolower(result[i]);
        if (t == result[i]) {
            i += 1;
        } else {
            result[i] = t;
        }
        i += 2;
    }
    return std::string(result.begin(), result.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("mJkLbn")) == ("mJklbn"));
}
