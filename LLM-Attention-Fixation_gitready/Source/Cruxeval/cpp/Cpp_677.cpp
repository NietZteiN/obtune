#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long length) {
    length = length < 0 ? -length : length;
    std::string output = "";
    for (int idx = 0; idx < length; idx++) {
        if (text[idx % text.length()] != ' ') {
            output += text[idx % text.length()];
        } else {
            break;
        }
    }
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate(("I got 1 and 0."), (5)) == ("I"));
}
