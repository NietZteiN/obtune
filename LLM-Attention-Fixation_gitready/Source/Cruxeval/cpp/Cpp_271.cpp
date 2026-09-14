#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string c) {
    std::vector<char> ls(text.begin(), text.end());
    if (text.find(c) == std::string::npos) {
        throw std::invalid_argument("Text has no " + c);
    }
    ls.erase(ls.begin() + text.rfind(c));
    return std::string(ls.begin(), ls.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("uufhl"), ("l")) == ("uufh"));
}
