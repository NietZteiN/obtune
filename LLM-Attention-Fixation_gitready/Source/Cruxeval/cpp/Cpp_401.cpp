#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if (!suffix.empty() && text.substr(text.length() - suffix.length()) == suffix) {
        return text.substr(0, text.length() - suffix.length());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("mathematics"), ("example")) == ("mathematics"));
}
