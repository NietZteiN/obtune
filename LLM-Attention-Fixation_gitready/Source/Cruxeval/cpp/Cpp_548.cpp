#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if(!suffix.empty() && !text.empty() && text.substr(text.length() - suffix.length()) == suffix) {
        return text.substr(0, text.length() - suffix.length());
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("spider"), ("ed")) == ("spider"));
}
