#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string pref) {
    if (text.find(pref) == 0) {
        size_t n = pref.length();
        size_t pos = text.find('.', n);
        if (pos != std::string::npos) {
            text = text.substr(pos + 1);
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("omeunhwpvr.dq"), ("omeunh")) == ("dq"));
}
